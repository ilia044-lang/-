from pathlib import Path
import yfinance as yf,json,datetime as dt
P=Path(__file__).parent;S=P/'sources'
symbols=['STLD','NFLX','GM','TSLA','META','IBM','LRCX','PG','BE','AXP']
results=[]
for symbol in symbols:
 try:
  c=yf.Ticker(symbol).option_chain('2026-10-23');u=c.underlying;s=float(u['regularMarketPrice']);both=c.calls.merge(c.puts,on='strike',suffixes=('_call','_put'));near=both.iloc[(both.strike-s).abs().argsort()[:1]].iloc[0];k=float(near.strike)
  row={'symbol':symbol,'spot':s,'spot_time':u['regularMarketTime'],'expiry':'2026-10-23','strike':k,'fetched_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
  for side in ['call','put']:
   for field in ['contractSymbol','lastTradeDate','lastPrice','bid','ask','volume','openInterest']:
    val=near[field+'_'+side];row[side+'_'+field]=val.isoformat() if hasattr(val,'isoformat') else val.item() if hasattr(val,'item') else val
  total=float(near.lastPrice_call+near.lastPrice_put);row.update(straddle_last_total=total,proxy_pct=total/s*100,low=s-total,high=s+total)
  c.calls.to_csv(S/f'{symbol}_calls.csv',index=False);c.puts.to_csv(S/f'{symbol}_puts.csv',index=False);(S/f'{symbol}_underlying.json').write_text(json.dumps(u,indent=2));results.append(row);print(symbol,round(row['proxy_pct'],2),row['call_lastTradeDate'],row['put_lastTradeDate'],'bidask',row['call_bid'],row['call_ask'],flush=True)
 except Exception as e:results.append({'symbol':symbol,'error':str(e)});print('ERROR',symbol,str(e)[:120],flush=True)
(P/'options_review.json').write_text(json.dumps(results,indent=2))
