import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.animation import FuncAnimation, FFMpegWriter

BG="#0b1220"; GRID="#1c2740"; GREEN="#22c55e"; RED="#ef4444"; GOLD="#facc15"; WHITE="#f8fafc"; MUTED="#94a3b8"
C=[(110,110.5,107.5,108),(108,108.5,104.5,105),(105,105.5,100.2,101),
   (101,105.5,100.5,105),(105,108.5,104.5,108),(108,108.6,104.5,105),(105,105.3,100.1,101),(101,104.5,100.5,104),(104,106.5,103.5,106),
   (106,106.2,101.5,102),(102,102.3,97.8,100.8),(100.8,104,100.4,103.5),
   (103.5,103.8,100.5,101),(101,101.3,95.5,96),
   (96,96.5,93.5,94),(94,99.6,93.8,99.2),(99.2,100.2,98.6,98.9),(98.9,99.1,94.5,95),
   (95,95.3,91.5,92)]
AP=[0.2,0.8,1.4, 2.8,3.35,3.9,4.45,5.0,5.55, 6.5,7.1,7.7, 9.9,10.6, 13.2,13.8,14.4,15.2, 16.8]
GROW=0.35; FPS=30; DUR=22.0; N=int(FPS*DUR); S=100
fig=plt.figure(figsize=(5.4,9.6),dpi=200,facecolor=BG)
ax=fig.add_axes([0.06,0.31,0.88,0.47])
tax=fig.add_axes([0,0,1,1])
ease=lambda x:1-(1-max(0,min(1,x)))**3
fade=lambda t,s,d=0.4:max(0.0,min(1.0,(t-s)/d))
def win(t,s,e): return min(fade(t,s,0.3),max(0,min(1,(e-t)/0.3)))

def draw(fr):
    t=fr/FPS
    ax.clear(); tax.clear(); tax.axis("off"); tax.set_xlim(0,1); tax.set_ylim(0,1)
    ax.set_facecolor(BG); ax.set_xlim(-4.6,len(C)); ax.set_ylim(89,113)
    for y in range(90,113,3): ax.axhline(y,color=GRID,lw=0.6,zorder=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    tax.text(0.5,0.855,"Can SUPPORT",color=WHITE,ha="center",fontsize=26,weight="bold")
    tax.text(0.5,0.805,"break?",color=RED if t>=10.6 else GREEN,ha="center",fontsize=30,weight="bold")

    # support / resistance line
    broken=t>=10.6; flip=t>=14.8
    lc=GREEN if not broken else (RED if flip else GOLD)
    ax.axhline(S,color=lc,lw=2.4,alpha=0.9,zorder=1,linestyle="-" if not broken or flip else "--")
    ax.axhspan(S-0.6,S+0.6,color=lc,alpha=0.10,zorder=0)
    if not flip:
        ax.text(-4.3,S+0.9,"SUPPORT",color=lc,fontsize=12,weight="bold",alpha=1-fade(t,14.5))
    else:
        ax.text(-4.3,S+0.9,"RESISTANCE",color=RED,fontsize=12,weight="bold",alpha=fade(t,14.8))

    for i,(o,h,l,c) in enumerate(C):
        if t<AP[i]: continue
        p=ease((t-AP[i])/GROW); col=GREEN if c>=o else RED
        cc=o+(c-o)*p; hh=max(o,cc)+(h-max(o,c))*p; ll=min(o,cc)-(min(o,c)-l)*p
        big=(i==13 and t>=10.6)
        ax.plot([i,i],[ll,hh],color=col,lw=2.2 if big else 1.6,zorder=2)
        ax.add_patch(Rectangle((i-0.34,min(o,cc)),0.68,max(abs(cc-o),0.08),color=col,zorder=3))
        if big:
            g=0.25*(1-fade(t,11.0,1.5))+0.1
            ax.add_patch(Rectangle((i-0.6,94.8),1.2,7.2,color=RED,alpha=g,zorder=1))

    # touches
    a=fade(t,4.8)
    for i,y in [(2,100.2),(6,100.1)]:
        if a>0: ax.scatter(i,y-0.9,s=110,color=GREEN,alpha=a,edgecolors=WHITE,linewidths=1,zorder=5)
    if a>0: ax.text(3.5,96.6,"Buyers defend",color=GREEN,fontsize=12,weight="bold",ha="center",alpha=a)
    # wick not break
    w=fade(t,8.0)
    if w>0:
        ax.scatter(10,97.8-0.8,s=110,color=GOLD,alpha=w,edgecolors=WHITE,linewidths=1,zorder=5)
        ax.text(10,94.6,"Wick ≠ Break",color=GOLD,fontsize=12,weight="bold",ha="center",alpha=w)
    # break label
    b=fade(t,10.9)
    if b>0: ax.text(13.5,90.8,"BREAK!",color=RED,fontsize=16,weight="bold",ha="center",alpha=b)
    # retest
    r=fade(t,14.6)
    if r>0:
        ax.annotate("Retest",xy=(16,100.4),xytext=(16,104.5),color=WHITE,fontsize=12,weight="bold",ha="center",
                    arrowprops=dict(arrowstyle="->",color=WHITE,lw=1.6),alpha=r)

    caps=[(0,2.7,"Price keeps bouncing here...",WHITE),(2.8,6.3,"Buyers step in again and again",GREEN),
          (6.5,9.7,"Wick below? Watch the CLOSE",GOLD),(9.9,13.2,"Close below = support broken",RED),
          (13.4,16.6,"Old support → new resistance",WHITE)]
    for s,e,txt,col in caps:
        if s<=t<e: tax.text(0.5,0.23,txt,color=col,ha="center",fontsize=16,weight="bold",alpha=win(t,s,e))
    if t>=16.8:
        al=fade(t,16.8)
        tax.add_patch(FancyBboxPatch((0.08,0.175),0.84,0.11,boxstyle="round,pad=0.01,rounding_size=0.03",fc="#111c33",ec=GOLD,lw=1.5,alpha=al))
        tax.text(0.5,0.25,"Support is a ZONE,",color=WHITE,ha="center",fontsize=17,weight="bold",alpha=al)
        tax.text(0.5,0.198,"not a promise",color=GOLD,ha="center",fontsize=19,weight="bold",alpha=al)
        if t>=19.0: tax.text(0.5,0.135,"Always use a stop loss",color=RED,ha="center",fontsize=15,weight="bold",alpha=fade(t,19.0))

FuncAnimation(fig,draw,frames=N).save("sup_v.mp4",writer=FFMpegWriter(fps=FPS,bitrate=6000,codec="libx264",extra_args=["-pix_fmt","yuv420p"]),savefig_kwargs={"facecolor":BG})
print("ok")
