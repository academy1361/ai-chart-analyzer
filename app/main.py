import json
from pathlib import Path
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,EmailStr
from sqlalchemy.orm import Session
from .config import settings
from .database import Base,engine,get_db
from .models import User,Analysis,Backtest,Watchlist,WatchItem,Alert
from .security import hash_password,verify_password,token
from .market import candles
from .indicators import analyze
from .backtest import run as run_backtest
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
class Auth(BaseModel): email:EmailStr; password:str
class AnalyzeReq(BaseModel): symbol:str="BTCUSDT"; timeframe:str="15m"
class BacktestReq(BaseModel): symbol:str="BTCUSDT"; timeframe:str="15m"; initial_balance:float=10000
class WatchReq(BaseModel): name:str="Default"
class ItemReq(BaseModel): symbol:str; timeframe:str="15m"
class AlertReq(BaseModel): symbol:str; timeframe:str="15m"; condition:str="score_above"; threshold:float=60
@app.get("/api/health")
def health(): return {"success":True,"data":{"status":"ok","version":"2.0.0"},"error":None}
@app.post("/api/auth/register")
def register(x:Auth,db:Session=Depends(get_db)):
    if len(x.password)<8: raise HTTPException(422,"Password must be at least 8 characters")
    if db.query(User).filter(User.email==x.email).first(): raise HTTPException(400,"Email already registered")
    u=User(email=x.email,password_hash=hash_password(x.password));db.add(u);db.commit();db.refresh(u)
    return {"success":True,"data":{"access_token":token(u.id),"user_id":u.id},"error":None}
@app.post("/api/auth/login")
def login(x:Auth,db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==x.email).first()
    if not u or not verify_password(x.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
    return {"success":True,"data":{"access_token":token(u.id),"user_id":u.id},"error":None}
@app.post("/api/analyze")
async def api_analyze(x:AnalyzeReq,db:Session=Depends(get_db)):
    try: df,src=await candles(x.symbol,x.timeframe,300)
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception as e: raise HTTPException(503,str(e))
    if len(df)<210: raise HTTPException(422,"At least 210 candles required")
    r=analyze(df); l=r["levels"]; row=Analysis(symbol=x.symbol.upper(),timeframe=x.timeframe,signal=r["signal"],confluence_score=r["confluence_score"],entry=l["entry"],stop_loss=l["sl"],tp1=l["tp1"],tp2=l["tp2"],tp3=l["tp3"],data_source=src,data_quality=100,analysis_json=json.dumps(r));db.add(row);db.commit();db.refresh(row)
    return {"success":True,"data":{"id":row.id,"symbol":row.symbol,"timeframe":row.timeframe,"signal":row.signal,"confluence_score":row.confluence_score,"levels":l,"quality":{"score":row.data_quality,"source":src},"details":r},"error":None}
@app.post("/api/analyze/upload")
async def upload(file:UploadFile=File(...)):
    if file.content_type not in {"image/png","image/jpeg","image/webp"}: raise HTTPException(415,"PNG/JPEG/WEBP only")
    b=await file.read()
    if len(b)>12*1024*1024: raise HTTPException(413,"Image too large")
    return {"success":True,"data":{"filename":file.filename,"size":len(b),"vision_status":"validated"},"error":None}
@app.get("/api/history")
def history(db:Session=Depends(get_db)):
    rows=db.query(Analysis).order_by(Analysis.created_at.desc()).limit(200).all()
    return {"success":True,"data":[{"id":r.id,"symbol":r.symbol,"timeframe":r.timeframe,"signal":r.signal,"score":r.confluence_score,"entry":r.entry,"sl":r.stop_loss,"tp1":r.tp1,"tp2":r.tp2,"tp3":r.tp3,"source":r.data_source,"created_at":r.created_at.isoformat()} for r in rows],"error":None}
@app.post("/api/backtest/run")
async def backtest(x:BacktestReq,db:Session=Depends(get_db)):
    try: df,src=await candles(x.symbol,x.timeframe,1000)
    except Exception as e: raise HTTPException(503,str(e))
    result=run_backtest(df,x.initial_balance); row=Backtest(symbol=x.symbol.upper(),timeframe=x.timeframe,strategy="RSI-MACD-ICHIMOKU-EMA-PSAR",initial_balance=x.initial_balance,final_balance=result["final_balance"],total_trades=result["total_trades"],winning_trades=result["winning_trades"],losing_trades=result["losing_trades"],max_drawdown=result["max_drawdown"],result_json=json.dumps(result));db.add(row);db.commit();db.refresh(row)
    return {"success":True,"data":{"id":row.id,"data_source":src,**result},"error":None}
@app.get("/api/backtest/history")
def backtest_history(db:Session=Depends(get_db)):
    rows=db.query(Backtest).order_by(Backtest.created_at.desc()).limit(100).all()
    return {"success":True,"data":[{"id":r.id,"symbol":r.symbol,"timeframe":r.timeframe,"strategy":r.strategy,"final_balance":r.final_balance,"trades":r.total_trades,"win":r.winning_trades,"loss":r.losing_trades,"drawdown":r.max_drawdown} for r in rows],"error":None}
@app.get("/api/scanner/symbols")
def scanner_symbols(): return {"success":True,"data":["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT"],"error":None}
@app.post("/api/scanner/run")
async def scanner(x:AnalyzeReq):
    symbols=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT"];out=[]
    for s in symbols:
        try:
            df,src=await candles(s,x.timeframe,300)
            if len(df)>=210:
                r=analyze(df);out.append({"symbol":s,"timeframe":x.timeframe,"signal":r["signal"],"score":r["confluence_score"],"source":src,"rsi":r["indicators"]["rsi"]})
        except Exception as e: out.append({"symbol":s,"timeframe":x.timeframe,"signal":"ERROR","score":0,"source":"UNAVAILABLE","error":str(e)})
    return {"success":True,"data":{"results":out},"error":None}
@app.post("/api/watchlist")
def create_watch(x:WatchReq,db:Session=Depends(get_db)):
    w=Watchlist(name=x.name);db.add(w);db.commit();db.refresh(w);return {"success":True,"data":{"id":w.id,"name":w.name},"error":None}
@app.post("/api/watchlist/{wid}/items")
def add_item(wid:int,x:ItemReq,db:Session=Depends(get_db)):
    if not db.get(Watchlist,wid): raise HTTPException(404,"Watchlist not found")
    i=WatchItem(watchlist_id=wid,symbol=x.symbol.upper(),timeframe=x.timeframe);db.add(i);db.commit();db.refresh(i);return {"success":True,"data":{"id":i.id},"error":None}
@app.get("/api/watchlist")
def watchlists(db:Session=Depends(get_db)):
    ws=db.query(Watchlist).all();return {"success":True,"data":[{"id":w.id,"name":w.name,"items":[{"symbol":i.symbol,"timeframe":i.timeframe} for i in db.query(WatchItem).filter(WatchItem.watchlist_id==w.id).all()]} for w in ws],"error":None}
@app.post("/api/alerts")
def create_alert(x:AlertReq,db:Session=Depends(get_db)):
    a=Alert(symbol=x.symbol.upper(),timeframe=x.timeframe,condition=x.condition,threshold=x.threshold);db.add(a);db.commit();db.refresh(a);return {"success":True,"data":{"id":a.id,"symbol":a.symbol,"condition":a.condition,"threshold":a.threshold,"enabled":a.enabled},"error":None}
@app.get("/api/alerts")
def alerts(db:Session=Depends(get_db)):
    return {"success":True,"data":[{"id":a.id,"symbol":a.symbol,"timeframe":a.timeframe,"condition":a.condition,"threshold":a.threshold,"enabled":a.enabled} for a in db.query(Alert).order_by(Alert.id.desc()).all()],"error":None}
@app.get("/api/dashboard")
def dashboard(db:Session=Depends(get_db)):
    total=db.query(Analysis).count(); longs=db.query(Analysis).filter(Analysis.signal=="LONG").count(); shorts=db.query(Analysis).filter(Analysis.signal=="SHORT").count()
    return {"success":True,"data":{"analyses":total,"long":longs,"short":shorts,"neutral":total-longs-shorts},"error":None}
@app.get("/api/analytics")
def analytics(db:Session=Depends(get_db)):
    rows=db.query(Analysis).all(); avg=sum(r.confluence_score for r in rows)/len(rows) if rows else 0
    return {"success":True,"data":{"total":len(rows),"average_confluence":round(avg,2)},"error":None}
@app.get("/api/reports")
def reports(db:Session=Depends(get_db)):
    return {"success":True,"data":{"analysis_count":db.query(Analysis).count(),"backtest_count":db.query(Backtest).count(),"watchlists":db.query(Watchlist).count(),"alerts":db.query(Alert).count()},"error":None}
@app.get("/api/settings")
def settings_api(): return {"success":True,"data":{"timeframes":["5m","15m","30m","1h","4h","1d"],"educational_only":True,"real_orders":False},"error":None}
@app.get("/api/account")
def account(): return {"success":True,"data":{"authentication":"JWT","real_orders":False},"error":None}
frontend=Path(__file__).resolve().parent.parent/"frontend"
if frontend.exists(): app.mount("/",StaticFiles(directory=frontend,html=True),name="frontend")
