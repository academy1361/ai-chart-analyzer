import numpy as np,pandas as pd
from app.indicators import calculate
def test_columns():
 n=300;c=np.linspace(100,150,n)+np.sin(np.arange(n));df=pd.DataFrame({"open":c,"high":c+1,"low":c-1,"close":c,"volume":1000})
 x=calculate(df)
 assert all(k in x for k in ["rsi","macd","atr","ema200","span_a","span_b"])
