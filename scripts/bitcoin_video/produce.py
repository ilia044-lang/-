#!/usr/bin/env python3
"""Bitcoin daily short: publication date is separate from the completed UTC bar."""
import sys,json,math,inspect,functools,datetime,os,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'weekly_video'))
import run as production,visuals as v
from visuals import text,wrapped,panel,font,GOLD,WHITE,GRAY,GREEN,RED,CYAN
ROOT=Path(os.environ.get('BITCOIN_OUTPUT','/tmp/bitcoin-daily-2026-10-11'))
OUT=ROOT/'Bitcoin_Daily_2026-10-11'
OUT.mkdir(parents=True,exist_ok=True)
A=json.loads((ROOT/'analysis.json').read_text());R=A['markets']['BTC-USD']
DATA_DAY=datetime.date.fromisoformat(A['date']).strftime('%b %d')
DATA_WORDS=datetime.date.fromisoformat(A['date']).strftime('%B')+' '+str(datetime.date.fromisoformat(A['date']).day)
RETRIEVED=A['retrieved_utc'][:16].replace('T',' ')
SNAPSHOT=A.get('snapshot')
RECENT_LOW=R.get('recent_low',min(x['low'] for x in R['history'][-3:]))
# Retain the audited chart implementation, with daily wording and a two-line header.
src=inspect.getsource(v.chart).replace('def chart(', 'def daily_chart(')
src=src.replace("text(im,(x+155,y-29),'Last candles' if zoom else 'Daily structure',14,GRAY)","text(im,(x,y-53),'LAST 18 CANDLES' if zoom else 'DAILY STRUCTURE',13,GRAY)")
src=src.replace("f'Week {record[\"weekly_pct\"]:+.2f}%  |  Close {record[\"close\"]:,.2f}'", "f'Day {record[\"daily_pct\"]:+.2f}%'" )
exec(src,v.__dict__)

def coin(im,cx,cy,size,t):
    d=ImageDraw.Draw(im);width=size*(.72+.22*math.sin(t*.8));depth=14
    for off in range(depth,0,-1):d.ellipse((cx-width+off,cy-size,cx+width+off,cy+size),fill='#7e4a18')
    d.ellipse((cx-width,cy-size,cx+width,cy+size),fill='#dbad46',outline='#ffe39a',width=4)
    d.ellipse((cx-width+12,cy-size+12,cx+width-12,cy+size-12),outline='#946121',width=3)
    text(im,(cx,cy),'B',int(size*1.23),'#fff0b2',True,'mm')
    d.line((cx-12,cy-size*.67,cx-12,cy+size*.67),fill='#fff0b2',width=3)
    d.line((cx+7,cy-size*.67,cx+7,cy+size*.67),fill='#fff0b2',width=3)

@functools.lru_cache(maxsize=1)
def make_cover():
    im=v.background(1080,1920,'digital.png').crop((40,20,1120,1940));d=ImageDraw.Draw(im)
    panel(im,(42,50,1038,1020),'#152332','#bda15e')
    text(im,(80,83),'MARKET MIND',44,GOLD,True)
    text(im,(80,175),'BITCOIN',112,WHITE,True)
    wrapped(im,('Above MA20.' if R['close']>R['ma']['20'] else 'Below MA20.')+'\nIBIT explained.',80,340,870,67,GOLD,True,3)
    text(im,(80,555),f'BTC {R["daily_pct"]:+.2f}%',78,GREEN,True)
    text(im,(80,662),'IBIT explained',53,WHITE,True)
    text(im,(80,760),'EDITION · OCT 11, 2026',35,GOLD,True)
    wrapped(im,f'Data: {DATA_DAY} UTC daily close\nEdition: Oct 11 · Snapshot labelled',80,832,865,29,GRAY,False,3)
    coin(im,540,1280,210,2)
    cast=Image.open(v.ASSETS/'cover-cast.png').convert('RGBA');cast.thumbnail((810,410));im.paste(cast,((1080-cast.width)//2,1350),cast)
    text(im,(540,1780),'@MarketMindTradingBasics',33,GOLD,True,'mt')
    text(im,(540,1842),'Education only · Not financial advice',26,WHITE,False,'mt')
    text(im,(540,1881),'I am not a licensed advisor',24,GRAY,False,'mt')
    return im

ROWS=[
 {'kind':'daily_hook','title':'Bitcoin: the daily map','kicker':f'OCT 11 EDITION · DATA: {DATA_DAY.upper()} UTC','actor':('bull' if R['daily_pct']>=0 else 'bear'),
  'voice':f'Bitcoin closed {abs(R["daily_pct"]):.2f} percent '+('higher' if R['daily_pct']>=0 else 'lower')+f'. This October eleventh edition analyzes the completed {DATA_WORDS} U T C candle. The current snapshot is shown separately.'},
 {'kind':'daily_chart','title':'The daily structure','kicker':'BITCOIN / USD · 1 DAY','actor':'debate',
  'voice':f'The completed close was {R["close"]:,.0f} dollars. The twenty day average is {R["ma"]["20"]:,.0f}, and the fifty day is {R["ma"]["50"]:,.0f}. All four averages are on screen.'},
 {'kind':'daily_candle','title':'The completed candle','kicker':'BODY · WICKS · MOMENTUM','actor':'debate',
  'voice':f'The candle closed {R["close_position_pct"]:.0f} percent up its range. R S I is {R["rsi"]:.0f}. Volume was {R["relative_volume"]:.2f} times its twenty day average.'},
 {'kind':'daily_scenarios','title':'Two levels to watch','kicker':'SCENARIOS, NOT PREDICTIONS','actor':'debate',
  'voice':f'The upside reference is resistance near {R["resistance"]:,.0f}. A break below the recent low near {RECENT_LOW:,.0f} would weaken the structure. Scenarios, not predictions.'},
 {'kind':'daily_ibit','title':'Bitcoin exposure\nthrough IBIT','kicker':'ISHARES BITCOIN TRUST ETF','actor':'debate',
  'voice':'I B I T is a spot Bitcoin E T F, offering exposure through a brokerage account. It seeks to track Bitcoin, but fees, tracking differences and exchange trading hours mean the match is not exact. Bitcoin trades all weekend; I B I T does not.'},
 {'kind':'daily_end','title':'Follow the daily chart','kicker':'MARKET MIND · TRADING BASICS','actor':'debate',
  'voice':'Subscribe to Market Mind Trading Basics. Education only. I am not a licensed advisor, and this is not a recommendation to take investment action.'}
]

def frame(a,s,t,portrait=True,sources=None):
    w,h=720,1280;kind=s['kind'];r=a['markets']['BTC-USD'];global_t=s['start']+t
    if kind=='daily_hook' and t<1.2:
        cover=make_cover();scale=1+.018*t;cover=cover.resize((int(720*scale),int(1280*scale)));im=cover.crop(((cover.width-w)//2,(cover.height-h)//2,(cover.width+w)//2,(cover.height+h)//2))
        return im
    if kind=='daily_end' and t>=s['duration']-.75:return make_cover().resize((w,h))
    xp=45;yp=25 # Stable scenery; actors and drawn explanations provide motion.
    im=v.background(w,h,'digital.png').crop((xp,yp,xp+w,yp+h));d=ImageDraw.Draw(im)
    v.orbit(im,global_t,550,600,240)
    d.rectangle((0,0,w,60),fill='#101722');text(im,(26,15),'MARKET MIND',25,GOLD,True);text(im,(w-25,22),'DAILY ANALYSIS',13,GRAY,anchor='rt')
    text(im,(30,82),s['kicker'],16,GOLD,True)
    wrapped(im,s['title'],30,119,655,38,WHITE,True,3)
    text(im,(30,280),'BTC · 1D',30,GOLD,True)
    text(im,(30,327),'Edition: 11 Oct 2026',18,GRAY)
    y=420
    if kind=='daily_hook':
        coin(im,350,590,135,t)
        text(im,(360,770),f'${r["close"]:,.2f}',63,WHITE,True,'mt')
        text(im,(360,852),f'{r["daily_pct"]:+.2f}% daily close',35,GREEN,True,'mt')
        text(im,(360,922),f'Snapshot: ${SNAPSHOT["price"]:,.0f}' if SNAPSHOT else 'Daily close, not a live quote',27,GOLD,True,'mt')
        
    elif kind=='daily_chart':
        v.daily_chart(im,r,t,(45,y,555,440))
        text(im,(36,930),f'RSI 14: {r["rsi"]:.1f}  |  ATR 14: ${r["atr"]:,.0f}',24,GOLD,True)
    elif kind=='daily_candle':
        panel(im,(30,405,690,984),'#131e2b')
        o=r['ohlc'];lo=o['low'];hi=o['high'];py=lambda p:810-(p-lo)/(hi-lo)*335
        x=220;d.line((x,py(hi),x,py(lo)),fill=GREEN,width=5)
        top,bottom=sorted([py(o['open']),py(o['close'])]);d.rectangle((x-42,top,x+42,bottom),fill=GREEN)
        for key in ['high','close','open','low']:
            yy=py(o[key]);d.line((x+48,yy,330,yy),fill=GRAY,width=1);text(im,(345,yy-12),f'{key[0].upper()}  {o[key]:,.2f}',24,WHITE,True)
        text(im,(60,858),f'Close position: {r["close_position_pct"]:.0f}% of range',24,GOLD,True)
        text(im,(60,908),f'Volume: {r["relative_volume"]:.2f}x 20-day average',23,GRAY)
    elif kind=='daily_scenarios':
        for i,(label,col,num,sub) in enumerate([('RESISTANCE REFERENCE',GREEN,r['resistance'],'Watch for acceptance above this level'),('BELOW RECENT LOW',RED,RECENT_LOW,'Recovery weakens; no guaranteed move')]):
            yy=430+i*270;panel(im,(30,yy-20,690,yy+215),'#131e2b')
            text(im,(55,yy),label,26,col,True);text(im,(55,yy+50),f'${num:,.0f}',57,WHITE,True)
            wrapped(im,sub,55,yy+138,580,23,GRAY,False,2)
            for j in range(8):
                xx=390+j*26;dy=(j*7 if i else -j*7);base=yy+110+dy+5*math.sin(t*2)
                d.line((xx,base,xx+14,base+(-5 if i==0 else 5)),fill=col,width=3)
    elif kind=='daily_ibit':
        phase=int(t/5)%3
        if phase==0:
            coin(im,160,560,83,t);text(im,(330,500),'IBIT',77,WHITE,True)
            text(im,(330,600),'Spot Bitcoin ETF',25,GOLD,True)
            for j in range(6):
                x=255+j*11;d.line((x,550,x+6,550),fill=CYAN,width=3)
            panel(im,(30,725,690,980),'#131e2b')
            wrapped(im,'Brokerage exposure\nNo direct coin ownership\nMarket price can differ from NAV',55,760,600,30,WHITE,True,4)
        elif phase==1:
            panel(im,(30,420,690,990),'#131e2b')
            text(im,(55,455),'Seeks to track Bitcoin',34,GOLD,True)
            for j,(title,detail) in enumerate([('Fees','Reduce returns over time'),('Tracking differences','ETF price may diverge from NAV'),('Exchange hours','Bitcoin continues trading outside them')]):
                yy=540+j*137;text(im,(55,yy),title,31,WHITE,True);wrapped(im,detail,55,yy+48,575,24,GRAY,False,2)
        else:
            for j,(title,col,detail) in enumerate([('BITCOIN',GOLD,'Trades 24 / 7'),('IBIT',CYAN,'Trades on exchange hours')]):
                yy=430+j*260;panel(im,(30,yy,690,yy+220),'#131e2b');text(im,(60,yy+28),title,48,col,True);text(im,(60,yy+116),detail,31,WHITE,True)
            text(im,(360,986),'Not an exact price-for-price match',23,GOLD,True,'mt')
    else:
        panel(im,(30,415,690,990),'#131e2b')
        text(im,(360,455),'DAILY CHART EDUCATION',28,GOLD,True,'mt')
        d.rounded_rectangle((140,535,580,625),radius=30,fill=RED);text(im,(360,555),'Subscribe',43,WHITE,True,'mt')
        text(im,(360,675),'@MarketMindTradingBasics',25,GOLD,True,'mt')
        wrapped(im,'Education only.\nNot a recommendation\nto buy or sell.',70,760,585,36,WHITE,True,4)
    d.rectangle((0,1060,w,h),fill='#101722')
    caption=next((c['text'] for c in s['captions'] if c['start']<=t<c['end']),'')
    size=26;lines=v.fit(caption,630,size)
    while len(lines)>4:size-=1;lines=v.fit(caption,630,size)
    if caption:
        d.rounded_rectangle((20,1080,700,1100+len(lines)*32),radius=18,fill='#1b2b3d',outline='#4d5969')
        for i,line in enumerate(lines):text(im,(360,1090+i*32),line,size,WHITE,False,'mt')
    text(im,(30,1017),f'Data: {DATA_DAY} UTC close · Edition: Oct 11',18,GRAY)
    text(im,(30,1040),('Snapshot: '+A['snapshot']['asof_utc'][5:16].replace('T',' ')+' UTC · Yahoo' if SNAPSHOT and kind=='daily_hook' else 'Yahoo Finance · IBIT product overview'),14,GRAY)
    text(im,(360,1231),'Not financial advice · Education only',17,GRAY,False,'mt')
    text(im,(360,1255),'I am not a licensed advisor',16,GRAY,False,'mt')
    d.rectangle((0,59,int(w*min(1,global_t/a.get('duration',90))),62),fill=GOLD)
    if kind=='daily_hook' and 1.2<=t<1.35:
        flash=Image.new('RGB',im.size,'white');im=Image.blend(im,flash,(1.35-t)/.15)
    return im

def actor(a,s,t):
    if s['kind']=='daily_scenarios':
        c=next((x['text'] for x in s['captions'] if x['start']<=t<x['end']),'')
        return 'bear' if 'below' in c.lower() or 'weaken' in c.lower() else 'bull'
    return s['actor']

def main():
    v.frame=frame;v.character_at=actor
    engine=production.engine(Path(os.environ.get('MODEL_CACHE',str(Path.home()/'.cache/stock-video'))))
    class SelectedVoice:
        def create(self,words,**kwargs):
            voice=os.environ.get('NARRATOR','am_adam');return engine.create(words,voice=voice,speed=1.0,lang='en-gb' if voice.startswith('b') else 'en-us')
    voice=SelectedVoice()
    production.editorial.caption_chunks=lambda sentence:re.split(r'(?<=[.!?])\s+(?=[A-Z])',sentence)
    duration=production.narration(ROWS,OUT,voice,1.09)
    A['duration']=duration;(ROOT/'analysis.json').write_text(json.dumps(A,indent=2))
    assert 40<duration<120,duration
    make_cover().save(ROOT/'Bitcoin_cover_2026-10-11.png')
    for i,s in enumerate(ROWS):frame(A,s,min(5,s['duration']/2),True).save(ROOT/f'preview-{i}.jpg')
    path,receipt=production.render(A,ROWS,OUT,True,2)
    receipt.update(narrator=os.environ.get('NARRATOR','am_adam'),publication_date=A['publication_date'],data_date=A['date'],data_basis=A['data_basis'],not_live=True)
    (ROOT/'validation.json').write_text(json.dumps(receipt,indent=2))
    print('READY',str(path),json.dumps(receipt),flush=True)
if __name__=='__main__':main()
