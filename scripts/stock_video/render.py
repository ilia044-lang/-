"""Animated, fixed-data chart analysis: tools move; historical prices do not."""
import json,math,textwrap,subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
import pandas as pd
from PIL import Image,ImageDraw,ImageFont

W,H=1080,1920
BG='#0f0f0f';FG='#eceef2';GRAY='#8a9099';GRID='#23262b'
GREEN='#4caf50';RED='#f23645';CYAN='#24c5d9';GOLD='#e4c44c';BLUE='#4088ff'
@lru_cache(maxsize=64)
def font(size,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)
def text(im,xy,s,size=26,col=FG,bold=False,anchor=None):ImageDraw.Draw(im).text(xy,str(s),fill=col,font=font(size,bold),anchor=anchor)
def center(im,y,s,size=32,col=FG):text(im,(540,y),s,size,col,True,'mt')
def line(im,pts,col,width=2):ImageDraw.Draw(im).line(pts,fill=col,width=width)
def box(im,rect,fill='#191b1e',outline=None,r=12,width=2):ImageDraw.Draw(im).rounded_rectangle(rect,radius=r,fill=fill,outline=outline,width=width)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def phase(u,a,b):return ease((u-a)/(b-a))
def lerp(a,b,f):return a+(b-a)*f
def date(s):return pd.Timestamp(s).strftime('%b %d, %Y')
def short(s):return pd.Timestamp(s).strftime('%b %d')
def money(x):return f'${x:,.2f}'
def dash(im,a,b,c,width=2,progress=1,offset=0):
    a=np.array(a);b=np.array(b);dist=np.linalg.norm(b-a);end=dist*progress
    if dist<1:return
    for pos in np.arange(-28+offset%28,end,28):
        lo=max(0,pos);hi=min(pos+16,end)
        if hi>lo:line(im,[tuple(a+(b-a)*lo/dist),tuple(a+(b-a)*hi/dist)],c,width)
def stroke(im,a,b,c,f=1,width=3):
    end=tuple(lerp(x,y,f) for x,y in zip(a,b));line(im,[a,end],c,width);return end
def cursor(im,pt,t,c=FG):
    x,y=pt
    if not 80<x<930 or not 330<y<1420:return
    dash(im,(82,y),(928,y),'#535963',1);dash(im,(x,334),(x,1220),'#535963',1)
    r=14+4*math.sin(t*4);d=ImageDraw.Draw(im);d.ellipse((x-r,y-r,x+r,y+r),outline=c,width=2)
    d.polygon([(x,y),(x+3,y+24),(x+11,y+16),(x+18,y+18)],fill=FG,outline=BG,width=2)

def init(output):
    global ROOT,A,D,L,S,ARR,BASE
    ROOT=Path(output);A=json.loads((ROOT/'analysis.json').read_text());D=pd.read_csv(ROOT/'daily.csv');L=A['last'];S=json.loads((ROOT/'timing.json').read_text())
    ARR={c:D[c].to_numpy() for c in D if c!='date'}
    BASE={0:base(0),1:base(1)}

class Camera:
    def __init__(self,z):
        self.start=lerp(len(D)-90,len(D)-26,z);self.count=len(D)-self.start
        wide_low=min(D.low.tail(90).min(),D.ma200.tail(90).min());wide_high=D.high.tail(90).max()
        close_low=min(D.low.tail(16).min(),D.ma20.iloc[-1]);close_high=D.high.tail(26).max()
        self.lo=lerp(wide_low,close_low,z)-L['atr']*.8;self.hi=lerp(wide_high,close_high,z)+L['atr']*.8
    def x(self,i):return 82+(i-self.start+.5)*846/(self.count+7)
    def y(self,p):return 1115-(p-self.lo)/(self.hi-self.lo)*780

def phone(im):
    text(im,(62,30),'9:41',31,bold=True);box(im,(414,23,666,64),'#000',r=23)
    d=ImageDraw.Draw(im)
    for i in range(4):d.rectangle((866+i*11,50-i*6,872+i*11,60),fill=FG)
    d.arc((927,30,965,62),208,332,fill=FG,width=4);d.arc((935,38,957,60),208,332,fill=FG,width=4)
    box(im,(985,36,1030,58),None,FG,5);d.rectangle((990,40,1022,54),fill=FG)
    box(im,(401,1871,679,1881),FG,r=5)
    center(im,1780,'Not financial advice · Education only',22,GRAY)
    center(im,1814,'I am not a licensed advisor',22,GRAY)

def base(z):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);v=Camera(z)
    phone(im);text(im,(42,112),A['company']+' · 1D',27,bold=True)
    text(im,(1038,116),date(A['analysis_date']),24,GOLD,True,'rt')
    c=GREEN if A['change']>=0 else RED
    text(im,(42,161),'  '.join(f'{k[0].upper()} {L[k]:.2f}' for k in ['open','high','low','close']),25,c)
    text(im,(1038,161),f'{A["change"]:+.2f} ({A["change_pct"]:+.2f}%)',25,c,anchor='rt')
    for x,n,c in [(42,20,CYAN),(294,50,GREEN),(546,150,RED),(810,200,GOLD)]:text(im,(x,207),f'MA{n} {L[f"ma{n}"]:.2f}',23,c)
    text(im,(42,248),f'Vol {L["volume"]/1e6:.2f}M · Data: close {date(A["date"])}',23,GRAY)
    text(im,(1038,248),'Yahoo Finance',21,GRAY,anchor='rt')
    step=max(1,round((v.hi-v.lo)/12/2)*2)
    for price in np.arange(math.ceil(v.lo/step)*step,v.hi,step):
        y=v.y(price);line(im,[(82,y),(928,y)],GRID,1);text(im,(945,y-12),f'{price:g}',21,GRAY)
    indices=list(range(math.ceil(v.start),len(D)))
    ticks=[indices[0],indices[-1]]+[i for i in indices[1:-1] if D.date.iloc[i][5:7]!=D.date.iloc[i-1][5:7]]
    if z>.95:ticks=[indices[0],indices[7],indices[14],indices[-1]]
    for i in ticks:
        if i not in [indices[0],indices[-1]] and min(v.x(i)-v.x(indices[0]),v.x(indices[-1])-v.x(i))<105:continue
        x=v.x(i);line(im,[(x,335),(x,1218)],GRID,1);text(im,(x,1418),short(D.date.iloc[i]),19,GRAY,anchor='mt')
    center(im,720,A['ticker']+', 1D',100,'#191b1d')
    bw=max(3,min(21,846/(v.count+7)*.67));volmax=max(ARR['volume'][indices])
    for i in indices:
        x=v.x(i);c=GREEN if ARR['close'][i]>=ARR['open'][i] else RED
        if ARR['high'][i]>=v.lo and ARR['low'][i]<=v.hi:
            line(im,[(x,max(335,v.y(ARR['high'][i]))),(x,min(1115,v.y(ARR['low'][i])))],c,2)
            ya,yb=sorted([v.y(ARR['open'][i]),v.y(ARR['close'][i])])
            if yb>=335 and ya<=1115:d.rectangle((x-bw/2,max(335,ya),x+bw/2,min(1115,max(ya+2,yb))),fill=c)
        d.rectangle((x-bw/2,1218-ARR['volume'][i]/volmax*94,x+bw/2,1218),fill=c)
    for key,c in [('ma20',CYAN),('ma50',GREEN),('ma150',RED),('ma200',GOLD)]:
        pts=[(v.x(i),v.y(ARR[key][i])) for i in indices if v.lo<=ARR[key][i]<=v.hi]
        if len(pts)>1:line(im,pts,c,3)
    y=v.y(L['close']);dash(im,(82,y),(928,y),GREEN,1)
    box(im,(928,y-16,1038,y+16),GREEN,r=0);text(im,(983,y),f'{L["close"]:.2f}',22,FG,True,'mm')
    text(im,(82,1240),'CCI 14',22,GRAY);text(im,(1038,1240),f'{L["cci"]:.2f}',22,BLUE,True,'rt')
    cy=lambda x:1393-(np.clip(x,-250,250)+250)/500*109
    for val in [-100,0,100]:dash(im,(82,cy(val)),(928,cy(val)),'#3c4650',1)
    for key,c in [('cci',BLUE),('cci_avg',GOLD)]:line(im,[(v.x(i),cy(ARR[key][i])) for i in indices],c,2)
    for j,label in enumerate(['+','/','↗','□','T']):text(im,(23,337+j*72),label,28,GRAY)
    return im

def trend(im,v,f=1):
    a=A['trend'];start=(v.x(a['a']),v.y(a['ya']));end=(v.x(a['b']),v.y(a['yb']))
    # Clip to the data pane, including lines whose anchor is outside a zoomed viewport.
    dx=end[0]-start[0];dy=end[1]-start[1]
    t0,t1=0.,1.
    for p,q in [(-dx,start[0]-82),(dx,919-start[0]),(-dy,start[1]-335),(dy,1115-start[1])]:
        if p==0:
            if q<0:return end
        elif p<0:t0=max(t0,q/p)
        else:t1=min(t1,q/p)
    if t0>t1:return end
    aa=(start[0]+dx*t0,start[1]+dy*t0);bb=(start[0]+dx*t1,start[1]+dy*t1)
    return stroke(im,aa,bb,GREEN,f,4)

def level(im,v,price,label,col,f=1,labels=True):
    y=v.y(price);pt=stroke(im,(90,y),(919,y),col,f,3)
    if labels and f>.15:
        box(im,(90,y-36,90+min(730,len(label)*14+16),y-4),BG,r=1);text(im,(96,y-33),label,23,col,True)
    if f>.98:box(im,(928,y-16,1038,y+16),col,r=0);text(im,(983,y),f'{price:.2f}',21,FG,True,'mm')
    return pt

def panel(im,rect,rows,show=1,col=GRAY):
    x,y,w,h=rect;box(im,(x,y,x+w,y+h),'#17191c',col)
    for j,(s,size,c,bold) in enumerate(rows):
        if j<=show:text(im,(x+26,y+24+j*48),s,size,c,bold)

def frame(index,t):
    u=t/S[index]['duration'];z=phase(u,0,.28) if index==5 else 1 if index>=6 else 0
    if index==9:z=1-ease(u)
    v=Camera(z);im=BASE[z].copy() if z in BASE else base(z);d=ImageDraw.Draw(im)
    if 3<=index<=8:trend(im,v)
    if 5<=index<=8:
        level(im,v,A['resistance'][-1],f'Resistance · {money(A["resistance"][-1])}',RED,labels=index!=5)
        level(im,v,A['support'],f'Support reference · {money(A["support"])}',GREEN,labels=index!=5)
    if index==0:
        rows=[(A['ticker']+' · DAILY SNAPSHOT',23,FG,True),(f'Above {A["above_count"]} of 4 moving averages',23,GREEN,False),(f'RSI(14) {L["rsi"]:.1f}  |  ATR {money(L["atr"])}',23,FG,False),(f'Volume {A["volume_ratio"]:.2f}× the 20-day average',22,FG,False),(f'Body: {A["anatomy"]["body_pct"]:.1f}% of the range',23,GOLD,False)]
        panel(im,(104,316,615,278),rows,math.floor(u*20),'#35383e')
        pt=(v.x(len(D)-1),v.y(lerp(L['ma200'],L['close'],phase(u,.1,.65))))
        cursor(im,pt,t,GOLD)
    elif index==1:
        a=(v.x(A['anchor']),v.y(A['anchor_price']));b=(v.x(len(D)-1),v.y(L['close']));f=phase(u,.08,.68);pt=tuple(lerp(x,y,f) for x,y in zip(a,b))
        tile=Image.new('RGBA',(W,H));ImageDraw.Draw(tile).rectangle((a[0],pt[1],pt[0],a[1]),fill=(64,136,255,35),outline=BLUE,width=2);im.paste(tile,(0,0),tile)
        cursor(im,pt,t,BLUE)
        text(im,(a[0]+15,a[1]+12),short(A['anchor_date'])+' low · '+money(A['anchor_price']),22,BLUE,True)
        if f>.99:box(im,(a[0]+20,b[1]+48,min(a[0]+420,920),b[1]+104),BLUE,r=6);text(im,(a[0]+32,b[1]+61),f'+{money(A["advance_dollars"])} (+{A["advance_pct"]:.1f}%)',24,FG,True)
    elif index==2:
        pt=trend(im,v,phase(u,.04,.8));cursor(im,pt,t,GREEN)
        a=A['trend'];text(im,(110,1080),'Anchor: '+short(D.date.iloc[a['a']])+' · '+money(a['ya']),23,GREEN,True)
    elif index==3:
        gap=A['gap']
        if gap:
            ya,yb=v.y(gap['high']),v.y(gap['low']);x=max(96,v.x(gap['index'])-12);right=lerp(x,919,phase(u,.05,.7));c=GREEN if gap['direction']=='up' else RED
            tile=Image.new('RGBA',(W,H));ImageDraw.Draw(tile).rectangle((x,ya,right,yb),fill=(76,175,80,45) if c==GREEN else (242,54,69,45),outline=c,width=2);im.paste(tile,(0,0),tile)
            cursor(im,(right,ya),t,c)
            if u>.7:text(im,(105,yb+15),'Remaining gap: '+money(gap['low'])+'–'+money(gap['high']),25,c,True)
        else:
            panel(im,(112,706,804,253),[(f'VOLUME: {L["volume"]/1e6:.2f}M',33,FG,True),(f'{A["volume_ratio"]:.2f}× the 20-session average',30,CYAN,True),(f'ATR(14): {money(L["atr"])}',29,FG,False),('No named chart pattern is assumed.',24,GRAY,False)],u*7)
            cursor(im,(v.x(lerp(len(D)-20,len(D)-1,phase(u,.05,.85))),1180),t,CYAN)
    elif index==4:
        pt=(90,v.y(A['resistance'][0]))
        for j,r in enumerate(A['resistance']):
            f=phase(u,.05+j*.27,.3+j*.27)
            if f:pt=level(im,v,r,'Resistance · '+money(r),RED,f)
        if u>.65:pt=level(im,v,A['support'],'Support reference · '+money(A['support']),GREEN,phase(u,.65,.9))
        cursor(im,pt,t,GREEN if u>.65 else RED)
    elif index==5:
        x=v.x(len(D)-1)
        for j,(key,dy) in enumerate([('high',-60),('open',-28),('close',28),('low',65)]):
            f=phase(u,.3+j*.08,.38+j*.08)
            if not f:continue
            y=v.y(L[key]);yy=y+dy
            stroke(im,(x-8,y),(x-100,yy+18),FG,f,2)
            if f>.85:box(im,(x-330,yy,x-105,yy+38),'#292d32',r=5);text(im,(x-316,yy+5),key.upper()+' '+f'{L[key]:.2f}',21,FG,True)
        cursor(im,(x,v.y(lerp(L['high'],L['low'],phase(u,.3,.85)))),t)
        if u>.66:
            a=A['anatomy'];panel(im,(112,851,804,244),[(f'Body {money(a["body"])} · Range {money(a["range"])}',27,FG,True),(f'Upper wick {money(a["upper_wick"])} · Lower {money(a["lower_wick"])}',25,FG,False),(f'Close position: {a["close_position"]:.1f}% of range',25,FG,False),(f'Volume: {A["volume_ratio"]:.2f}× average',25,GRAY,False)],(u-.66)*15)
    elif index==6:
        yy=735+round(50*(1-phase(u,0,.08)));box(im,(105,yy,917,yy+384),'#17191c','#35383e')
        text(im,(132,yy+24),'MOMENTUM & DAILY RANGE',28,FG,True);text(im,(132,yy+84),'RSI(14)',26,GRAY);text(im,(880,yy+77),f'{L["rsi"]:.1f}',54,CYAN,True,'rt')
        x0,x1,y=139,879,yy+180;line(im,[(x0,y),(x1,y)],'#383c42',10);target=x0+740*L['rsi']/100;end=lerp(x0,target,phase(u,.08,.3));line(im,[(x0,y),(end,y)],CYAN,6)
        for val in [30,70]:x=x0+740*val/100;line(im,[(x,y-12),(x,y+12)],GRAY,2);text(im,(x,y+20),str(val),20,GRAY,anchor='mt')
        d.ellipse((end-10,y-10,end+10,y+10),fill=CYAN)
        if u>.4:text(im,(139,yy+259),f'ATR(14) {money(L["atr"])} · {L["atr"]/L["close"]*100:.2f}% of close',28,FG,True)
        if u>.65:text(im,(139,yy+319),f'CCI(14) {L["cci"]:+.2f}',27,BLUE,True)
        cursor(im,(end,y if u<.45 else yy+280 if u<.75 else yy+333),t,CYAN)
    elif index==7:
        yy=700+round(70*(1-phase(u,0,.08)));box(im,(82,yy,1018,yy+686),'#17191c','#35383e')
        text(im,(111,yy+27),'REPORTED HEADLINES · '+A['ticker'],30,FG,True)
        text(im,(111,yy+77),'Sources shown; no causal price claim.',22,GRAY)
        for j,(key,col) in enumerate([('positive',GREEN),('risk',RED)]):
            begin=.08+j*.43
            if u<begin:continue
            y=yy+135+j*220;item=A['news'][key]
            box(im,(111,y,290,y+33),col,r=4);text(im,(122,y+5),key.upper(),21,FG,True)
            title=item['headline'] if item else 'No source-verified item available in this run.'
            for n,s in enumerate(textwrap.wrap(title,48)[:4]):text(im,(111,y+50+n*32),s,25,FG,True)
            if item:text(im,(111,y+183),(item['publisher']+' · '+short(item['published']))[:65],21,GRAY)
            line(im,[(111,y+211),(111+830*phase(u,begin,begin+.39),y+211)],col,3)
        text(im,(111,yy+601),'Headline feed only · full articles not verified.',21,GRAY)
        text(im,(111,yy+639),'Next earnings date: unverified.',21,GRAY)
    elif index==8:
        start=(v.x(len(D)-1)+12,v.y(L['close']));up=(905,v.y(A['resistance'][-1]+L['atr']*.35));down=(904,v.y(A['support']-L['atr']*.35))
        f=phase(u,.06,.47);dash(im,start,up,GREEN,4,f,t*20);pt=tuple(lerp(a,b,f) for a,b in zip(start,up))
        if u>.5:f=phase(u,.52,.94);dash(im,start,down,RED,4,f,t*20);pt=tuple(lerp(a,b,f) for a,b in zip(start,down))
        cursor(im,pt,t,GREEN if u<.5 else RED)
        panel(im,(110,964,800,131),[(f'Above {money(A["resistance"][-1])}: hold + stronger volume?',27,GREEN,True),(f'Below {money(A["support"])}: support fails?',27,RED,True)],1 if u>.5 else 0)
    else:
        shade=Image.new('RGBA',(W,H));ImageDraw.Draw(shade).rectangle((40,300,1040,1450),fill=(15,15,15,195));im.paste(shade,(0,0),shade)
        for j,(y,s,size,c) in enumerate([(580,'EDUCATION ONLY',63,GOLD),(700,'Not a recommendation',40,FG),(753,'to buy or sell.',40,FG),(946,'FOLLOW FOR THE NEXT',32,GRAY),(999,'DAILY CHART',55,FG)]):
            if u>j*.08:center(im,y+16*(1-phase(u,j*.08,j*.08+.15)),s,size,c)
        line(im,[(290,1080),(290+500*ease(u),1080)],GOLD,3)
    title=S[index]['title'];sub=S[index]['subtitle'];accent=S[index]['color']
    box(im,(47,1505,1033,1690),'#191b1e',accent,r=18,width=3)
    for j,s in enumerate(textwrap.wrap(title,38)):center(im,1532+j*40,s,32,FG)
    for j,s in enumerate(textwrap.wrap(sub,57)):center(im,1610+j*30,s,23,GRAY)
    line(im,[(48,1727),(1032,1727)],GRID,3);line(im,[(48,1727),(48+984*u,1727)],accent,3)
    return im

def cover(asset):
    im=Image.open(asset).convert('RGB').resize((W,H),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im)
    box(im,(230,85,850,146),'#14191c',GOLD,r=30);center(im,103,'DAILY CHART ANALYSIS',26,GOLD)
    f=font(208,True);title=A['ticker'];width=d.textbbox((0,0),title,font=f)[2];x=(W-width)/2
    for z in range(23,0,-1):d.text((x+z,177+z),title,font=f,fill='#37403d',stroke_width=2)
    d.text((x,177),title,font=f,fill='#edf2eb',stroke_width=2,stroke_fill='#d6cba7')
    center(im,444,A['company']+' · '+A['exchange'],28,FG)
    span=max(L['high']-L['low'],.01);y=lambda val:947-(val-L['low'])/span*380
    c=GREEN if L['close']>=L['open'] else RED
    d.rectangle((535,567,545,947),fill=c)
    ya,yb=sorted([y(L['open']),y(L['close'])]);yb=max(ya+2,yb)
    d.polygon([(588,ya),(605,ya-17),(605,yb-17),(588,yb)],fill='#1c542c' if c==GREEN else '#841524')
    d.polygon([(492,ya),(509,ya-17),(605,ya-17),(588,ya)],fill='#9cebbb' if c==GREEN else '#ff7782')
    d.rectangle((492,ya,588,yb),fill=c,outline=FG,width=2)
    for key,side in [('high','right'),('open','left'),('close','right'),('low','left')]:
        yy=y(L[key]);label_y=yy
        if key=='close' and abs(yy-567)<70:label_y=yy+75
        if key=='open' and abs(yy-947)<70:label_y=yy-75
        end=826 if side=='right' else 263;line(im,[(610 if side=='right' else 470,yy),(end,label_y)],FG,2)
        text(im,(842 if side=='right' else 247,label_y),key[0].upper()+' '+f'{L[key]:.2f}',31,FG,True,'lm' if side=='right' else 'rm')
    center(im,1000,'DAILY CLOSE',27,GOLD);center(im,1052,money(L['close'])+f'  {"▲" if A["change_pct"]>=0 else "▼"} {abs(A["change_pct"]):.2f}%',61,FG)
    box(im,(110,1540,970,1644),'#111719',GOLD,r=16)
    center(im,1557,f'ABOVE {A["above_count"]} OF 4 MAs',40,FG);center(im,1610,'THE LEVELS THAT MATTER',26,GOLD)
    box(im,(200,1683,880,1741),GOLD,r=29);center(im,1698,'ANALYSIS · '+date(A['analysis_date']).upper(),25,'#141719')
    center(im,1753,'Data: close '+date(A['date'])+' · Yahoo Finance',23,FG)
    center(im,1798,'Not financial advice · Education only',22,FG);center(im,1832,'I am not a licensed advisor',22,FG)
    im.save(ROOT/(A['ticker']+'_cover.png'))

def render_piece(spec):
    index,start,end,number=spec;dest=ROOT/'chunks'/f'{number:03d}.mp4';count=round((end-start)*30)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','1','-video_track_timescale','15360',str(dest)]
    with open(dest.with_suffix('.log'),'w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(count):proc.stdin.write(frame(index,start+n/30).tobytes())
            proc.stdin.close();assert proc.wait()==0
        except BaseException:proc.kill();proc.wait();raise
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=nb_frames','-of','json',str(dest)]));assert int(p['streams'][0]['nb_frames'])==count
    print('Rendered',index,number,count,'frames',flush=True)
    return dest
