import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.animation import FuncAnimation, FFMpegWriter
BG="#0b1220"; GRID="#1c2740"; GREEN="#22c55e"; RED="#ef4444"; GOLD="#facc15"; WHITE="#f8fafc"; MUTED="#94a3b8"
OR="#fb923c"; BL="#38bdf8"
FPS=30; DUR=29.0; N=int(FPS*DUR)
fig=plt.figure(figsize=(5.4,9.6),dpi=200,facecolor=BG)
ax=fig.add_axes([0.08,0.33,0.72,0.42]); tax=fig.add_axes([0,0,1,1])
cl=lambda x:max(0.0,min(1.0,x)); ease=lambda x:1-(1-cl(x))**3
fade=lambda t,s,d=0.4:cl((t-s)/d)
def win(t,s,e): return min(fade(t,s,0.3),cl((e-t)/0.3))
def path(keys,n=400,wig=0.035,seed=1):
    kx,ky=zip(*keys); x=np.linspace(0,1,n); y=np.interp(x,kx,ky)
    y=y+wig*np.sin(x*57+seed)*np.sin(x*13+seed*2); return x,y
MX,MY=path([(0,49.25),(0.3,49.6),(0.6,50.0),(0.63,50.40),(0.8,50.55),(1,50.65)])
AX,AY=path([(0,50.45),(0.3,50.0),(0.6,49.5),(0.8,49.9),(1,50.2)],seed=3)
BX,BY=path([(0,50.45),(0.3,50.0),(0.55,49.66),(0.8,50.3),(1,50.7)],seed=3)
# force exact touch points
AY[np.argmin(np.abs(AX-0.6))]=49.5
def upto(X,Y,p):
    m=X<=p; return X[m],Y[m]
def setup(lo,hi,ticks):
    ax.set_facecolor(BG); ax.set_xlim(-0.02,1.02); ax.set_ylim(lo,hi)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]); ax.yaxis.tick_right()
    ax.set_yticks(ticks); ax.set_yticklabels([f"${v:.2f}" for v in ticks],color=MUTED,fontsize=10)
    ax.tick_params(length=0)
    for v in ticks: ax.axhline(v,color=GRID,lw=0.7,zorder=0)

def draw(fr):
    t=fr/FPS
    ax.clear(); tax.clear(); tax.axis("off"); tax.set_xlim(0,1); tax.set_ylim(0,1)
    tax.text(0.30,0.84,"MARKET",color=OR,ha="center",fontsize=27,weight="bold")
    tax.text(0.525,0.84,"or",color=MUTED,ha="center",fontsize=20,weight="bold")
    tax.text(0.74,0.84,"LIMIT?",color=BL,ha="center",fontsize=27,weight="bold")
    cap=None
    if t<3.8:
        ax.set_visible(False)
        a=fade(t,0.3)
        for x,lab,col in [(0.3,"BUY\nMARKET",OR),(0.7,"BUY\nLIMIT",BL)]:
            tax.add_patch(FancyBboxPatch((x-0.16,0.47),0.32,0.14,boxstyle="round,pad=0.01,rounding_size=0.04",fc="#111c33",ec=col,lw=2.5,alpha=a))
            tax.text(x,0.54,lab,color=col,ha="center",va="center",fontsize=19,weight="bold",alpha=a)
        tax.text(0.5,0.40,"Which button do you press?",color=WHITE,ha="center",fontsize=16,weight="bold",alpha=fade(t,1.2))
        cap=(0,3.8,"Pick wrong = it costs you",RED)
    elif t<13.6:
        ax.set_visible(True); setup(49.0,50.9,[49.25,49.5,49.75,50.0,50.25,50.5,50.75])
        tax.text(0.08,0.765,"MARKET ORDER",color=OR,fontsize=15,weight="bold",alpha=fade(t,3.8))
        p=0.6*ease((t-3.9)/2.6) if t<8.3 else 0.6+0.06*cl((t-8.3)/0.7) if t<9.0 else 0.66+0.34*ease((t-9.0)/1.5)
        x,y=upto(MX,MY,p); ax.plot(x,y,color=WHITE,lw=2.2,zorder=3)
        if t>=6.5:
            a=fade(t,6.5); ax.axhline(50.0,xmax=1,color=WHITE,lw=1.2,ls="--",alpha=0.7*a,zorder=2)
            ax.scatter(0.6,50.0,s=140,color=WHITE,edgecolors=OR,linewidths=2,zorder=5,alpha=a)
            ax.text(0.02,50.06,"You wanted $50.00",color=WHITE,fontsize=11,weight="bold",alpha=a)
            if t<8.4:
                r=(t-6.5)%0.8
                ax.scatter(0.6,50.0,s=140+900*r,facecolors="none",edgecolors=OR,lw=2,alpha=max(0,0.8-r),zorder=4)
        if t>=9.0:
            a=fade(t,9.0); ax.scatter(0.63,50.40,s=160,color=OR,edgecolors=WHITE,linewidths=1.5,zorder=6,alpha=a)
            ax.text(0.30,50.47,"Filled $50.40",color=OR,fontsize=12,weight="bold",alpha=a)
        if t>=10.3:
            a=fade(t,10.3)
            ax.annotate("",xy=(0.7,50.40),xytext=(0.7,50.0),arrowprops=dict(arrowstyle="<->",color=RED,lw=2),alpha=a)
            ax.text(0.73,50.17,"SLIPPAGE\n-$0.40/share",color=RED,fontsize=11,weight="bold",alpha=a,va="center")
        cap=(3.8,8.2,"Instant fill. Any price.",OR) if t<8.2 else (8.2,13.6,"Fast move = you pay more",RED)
    elif t<21.6:
        ax.set_visible(True); setup(49.2,50.9,[49.25,49.5,49.75,50.0,50.25,50.5,50.75])
        tax.text(0.08,0.765,"LIMIT ORDER",color=BL,fontsize=15,weight="bold",alpha=fade(t,13.6))
        if t>=13.9:
            a=fade(t,13.9); ax.axhline(49.5,color=BL,lw=2,ls="--",alpha=a,zorder=2)
            ax.text(0.02,49.39,"Your limit $49.50",color=BL,fontsize=11,weight="bold",alpha=a)
        pa=ease((t-13.9)/3.3)
        aalpha=1.0 if t<18.0 else 1-fade(t,18.0,0.6)
        x,y=upto(AX,AY,pa); ax.plot(x,y,color=WHITE,lw=2.2,zorder=3,alpha=aalpha)
        if t>=16.3:
            a=fade(t,16.3)*aalpha; ax.scatter(0.6,49.5,s=170,color=GREEN,edgecolors=WHITE,linewidths=1.5,zorder=6,alpha=a)
            ax.text(0.62,49.30,"FILLED $49.50 ✓",color=GREEN,fontsize=12,weight="bold",alpha=a)
        if t>=18.0:
            pb=ease((t-18.0)/2.4); x,y=upto(BX,BY,pb); ax.plot(x,y,color=GOLD,lw=2.4,zorder=4)
            if t>=19.6:
                a=fade(t,19.6); ax.scatter(0.55,49.66,s=200,marker="X",color=RED,zorder=6,alpha=a)
                ax.text(0.60,49.57,"NOT FILLED",color=RED,fontsize=12,weight="bold",alpha=a,ha="left")
            if t>=20.4:
                ax.text(0.97,50.78,"Missed the move",color=GOLD,fontsize=11,weight="bold",ha="right",alpha=fade(t,20.4))
        cap=(13.6,17.9,"Your price — or better",BL) if t<17.9 else (17.9,21.6,"Price never comes? No fill.",GOLD)
    else:
        ax.set_visible(False)
        cards=[(0.585,"MARKET",OR,"✓ Fill guaranteed","✗ Price NOT guaranteed",21.8),
               (0.405,"LIMIT",BL,"✓ Price guaranteed","✗ Fill NOT guaranteed",23.6)]
        for y0,name,col,good,bad,s in cards:
            a=fade(t,s)
            tax.add_patch(FancyBboxPatch((0.08,y0),0.84,0.15,boxstyle="round,pad=0.01,rounding_size=0.03",fc="#111c33",ec=col,lw=2,alpha=a))
            tax.text(0.13,y0+0.11,name,color=col,fontsize=20,weight="bold",alpha=a,va="center")
            tax.text(0.13,y0+0.065,good,color=GREEN,fontsize=14,weight="bold",alpha=a,va="center")
            tax.text(0.13,y0+0.025,bad,color=RED,fontsize=14,weight="bold",alpha=a,va="center")
        if t>=25.3:
            a=fade(t,25.3)
            tax.add_patch(FancyBboxPatch((0.08,0.245),0.84,0.10,boxstyle="round,pad=0.01,rounding_size=0.03",fc=GOLD,ec=GOLD,alpha=a))
            tax.text(0.5,0.315,"Fast or thin stock?",color=BG,ha="center",fontsize=16,weight="bold",alpha=a)
            tax.text(0.5,0.268,"→ Use a LIMIT",color=BG,ha="center",fontsize=19,weight="bold",alpha=a)
    if cap and cap[0]<=t<cap[1]:
        tax.text(0.5,0.235,cap[2],color=cap[3],ha="center",fontsize=17,weight="bold",alpha=win(t,cap[0],cap[1]))

FuncAnimation(fig,draw,frames=N).save("ml_v.mp4",writer=FFMpegWriter(fps=FPS,bitrate=6000,codec="libx264",extra_args=["-pix_fmt","yuv420p"]),savefig_kwargs={"facecolor":BG})
print("ok")
