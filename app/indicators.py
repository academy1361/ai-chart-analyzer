import pandas as pd,numpy as np
def calculate(df):
    x=df.copy(); c=x.close; h=x.high; l=x.low
    x["ema20"]=c.ewm(span=20,adjust=False).mean(); x["ema50"]=c.ewm(span=50,adjust=False).mean(); x["ema200"]=c.ewm(span=200,adjust=False).mean()
    d=c.diff(); g=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); z=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); x["rsi"]=100-100/(1+g/z.replace(0,np.nan))
    f=c.ewm(span=12,adjust=False).mean(); s=c.ewm(span=26,adjust=False).mean(); x["macd"]=f-s; x["macd_signal"]=x.macd.ewm(span=9,adjust=False).mean()
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); x["atr"]=tr.ewm(alpha=1/14,adjust=False).mean()
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    x["tenkan"]=ten;x["kijun"]=kij;x["span_a"]=(ten+kij)/2;x["span_b"]=(h.rolling(52).max()+l.rolling(52).min())/2;x["psar"]=l.rolling(5).min()
    return x
def analyze(df):
    x=calculate(df).dropna()
    if x.empty: raise ValueError("Insufficient data")
    r=x.iloc[-1]
    st={"rsi":1 if r.rsi>=55 else -1 if r.rsi<=45 else 0,"macd":1 if r.macd>r.macd_signal else -1,"ema":1 if r.close>r.ema50 else -1,"ichimoku":1 if r.close>max(r.span_a,r.span_b) else -1 if r.close<min(r.span_a,r.span_b) else 0,"psar":1 if r.close>r.psar else -1,"structure":1 if r.close>r.ema20 else -1}
    w={"rsi":1,"macd":1.5,"ema":1.5,"ichimoku":1.5,"psar":1,"structure":1.5}; score=round(50+sum(st[k]*v for k,v in w.items())/sum(w.values())*50,1)
    sig="LONG" if score>=60 else "SHORT" if score<=40 else "NEUTRAL"; e=float(r.close); a=max(float(r.atr),e*.001)
    sl,tp1,tp2,tp3=(e-1.5*a,e+a,e+2*a,e+3*a) if sig!="SHORT" else (e+1.5*a,e-a,e-2*a,e-3*a)
    return {"signal":sig,"confluence_score":score,"levels":{"entry":e,"sl":sl,"tp1":tp1,"tp2":tp2,"tp3":tp3},"indicators":{"rsi":float(r.rsi),"macd":float(r.macd),"macd_signal":float(r.macd_signal),"ema20":float(r.ema20),"ema50":float(r.ema50),"ema200":float(r.ema200),"ichimoku":"BULLISH" if st["ichimoku"]==1 else "BEARISH" if st["ichimoku"]==-1 else "NEUTRAL","psar":float(r.psar),"atr":a},"states":st}
