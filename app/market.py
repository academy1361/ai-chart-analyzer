import asyncio,httpx,pandas as pd
from .config import settings
TIMEFRAMES={"5m","15m","30m","1h","4h","1d"}
async def candles(symbol,interval,limit=300):
    symbol=symbol.upper().replace("/","")
    if interval not in TIMEFRAMES: raise ValueError("Unsupported timeframe")
    last=None
    for n in range(3):
        try:
            async with httpx.AsyncClient(timeout=15,headers={"User-Agent":"AI-Chart-Analyzer/1.0"}) as c:
                r=await c.get(settings.binance_base_url+"/api/v3/klines",params={"symbol":symbol,"interval":interval,"limit":min(limit,1000)})
                if r.status_code in (403,429,451) or r.status_code>=500:
                    last=RuntimeError(f"provider HTTP {r.status_code}"); await asyncio.sleep(.7*(n+1)); continue
                r.raise_for_status(); rows=r.json()
                cols=["time","open","high","low","close","volume","a","b","c","d","e","f"]
                df=pd.DataFrame(rows,columns=cols)[["time","open","high","low","close","volume"]]
                for col in ["open","high","low","close","volume"]: df[col]=pd.to_numeric(df[col],errors="coerce")
                return df.dropna(),"LIVE"
        except Exception as e: last=e; await asyncio.sleep(.7*(n+1))
    raise RuntimeError(f"Market data unavailable: {last}")
