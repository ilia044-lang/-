"""Deterministic broadcast graphics: fixed sourced values, animated explanation."""
import functools,json,math,subprocess,textwrap,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance,ImageFilter

GOLD='#e2bd69';WHITE='#f1eee7';GRAY='#b9bdc4';GREEN='#4caf50';RED='#f23645';CYAN='#24c5d9';BG='#101317'
ASSETS=Path(__file__).parent/'assets'
@functools.lru_cache(maxsize=70)
def font(size,bold=False):return ImageFont.truetype(str(ASSETS/('Inter-700.ttf' if bold else 'Inter-400.ttf')),size)
def text(im,xy,s,size=26,col=WHITE,bold=False,anchor=None):ImageDraw.Draw(im).text(xy,str(s),font=font(size,bold),fill=col,anchor=anchor)
def fit(s,width,size,bold=False):
    lines=[]
    for para in str(s).split('\n'):
        line=''
        for word in para.split():
            test=(line+' '+word).strip()
            if line and font(size,bold).getlength(test)>width:lines.append(line);line=word
            else:line=test
        if line:lines.append(line)
    return lines
def wrapped(im,s,x,y,width,size=26,col=WHITE,bold=False,maxlines=5):
    lines=fit(s,width,size,bold)
    if len(lines)>maxlines:
        if size>16:return wrapped(im,s,x,y,width,max(16,size-2),col,bold,maxlines)
        lines=lines[:maxlines];lines[-1]=lines[-1][:-2]+'…'
    for line in lines:text(im,(x,y),line,size,col,bold);y+=round(size*1.3)
    return y
def panel(im,rect,fill='#171d25',outline='#3a414b'):
    ImageDraw.Draw(im).rounded_rectangle(rect,radius=12,fill=fill,outline=outline,width=1)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)

@functools.lru_cache(maxsize=8)
def background(w,h,theme):
    im=Image.open(ASSETS/theme).convert('RGB');im=ImageOps.fit(im,(w+100,h+60))
    return ImageEnhance.Brightness(im).enhance(.64)

def orbit(im,t,cx,cy,size):
    """Perspective-projected wire globe; decor, not a market data series."""
    d=ImageDraw.Draw(im);theta=t*.11
    for lat in [-60,-30,0,30,60]:
        pts=[]
        for k in range(81):
            a=k/80*2*math.pi+theta;la=math.radians(lat);x=math.cos(la)*math.cos(a);y=math.sin(la);z=math.cos(la)*math.sin(a);p=2.9/(3.5-z)
            pts.append((cx+x*size*p,cy+y*size*p))
        d.line(pts,fill='#6b5b3a',width=1)
    for mer in range(0,180,30):
        pts=[]
        for k in range(81):
            a=k/80*2*math.pi;x=math.cos(a)*math.cos(math.radians(mer)+theta);z=math.cos(a)*math.sin(math.radians(mer)+theta);y=math.sin(a);p=2.9/(3.5-z);pts.append((cx+x*size*p,cy+y*size*p))
        d.line(pts,fill='#504936',width=1)

def bar3d(im,x,y,w,height,col):
    d=ImageDraw.Draw(im);depth=12
    top=y-height
    if height>=0:
        d.rectangle((x,top,x+w,y),fill=col);d.polygon([(x,top),(x+depth,top-depth),(x+w+depth,top-depth),(x+w,top)],fill='#d1b569' if col==GOLD else '#73a888');d.polygon([(x+w,top),(x+w+depth,top-depth),(x+w+depth,y-depth),(x+w,y)],fill='#3f514f')
    else:
        d.rectangle((x,y,x+w,top),fill=col);d.polygon([(x+w,y),(x+w+depth,y-depth),(x+w+depth,top-depth),(x+w,top)],fill='#66343c')

def chart(im,record,t,rect):
    x,y,w,h=rect;d=ImageDraw.Draw(im);panel(im,(x-14,y-38,x+w+72,y+h+20),'#0f0f0f')
    zoom=int(t/9)%2==1;history=record['history'][-18 if zoom else -60:]
    ph=h*.57;vy=y+ph+12;vh=h*.12;iy=vy+vh+16;ih=h*.17
    vals=[p['high'] for p in history]+[p['low'] for p in history]+[record['support'],record['resistance']]
    lo=min(vals);hi=max(vals);pad=(hi-lo)*.1 or 1;lo-=pad;hi+=pad
    px=lambda i:x+(i+.5)*w/len(history);py=lambda p:y+ph-(p-lo)/(hi-lo)*ph
    text(im,(x,y-31),record['symbol']+' · 1D',18,WHITE,True)
    text(im,(x+155,y-29),'Last candles' if zoom else 'Daily structure',14,GRAY)
    if w>800:text(im,(x+325,y-29),f'RSI 14 {record["rsi"]:.1f}  ·  ATR 14 {record["atr"]:.2f}',13,GRAY)
    text(im,(x+w,y-29),f'Week {record["weekly_pct"]:+.2f}%  |  Close {record["close"]:,.2f}',14,GOLD,anchor='rt')
    text(im,(x+w*.43,y+ph*.45),record['symbol']+', 1D',40,'#252830',True,anchor='mm')
    for k in range(5):
        price=lo+(hi-lo)*k/4;yy=py(price);d.line((x,yy,x+w,yy),fill='#24272f',width=1);text(im,(x+w+6,yy-9),f'{price:,.1f}',12,GRAY)
    for i,p in enumerate(history):
        xx=px(i);col=GREEN if p['close']>=p['open'] else RED;bw=max(2,w/len(history)*.29)
        d.line((xx,py(p['high']),xx,py(p['low'])),fill=col,width=2);a,b=sorted([py(p['open']),py(p['close'])]);d.rectangle((xx-bw,a,xx+bw,max(a+2,b)),fill=col)
    for k,(period,col) in enumerate([(20,CYAN),(50,GREEN),(150,RED),(200,GOLD)]):
        pts=[(px(i),py(p[f'ma{period}'])) for i,p in enumerate(history) if p.get(f'ma{period}') is not None and lo<=p[f'ma{period}']<=hi]
        if len(pts)>1:d.line(pts,fill=col,width=2)
        label=f'MA{period} {record["ma"][str(period)]:.2f}'
        if not lo<=record['ma'][str(period)]<=hi:label+=' (off scale)'
        text(im,(x+k*w/4,y+ph+1),label,11,col)
    for label,price,col in [('SUPPORT',record['support'],GREEN),('RESISTANCE',record['resistance'],RED)]:
        yy=py(price);length=w*ease(t/2);d.line((x,yy,x+length,yy),fill=col,width=2);text(im,(x+10,yy-18),label+f'  {price:,.2f}',12,col,True)
    close_y=py(record['close']);d.rounded_rectangle((x+w+1,close_y-8,x+w+65,close_y+9),radius=3,fill=GREEN if record['ohlc']['close']>=record['ohlc']['open'] else RED)
    text(im,(x+w+4,close_y-6),f'{record["close"]:.2f}',10,WHITE,True)
    pivots=[i for i in range(2,len(history)-2) if history[i]['low']==min(p['low'] for p in history[i-2:i+3])]
    if len(pivots)>=2:
        i,j=pivots[-2:]
        if history[j]['low']>history[i]['low']:
            d.line((px(i),py(history[i]['low']),px(j),py(history[j]['low'])),fill=CYAN,width=2)
    vmax=max(p['volume'] or 0 for p in history) or 1
    for i,p in enumerate(history):
        height=(p['volume'] or 0)/vmax*vh;xx=px(i);bw=max(2,w/len(history)*.3)
        d.rectangle((xx-bw,vy+vh-height,xx+bw,vy+vh),fill=GREEN if p['close']>=p['open'] else RED)
    text(im,(x,vy+1),'Vol',10,GRAY)
    cci=[p['cci'] or 0 for p in history];cci_limit=max(200,math.ceil(max(abs(v) for v in cci)/100)*100)
    cp=lambda value:iy+ih*(cci_limit-value)/(2*cci_limit)
    for value in [-100,0,100]:
        d.line((x,cp(value),x+w,cp(value)),fill='#34343e',width=1)
    d.line([(px(i),cp(value)) for i,value in enumerate(cci)],fill='#9b8afb',width=2)
    text(im,(x,iy),f'CCI 14  {record["cci"]:.1f}',10,'#bdb0ff')
    selected=min(len(history)-1,int((.5+.5*math.sin(t*.32))*(len(history)-1)));xx=px(selected)
    d.line((xx,y,xx,iy+ih),fill='#697079',width=1)
    for i in [0,len(history)//2,len(history)-1]:text(im,(px(i),y+h+5),history[i]['date'][5:],10,GRAY,anchor='mt')

def season(im,a,sym,t,rect):
    s=next(x for x in a['seasonality'] if x['symbol']==sym);x,y,w,h=rect;d=ImageDraw.Draw(im)
    panel(im,(x-14,y-10,x+w+14,y+h+40),'#121921');base=y+h*.55;limit=max(abs(p['return_pct']) for p in s['years']) or 1
    d.line((x,base,x+w,base),fill='#646b72',width=1)
    for i,p in enumerate(s['years']):
        xx=x+i*w/15;hh=p['return_pct']/limit*h*.37*ease((t-i*.055)/1.2);col=GREEN if p['return_pct']>=0 else RED
        bar3d(im,xx+4,base,w/15*.57,hh,col);text(im,(xx+w/30,y+h+12),str(p['year'])[2:],15,GRAY,anchor='mm')
    text(im,(x+12,y+10),f'{s["positive"]}/15 positive  |  Average {s["mean"]:+.2f}%',22,GOLD,True)

@functools.lru_cache(maxsize=8)
def article_image(path):return Image.open(path).convert('RGB')

def cover(a,number=0):
    """Branded publication covers; every label and statistic is drawn from data."""
    portrait=number>0;w,h=(1080,1920) if portrait else (1920,1080)
    base=ImageOps.fit(Image.open(ASSETS/('newsroom.png' if number!=2 else 'digital.png')).convert('RGB'),(w,h))
    im=ImageEnhance.Brightness(base).enhance(.86);d=ImageDraw.Draw(im)
    # A localized title panel preserves bright artwork instead of dimming it all.
    d.rounded_rectangle((45,55,w-45 if portrait else 1240,1040 if portrait else 685),radius=38,fill='#16202a',outline='#af955b',width=3)
    text(im,(80,90),'MARKET MIND',44 if portrait else 55,GOLD,True)
    if number==0:
        text(im,(85,195),'THE MARKET WEEK',100,WHITE,True)
        text(im,(85,345),"WHAT’S NEXT?",130,GOLD,True)
        text(im,(90,555),'REVIEW OCT 5–9  ·  OUTLOOK OCT 12–16',40,WHITE,True)
    elif number==1:
        wrapped(im,'Was October\nprofitable?',85,220,w-170,105,WHITE,True,3)
        text(im,(85,520),'15 YEARS OF SPY DATA',43,GOLD,True)
        s=a['seasonality'][0]
        text(im,(85,645),f'{s["positive"]}/15',150,GREEN,True)
        text(im,(90,835),'POSITIVE OCTOBERS',45,WHITE,True)
        text(im,(90,925),'2011–2025 · Past returns are not a forecast',25,GRAY)
    else:
        wrapped(im,'Next week:\n3 signals',85,220,w-170,110,WHITE,True,3)
        for k,label in enumerate(['PRICE','PARTICIPATION','VOLATILITY']):
            text(im,(90,570+k*120),f'0{k+1}',49,GOLD,True);text(im,(220,570+k*120),label,48,WHITE,True)
        text(im,(90,965),'OCTOBER 12–16, 2026',36,GOLD,True)
    cast=Image.open(ASSETS/'cover-cast.png').convert('RGBA')
    cast.thumbnail((850,455) if portrait else (640,580))
    im.paste(cast,((w-cast.width)//2,1048) if portrait else (1260,180),cast)
    if portrait:
        panel(im,(45,1510,w-45,1710),'#16202a','#af955b')
        text(im,(w/2,1542),'Full weekly review on YouTube',38,WHITE,True,'mt')
        text(im,(w/2,1615),'@MarketMindTradingBasics',34,GOLD,True,'mt')
        text(im,(w/2,1810),'Education only · Not financial advice',29,WHITE,anchor='mt')
        text(im,(w/2,1858),'I am not a licensed advisor',26,WHITE,anchor='mt')
    else:
        panel(im,(60,895,w-60,1015),'#16202a','#af955b')
        text(im,(95,930),'SPY  ·  QQQ  ·  RATES  ·  WATCHLIST',44,WHITE,True)
        text(im,(w-90,943),'Education only',29,GOLD,anchor='rt')
    return im

def frame(a,scene,t,portrait=False,sources=None):
    w,h=(720,1280) if portrait else (1280,720);xpan=round(48+40*math.sin(t*.085));ypan=round(25+22*math.sin(t*.06))
    theme='technology.png' if scene.get('symbol') in ['IREN','AVGO','QQQ'] else 'digital.png' if scene.get('symbol') in ['MSTR','CIFR'] or scene['kind']=='crossasset' else 'newsroom.png'
    im=background(w,h,theme).crop((xpan,ypan,xpan+w,ypan+h));d=ImageDraw.Draw(im)
    orbit(im,t,w*.82,h*.38,210 if portrait else 235)
    d.rectangle((0,0,w,58),fill='#101317');text(im,(28,16),'MARKET MIND',24,GOLD,True);text(im,(w-28,20),'WEEKLY BRIEFING',14,GRAY,anchor='rt')
    text(im,(32,81),scene['kicker'],16,GOLD,True)
    title_size=34 if portrait else 40
    display_title=scene['title'].title() if scene['title'].isupper() else scene['title']
    for ticker in ['SPY','QQQ','MSTR','IREN','AVGO','CIFR','VIX']:display_title=re.sub(r'\b'+ticker+r'\b',ticker,display_title,flags=re.I)
    title_y=wrapped(im,display_title,32,115,w-260 if portrait else w-340,title_size,WHITE,True,4 if scene['kind']=='news' else 3)
    kind=scene['kind'];m=a['markets'];content_y=max(title_y+28,240 if not portrait else 390)
    if kind=='outro':
        panel(im,(40,245,840,490),'#171d28','#3b4657')
        text(im,(70,273),'Your weekly market briefing',31,WHITE,True)
        d.rounded_rectangle((70,335,310,392),radius=24,fill='#ed334b')
        text(im,(190,350),'Subscribe',28,WHITE,True,'mt')
        text(im,(70,420),'@MarketMindTradingBasics',29,GOLD,True)
        text(im,(70,463),'Education only · Not a recommendation to buy or sell',17,GRAY)
    elif kind=='hero':
        text(im,(35,content_y+25),'WEEK IN REVIEW',24,GOLD,True)
        text(im,(35,content_y+74),'OCT 5–9, 2026',34,WHITE,True)
        text(im,(35,content_y+132),'NEXT WEEK',24,GOLD,True)
        text(im,(35,content_y+177),'OCT 12–16',34,WHITE,True)
        if not portrait:
            for k in range(8):bar3d(im,840+k*42,530,24,60+100*(.5+.5*math.sin(t*.25+k*.6)),GOLD)
    elif kind=='season':
        season(im,a,scene['symbol'],t,(40,content_y,w-92,360 if portrait else 230))
        s=next(x for x in a['seasonality'] if x['symbol']==scene['symbol'])
        wrapped(im,f'Best {s["best"]:+.2f}%  •  Worst {s["worst"]:+.2f}%\n2026 excluded • Past performance is not a forecast',40,content_y+(435 if portrait else 253),w-80,17,GRAY,maxlines=3)
    elif kind in ['chart','stock']:
        r=m[scene['symbol']]
        # Intercut chart detail and typographic information rather than holding one slide.
        if kind=='chart' or int(t/7)%2:
            chart(im,r,t,(52,content_y+12,w-155,330 if portrait else 250))
        else:
            wrapped(im,f'${r["close"]:,.2f}',40,content_y,w-80,67,GOLD,True,2)
            wrapped(im,f'{r["weekly_pct"]:+.2f}% this week',40,content_y+100,w-80,34,GREEN if r['weekly_pct']>=0 else RED,True,2)
            wrapped(im,f'SUPPORT  {r["support"]:,.2f}\nRESISTANCE  {r["resistance"]:,.2f}',40,content_y+170,w-80,27,WHITE,True,3)
            wrapped(im,'Scenarios, not predictions',40,content_y+245,w-80,22,GRAY,False,2)
    elif kind=='scoreboard':
        syms=scene['symbols'];limit=max(abs(m[s]['weekly_pct']) for s in syms)+.5
        for k,sym in enumerate(syms):
            r=m[sym];xx=45 if portrait else 50+k*405;yy=content_y+k*150 if portrait else content_y
            text(im,(xx,yy),sym.replace('^',''),30,GOLD,True);text(im,(xx,yy+45),f'{r["weekly_pct"]:+.2f}%',45,GREEN if r['weekly_pct']>=0 else RED,True)
            bw=round(abs(r['weekly_pct'])/limit*(500 if portrait else 340)*ease(t/1.4));d.rectangle((xx,yy+111,xx+bw,yy+129),fill=GREEN if r['weekly_pct']>=0 else RED)
    elif kind in ['rates','crossasset']:
        syms=scene['symbols'];data=[]
        for sym in syms:
            r=m[sym];v=f'{r["close"]:.3f}%' if kind=='rates' else f'{r["close"]:,.2f}';data.append((r['name'],v))
        if kind=='rates':
            treasury=a['supplemental'].get('treasury');data.insert(1,('US 20-year yield',f'{treasury["latest"]["20y"]:.3f}%' if treasury else 'Not verified'))
        for k,(label,value) in enumerate(data):
            xx=40 if portrait else 40+k*410;yy=content_y+k*165 if portrait else content_y+20
            wrapped(im,label,xx,yy,600 if portrait else 365,25,GRAY,False,2);text(im,(xx,yy+75),value,42,GOLD,True)
        if kind=='crossasset':wrapped(im,'Oil / FX: market feed • Bitcoin: timestamped snapshot',40,h-220,w-80,17,GRAY,maxlines=3)
        elif a['supplemental'].get('treasury'):text(im,(40,h-215),'Treasury official series: '+a['supplemental']['treasury']['latest']['date'],16,GRAY)
    elif kind=='breadth':
        b=a['supplemental'].get('breadth');v=m['^VIX'];value=b['value'] if b else None
        wrapped(im,f'{value:.2f}% above MA50' if value is not None else 'S5FI: final value not verified',40,content_y,w-80,38,GOLD,True,3)
        if value is not None:
            for k in range(100):
                col=GREEN if k<round(value) else '#434954';xx=45+(k%20)*27;yy=content_y+130+(k//20)*27;d.rounded_rectangle((xx,yy,xx+17,yy+17),radius=3,fill=col)
        text(im,(40 if portrait else 790,content_y+(340 if portrait else 80)),f'VIX {v["close"]:.2f}',36,WHITE,True)
    elif kind=='news':
        n=scene.get('news');photo=Path(sources)/n['image_file'] if sources and n and n.get('image_file') else None
        has_photo=photo and photo.exists() and not portrait;panel_width=625 if has_photo else w-32
        panel(im,(32,content_y-5,panel_width,content_y+190),'#141c25')
        wrapped(im,'REPORTED HEADLINE',55,content_y+16,panel_width-90,22,GOLD,True,1)
        wrapped(im,n['publisher'] if n else 'No verified current headline',55,content_y+70,panel_width-90,34,WHITE,True,2)
        wrapped(im,n['published'][:10] if n else 'See source notes',55,content_y+135,panel_width-90,21,GRAY,False,2)
        if has_photo:
            pw=560;ph=max(120,min(205,h-235-content_y));base=ImageOps.fit(article_image(str(photo)),(pw+30,ph+20));dx=round(15+12*math.sin(t*.12));dy=round(10+8*math.sin(t*.1));im.paste(base.crop((dx,dy,dx+pw,dy+ph)),(675,content_y))
            text(im,(675,content_y+ph+8),'Publisher article image • '+n['publisher'],14,GRAY)
        else:wrapped(im,'Reported headline • source links accompany this edition.',40,content_y+220,w-80,20,GRAY,maxlines=2)
    elif kind=='calendar':
        entries=scene.get('events') or scene.get('earnings') or []
        if not entries:wrapped(im,'Specific dates could not be verified.\nCheck the original calendar before the event.',40,content_y,w-80,32,WHITE,True,4)
        else:
            for k,e in enumerate(entries[:6]):
                yy=content_y+k*(100 if portrait else 48)
                text(im,(40,yy),'OCT '+e['date'][-2:],23,GOLD,True)
                label=e.get('event') or e.get('symbol','')+' • est.'
                wrapped(im,label,165,yy,w-200,24,WHITE,True,2)
    elif kind=='scenarios' and portrait and t<12:
        chart(im,m['SPY'],t,(50,content_y+20,w-145,390))
        text(im,(40,content_y+460),'Price · participation · volatility',25,GOLD,True)
    elif kind=='scenarios':
        entries=[('CONSTRUCTIVE',GREEN,'Support holds • Participation improves'),('RISK',RED,'Support breaks • Yields or volatility rise')]
        for k,(label,col,body) in enumerate(entries):
            yy=content_y+k*(220 if portrait else 145);text(im,(40,yy),label,28,col,True);wrapped(im,body,40,yy+50,w-100,30,WHITE,False,3)
            # Dashed moving scenario arrows are explicitly not price forecasts.
            xx=40+int(t*65)%max(100,w-200);d.line((xx,yy+111,xx+90,yy+111),fill=col,width=3)
    # Timed captions originate from individually synthesized speech units.
    caption=next((c['text'] for c in scene['captions'] if c['start']<=t<c['end']),'')
    ch=150 if portrait else 112;cy=h-ch-50
    d.rectangle((0,cy-8,w,h),fill='#101317')
    caption_size=28 if portrait else 27
    lines=fit(caption,w-116,caption_size)
    if caption:
        d.rounded_rectangle((24,cy-3,w-24,cy+20+len(lines)*35),radius=22,fill='#1c2330',outline='#354052',width=1)
    for k,line in enumerate(lines):
        xx=(w-font(caption_size).getlength(line))/2
        for token in line.split(' '):
            text(im,(xx,cy+12+k*35),token,caption_size,CYAN if any(c.isdigit() for c in token) else WHITE)
            xx+=font(caption_size).getlength(token+' ')
    if portrait and t>=scene['duration']-9:
        panel(im,(32,915,w-32,1042),'#192330','#52627a')
        text(im,(w/2,934),'Watch the full weekly review',25,WHITE,True,'mt')
        text(im,(w/2,972),'on our YouTube channel',23,WHITE,False,'mt')
        text(im,(w/2,1005),'@MarketMindTradingBasics',21,GOLD,True,'mt')
    footer='Not financial advice · Education only · I am not a licensed advisor'
    if portrait:
        text(im,(w/2,h-48),'Not financial advice · Education only',17,GRAY,anchor='mt');text(im,(w/2,h-26),'I am not a licensed advisor',16,GRAY,anchor='mt')
    else:text(im,(w/2,h-32),footer,16,GRAY,anchor='mt')
    d.rectangle((0,57,int(w*min(1,t/scene['duration'])),60),fill=GOLD)
    source='Source: Yahoo Finance • '+a['date']
    if kind=='season':source='Yahoo adjusted month-end data • 2011–2025'
    if kind=='news':source='Source: '+scene.get('news',{}).get('publisher','unavailable')+' • '+scene.get('news',{}).get('published','')[:10]
    if kind=='calendar':source=('Source: Yahoo economic calendar • schedule subject to change' if scene.get('events') else 'Source: Nasdaq earnings calendar • estimates labelled')
    text(im,(32,cy-32),source,14,GRAY)
    if not portrait:text(im,(w-30,cy-32),'AI-generated background illustration',13,GRAY,anchor='rt')
    # A short gold wipe makes scene changes visible without masking the narration.
    if t<.3:
        xx=round(w*(1-t/.3));d.rectangle((0,60,xx,h-50),fill='#171b21')
    if portrait and t>=scene['duration']-.75:
        # The final selectable frame doubles as the Shorts cover in mobile upload.
        im=cover(a,1 if scene['kind']=='season' else 2).resize((w,h))
    return im

def character_at(a,scene,t):
    """Illustrate the current spoken argument, never imply a price prediction."""
    caption=' '.join(c['text'] for c in scene['captions'] if c['start']<=t<c['end']).lower()
    if any(s in caption for s in ['youtube','weekly market review','education only','scenarios, not predictions']):return 'debate'
    if 'risk case' in caption or 'support breaking' in caption:return 'bear'
    if 'constructive case' in caption:return 'bull'
    if 'below all four moving averages' in caption:return 'bear'
    if 'above all four moving averages' in caption:return 'bull'
    if scene['kind']=='season':
        if any(s in caption for s in ['worst','negative','losing']):return 'bear'
        if any(s in caption for s in ['positive','average october']):return 'bull'
        return 'debate'
    if any(s in caption for s in ['below support','risk scenario','support breaks','structure is weakening','lower for the review']):return 'bear'
    if any(s in caption for s in ['above resistance','constructive scenario','higher for the review']):return 'bull'
    if scene['kind']=='scenarios':
        risk=next((c['start'] for c in scene['captions'] if 'risk scenario' in c['text'].lower()),None)
        if risk is not None:return 'bull' if t<risk else 'bear'
        return 'debate'
    if scene['kind'] in ['stock','scoreboard','chart']:
        change=a['markets'][scene.get('symbol','SPY')]['weekly_pct']
        return 'bull' if change>.15 else 'bear' if change<-.15 else 'debate'
    return 'debate'

def character_stream(kind,start):
    crop='crop=1120:720:80:0' if kind=='debate' else 'crop=760:720:440:0'
    size=(250,160) if kind=='debate' else (169,160)
    key='colorkey=0x0dcc43:0.24:0.08,' if kind!='debate' else ''
    filters=f'{key}{crop},scale={size[0]}:{size[1]},setpts=(PTS-STARTPTS)/0.90,fps=24,format=rgba'
    proc=subprocess.Popen(['ffmpeg','-v','error','-stream_loop','-1','-ss',str(start*.90%60),'-i',str(ASSETS/('user-'+kind+'.mp4')),'-an','-vf',filters,'-f','rawvideo','-pix_fmt','rgba','-threads','1','-'],stdout=subprocess.PIPE)
    return proc,size

def remove_debate_background(clip):
    # Remove only near-black pixels connected to the outer background;
    # preserve enclosed dark suit details rather than keying every black pixel.
    rgb=np.asarray(clip)[:,:,:3]
    dark=Image.fromarray(np.where(rgb.max(axis=2)<12,255,0).astype(np.uint8)).copy()
    for point in [(0,0),(clip.width-1,0),(0,clip.height-1),(clip.width-1,clip.height-1)]:
        if dark.getpixel(point)==255:ImageDraw.floodfill(dark,point,128)
    alpha=Image.fromarray(np.where(np.asarray(dark)==128,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.45))
    clip.putalpha(alpha)
    return clip

def render_piece(task):
    root,scene_index,start,end,portrait,index=task;root=Path(root);a=json.loads((root/'analysis.json').read_text());scenes=json.loads((root/'timing.json').read_text());scene=scenes[scene_index]
    w,h=(720,1280) if portrait else (1280,720);outw,outh=(1080,1920) if portrait else (1920,1080);fps=24
    dest=root/'chunks'/f'{index:04d}.mp4';dest.parent.mkdir(exist_ok=True)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-vf',f'scale={outw}:{outh}:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-threads','2',str(dest)],stdin=subprocess.PIPE)
    character=None;active=None
    try:
        for n in range(round((end-start)*fps)):
            t=start+n/fps;im=frame(a,scene,t,portrait,root.parent/'sources')
            if portrait and t>=scene['duration']-.75:
                p.stdin.write(im.tobytes());continue
            kind=character_at(a,scene,t)
            if kind!=active:
                if character:character.kill();character.wait();character.stdout.close()
                character,size=character_stream(kind,t);active=kind
            raw=character.stdout.read(size[0]*size[1]*4)
            assert len(raw)==size[0]*size[1]*4,'Character video decode ended unexpectedly'
            clip=Image.frombytes('RGBA',size,raw)
            if kind=='debate':clip=remove_debate_background(clip)
            if portrait:
                clip.thumbnail((205,150));im.paste(clip,(w-clip.width-24,205),clip)
            else:im.paste(clip,(w-size[0]-22,72),clip)
            p.stdin.write(im.tobytes())
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('FFmpeg encoding failed')
    except BaseException:
        p.kill();p.wait();raise
    finally:
        if character:character.kill();character.wait();character.stdout.close()
    return str(dest)
