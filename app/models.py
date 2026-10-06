from datetime import datetime,timezone
from sqlalchemy import Column,Integer,String,Float,DateTime,Text,Boolean,ForeignKey
from .database import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"; id=Column(Integer,primary_key=True); email=Column(String(320),unique=True,index=True,nullable=False); password_hash=Column(String(255),nullable=False); is_active=Column(Boolean,default=True); created_at=Column(DateTime,default=now)
class Analysis(Base):
    __tablename__="analyses"; id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey("users.id"),nullable=True,index=True); symbol=Column(String(30),index=True); timeframe=Column(String(10),index=True); signal=Column(String(20)); confluence_score=Column(Float); entry=Column(Float); stop_loss=Column(Float); tp1=Column(Float); tp2=Column(Float); tp3=Column(Float); data_source=Column(String(30)); data_quality=Column(Float); analysis_json=Column(Text); created_at=Column(DateTime,default=now,index=True)
class Backtest(Base):
    __tablename__="backtests"; id=Column(Integer,primary_key=True); user_id=Column(Integer,nullable=True,index=True); symbol=Column(String(30)); timeframe=Column(String(10)); strategy=Column(String(50)); start_date=Column(String(30)); end_date=Column(String(30)); initial_balance=Column(Float); final_balance=Column(Float); total_trades=Column(Integer); winning_trades=Column(Integer); losing_trades=Column(Integer); max_drawdown=Column(Float); result_json=Column(Text); created_at=Column(DateTime,default=now)
class Watchlist(Base):
    __tablename__="watchlists"; id=Column(Integer,primary_key=True); name=Column(String(100)); created_at=Column(DateTime,default=now)
class WatchItem(Base):
    __tablename__="watch_items"; id=Column(Integer,primary_key=True); watchlist_id=Column(Integer,ForeignKey("watchlists.id")); symbol=Column(String(30)); timeframe=Column(String(10)); created_at=Column(DateTime,default=now)
class Alert(Base):
    __tablename__="alerts"; id=Column(Integer,primary_key=True); symbol=Column(String(30)); timeframe=Column(String(10)); condition=Column(String(50)); threshold=Column(Float,nullable=True); enabled=Column(Boolean,default=True); created_at=Column(DateTime,default=now)
