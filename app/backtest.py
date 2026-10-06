from .indicators import analyze
def run(df,initial=10000,fee=.001):
    balance=initial; trades=[]; equity=[balance]
    # Educational causal simulation: signal on candle i, entry at i+1 open.
    for i in range(210,len(df)-1):
        try: r=analyze(df.iloc[:i+1])
        except: continue
        if r["signal"]=="NEUTRAL": continue
        entry=float(df.iloc[i+1].open); sl=r["levels"]["sl"]; tp=r["levels"]["tp1"] if r["signal"]=="LONG" else r["levels"]["tp1"]
        if r["signal"]=="LONG": ret=(tp-entry)/entry if float(df.iloc[i+1].high)>=tp else (sl-entry)/entry if float(df.iloc[i+1].low)<=sl else 0
        else: ret=(entry-tp)/entry if float(df.iloc[i+1].low)<=tp else (entry-sl)/entry if float(df.iloc[i+1].high)>=sl else 0
        pnl=balance*.10*ret-balance*.10*fee; balance+=pnl; trades.append(pnl); equity.append(balance)
    wins=sum(x>0 for x in trades); dd=max((max(equity[:i+1])-equity[i])/max(equity[:i+1])*100 for i in range(len(equity))) if equity else 0
    return {"initial_balance":initial,"final_balance":balance,"total_trades":len(trades),"winning_trades":wins,"losing_trades":len(trades)-wins,"max_drawdown":dd,"trades":trades}
