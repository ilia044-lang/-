from pathlib import Path
import json,datetime as dt,concurrent.futures,urllib.request
from zoneinfo import ZoneInfo
P=Path(__file__).parent;S=P/'sources';S.mkdir(exist_ok=True)
def get(day):
 d=dt.datetime(2026,10,day,tzinfo=ZoneInfo('America/New_York'));a=int(d.timestamp()*1000);u=f'https://query1.finance.yahoo.com/ws/screeners/v1/finance/calendar-events?countPerDay=100&modules=earnings&startDate={a}&endDate={a+86400000-1}&lang=en-US&region=US';b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read();(S/f'earnings_{day}.json').write_bytes(b);data=json.loads(b)['finance']['result']['earnings'];records=[r for bucket in data for r in bucket['records']];return day,[(r['ticker'],r['companyShortName'],r['startDateTimeType'],r.get('dateIsEstimate')) for r in records[:18]]
with concurrent.futures.ThreadPoolExecutor(5) as pool:
 for x in pool.map(get,range(19,24)):print(x)
