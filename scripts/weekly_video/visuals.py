"""Deterministic broadcast graphics: fixed sourced values, animated explanation."""
import functools,json,math,subprocess,textwrap
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance

GOLD='#e2bd69';WHITE='#f1eee7';GRAY='#b9bdc4';GREEN='#4caf50';RED='#f23645';CYAN='#24c5d9';BG='#101317'
ASSETS=Path(__file__).parent/'assets'
@functools.lru_cache(maxsize=70)
def font(size,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)
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

@functools.lru_cache(maxsize=3)
def background(w,h):
    im=Image.open(ASSETS/'newsroom.png').convert('RGB');im=ImageOps.fit(im,(w+100,h+60))
    return ImageEnhance.Brightness(im).enhance(.34)

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
    x,y,w,h=rect;d=ImageDraw.Draw(im);panel(im,(x-12,y-14,x+w+68,y+h+42),'#101317')
    history=record['history'][-42:];vals=[p['high'] for p in history]+[p['low'] for p in history]+[record['support'],record['resistance']]
    lo=min(vals);hi=max(vals);pad=(hi-lo)*.1 or 1;lo-=pad;hi+=pad
    px=lambda i:x+(i+.5)*w/len(history);py=lambda p:y+h-(p-lo)/(hi-lo)*h
    for k in range(5):
        price=lo+(hi-lo)*k/4;yy=py(price);d.line((x,yy,x+w,yy),fill='#29313b',width=1);text(im,(x+w+6,yy-9),f'{price:,.1f}',14,GRAY)
    for i,p in enumerate(history):
        xx=px(i);col=GREEN if p['close']>=p['open'] else RED;bw=max(2,w/len(history)*.29)
        d.line((xx,py(p['high']),xx,py(p['low'])),fill=col,width=2);a,b=sorted([py(p['open']),py(p['close'])]);d.rectangle((xx-bw,a,xx+bw,max(a+2,b)),fill=col)
    for period,col in [(20,CYAN),(50,GREEN),(150,RED),(200,GOLD)]:
        pts=[(px(i),py(p[f'ma{period}'])) for i,p in enumerate(history) if p.get(f'ma{period}') is not None and lo<=p[f'ma{period}']<=hi]
        if len(pts)>1:d.line(pts,fill=col,width=2)
    for label,price,col in [('SUPPORT',record['support'],GREEN),('RESISTANCE',record['resistance'],RED)]:
        yy=py(price);length=w*ease(t/2);d.line((x,yy,x+length,yy),fill=col,width=2);text(im,(x+10,yy-23),label+f'  {price:,.2f}',16,col,True)
    selected=min(len(history)-1,int((.5+.5*math.sin(t*.32))*(len(history)-1)));xx=px(selected)
    d.line((xx,y,xx,y+h),fill='#697079',width=1)
    text(im,(x,y+h+15),history[0]['date']+'  —  '+history[-1]['date']+' | Yahoo Finance',14,GRAY)

def season(im,a,sym,t,rect):
    s=next(x for x in a['seasonality'] if x['symbol']==sym);x,y,w,h=rect;d=ImageDraw.Draw(im)
    panel(im,(x-14,y-10,x+w+14,y+h+40),'#121921');base=y+h*.55;limit=max(abs(p['return_pct']) for p in s['years']) or 1
    d.line((x,base,x+w,base),fill='#646b72',width=1)
    for i,p in enumerate(s['years']):
        xx=x+i*w/15;hh=p['return_pct']/limit*h*.37*ease((t-i*.055)/1.2);col=GREEN if p['return_pct']>=0 else RED
        bar3d(im,xx+4,base,w/15*.57,hh,col);text(im,(xx+w/30,y+h+12),str(p['year'])[2:],15,GRAY,anchor='mm')
    text(im,(x+12,y+10),f'{s["positive"]}/15 positive  |  Average {s["mean"]:+.2f}%',22,GOLD,True)

def frame(a,scene,t,portrait=False):
    w,h=(720,1280) if portrait else (1280,720);xpan=round(48+40*math.sin(t*.035));ypan=round(25+22*math.sin(t*.023));im=background(w,h).crop((xpan,ypan,xpan+w,ypan+h));d=ImageDraw.Draw(im)
    orbit(im,t,w*.82,h*.38,210 if portrait else 235)
    d.rectangle((0,0,w,58),fill='#101317');text(im,(28,16),'MARKET MIND',24,GOLD,True);text(im,(w-28,20),'WEEKLY BRIEFING',14,GRAY,anchor='rt')
    text(im,(32,81),scene['kicker'],16,GOLD,True)
    title_size=35 if portrait else 43
    title_y=wrapped(im,scene['title'],32,115,w-64,title_size,WHITE,True,4 if scene['kind']=='news' else 3)
    kind=scene['kind'];m=a['markets'];content_y=max(title_y+28,240 if not portrait else 350)
    if kind=='hero':
        text(im,(35,content_y+25),'WEEK IN REVIEW',24,GOLD,True)
        text(im,(35,content_y+74),'OCT 5–9, 2026',34,WHITE,True)
        text(im,(35,content_y+132),'NEXT WEEK',24,GOLD,True)
        text(im,(35,content_y+177),'OCT 12–16',34,WHITE,True)
        if not portrait:
            for k in range(8):bar3d(im,840+k*42,530,24,60+100*(.5+.5*math.sin(t*.25+k*.6)),GOLD)
    elif kind=='season':
        season(im,a,scene['symbol'],t,(40,content_y,w-92,360 if portrait else 230))
        s=next(x for x in a['seasonality'] if x['symbol']==scene['symbol'])
        wrapped(im,f'Best {s["best"]:+.2f}%  •  Worst {s["worst"]:+.2f}%\n2026 excluded • Past performance is not a forecast',40,content_y+(435 if portrait else 283),w-80,20,GRAY,maxlines=3)
    elif kind in ['chart','stock']:
        r=m[scene['symbol']]
        # Intercut chart detail and typographic information rather than holding one slide.
        if kind=='chart' or int(t/7)%2:
            chart(im,r,t%7,(52,content_y+12,w-155,330 if portrait else 215))
            wrapped(im,f'RSI {r["rsi"]:.1f} • ATR {r["atr"]:.2f} • CCI {r["cci"]:.1f}\nMA20 cyan | MA50 green | MA150 red | MA200 gold',40,content_y+(405 if portrait else 285),w-80,17,GRAY,maxlines=3)
        else:
            wrapped(im,f'${r["close"]:,.2f}',40,content_y,w-80,67,GOLD,True,2)
            wrapped(im,f'{r["weekly_pct"]:+.2f}% this week',40,content_y+100,w-80,34,GREEN if r['weekly_pct']>=0 else RED,True,2)
            wrapped(im,f'SUPPORT  {r["support"]:,.2f}\nRESISTANCE  {r["resistance"]:,.2f}',40,content_y+170,w-80,27,WHITE,True,3)
            wrapped(im,'Scenarios, not predictions',40,content_y+270,w-80,22,GRAY,False,2)
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
        n=scene.get('news');panel(im,(32,content_y-5,w-32,content_y+195),'#141c25')
        wrapped(im,'REPORTED HEADLINE',55,content_y+16,w-110,22,GOLD,True,1)
        wrapped(im,n['publisher'] if n else 'No verified current headline',55,content_y+70,w-110,34,WHITE,True,2)
        wrapped(im,n['published'][:10] if n else 'See source notes',55,content_y+135,w-110,21,GRAY,False,2)
        wrapped(im,'Attribution is not proof of market causation. Full links accompany this edition.',40,content_y+235,w-80,22,GRAY,maxlines=3)
    elif kind=='calendar':
        entries=scene.get('events') or scene.get('earnings') or []
        if not entries:wrapped(im,'Specific dates could not be verified.\nCheck the original calendar before the event.',40,content_y,w-80,32,WHITE,True,4)
        else:
            for k,e in enumerate(entries[:5]):
                yy=content_y+k*(100 if portrait else 59)
                text(im,(40,yy),'OCT '+e['date'][-2:],23,GOLD,True)
                label=e.get('event') or e.get('symbol','')+' • est.'
                wrapped(im,label,165,yy,w-200,24,WHITE,True,2)
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
    lines=fit(caption,w-80,27 if portrait else 25)
    for k,line in enumerate(lines):text(im,(w/2,cy+10+k*35),line,27 if portrait else 25,WHITE,False,'mt')
    footer='Not financial advice · Education only · I am not a licensed advisor'
    if portrait:
        text(im,(w/2,h-48),'Not financial advice · Education only',17,GRAY,anchor='mt');text(im,(w/2,h-26),'I am not a licensed advisor',16,GRAY,anchor='mt')
    else:text(im,(w/2,h-32),footer,16,GRAY,anchor='mt')
    d.rectangle((0,57,int(w*min(1,t/scene['duration'])),60),fill=GOLD)
    source='Source: Yahoo Finance • '+a['date']
    if kind=='season':source='Yahoo adjusted month-end data • 2011–2025'
    if kind=='news':source='Source: '+scene.get('news',{}).get('publisher','unavailable')+' • '+scene.get('news',{}).get('published','')[:10]
    if kind=='calendar':source='Sources: BLS / Nasdaq calendar • estimates labelled'
    text(im,(32,cy-32),source,14,GRAY)
    if not portrait:text(im,(w-30,cy-32),'AI-generated background illustration',13,GRAY,anchor='rt')
    # A short gold wipe makes scene changes visible without masking the narration.
    if t<.3:
        xx=round(w*(1-t/.3));d.rectangle((0,60,xx,h-50),fill='#171b21')
    return im

def render_piece(task):
    root,scene_index,start,end,portrait,index=task;root=Path(root);a=json.loads((root/'analysis.json').read_text());scenes=json.loads((root/'timing.json').read_text());scene=scenes[scene_index]
    w,h=(720,1280) if portrait else (1280,720);outw,outh=(1080,1920) if portrait else (1920,1080);fps=24
    dest=root/'chunks'/f'{index:04d}.mp4';dest.parent.mkdir(exist_ok=True)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-vf',f'scale={outw}:{outh}:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-threads','2',str(dest)],stdin=subprocess.PIPE)
    try:
        for n in range(round((end-start)*fps)):p.stdin.write(frame(a,scene,start+n/fps,portrait).tobytes())
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('FFmpeg encoding failed')
    except BaseException:
        p.kill();p.wait();raise
    return str(dest)
