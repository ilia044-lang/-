import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation, FFMpegWriter
exec(open('t3d.py').read().split("def render")[0])
FPS=30; DUR=10.0; N=int(FPS*DUR); FL=98.0
fig=plt.figure(figsize=(5.4,9.6),dpi=200,facecolor=BG)
ax=fig.add_axes([-0.35,0.14,1.7,0.72],projection="3d")
cl=lambda x:max(0.0,min(1.0,x)); ease=lambda x:1-(1-cl(x))**3
AP=[0.3+i*0.5 for i in range(len(C))]
def draw(fr):
    t=fr/FPS; ax.clear(); ax.set_facecolor(BG); ax.set_axis_off()
    for x in np.arange(-1,14,1): ax.plot([x,x],[-2,2],[FL,FL],color="#1e2c4a",lw=0.7)
    for y in np.arange(-2,2.1,1): ax.plot([-1,13],[y,y],[FL,FL],color="#1e2c4a",lw=0.7)
    for i,(o,h,l,c) in enumerate(C):
        if t<AP[i]: continue
        p=ease((t-AP[i])/0.4); col=G if c>=o else R
        cc=o+(c-o)*p; top=max(o,cc); bot=min(o,cc)
        if top-bot<0.05: top=bot+0.05
        ax.add_collection3d(Poly3DCollection([[[i-0.4,-0.4,FL],[i+0.4,-0.4,FL],[i+0.4,0.9,FL],[i-0.4,0.9,FL]]],facecolors=(0,0,0,0.45)))
        ax.plot([i,i],[0,0],[bot-(min(o,c)-l)*p,bot],color=col,lw=2.4)
        ax.plot([i,i],[0,0],[top,top+(h-max(o,c))*p],color=col,lw=2.4)
        ax.add_collection3d(Poly3DCollection(box(i,bot,top,0.75,0.75),
            facecolors=[shade(col,k) for k in [0.35,1.2,0.75,0.95,0.9,0.55]],edgecolors=shade(col,1.35),linewidths=0.5))
    if t>=7.0:
        p=ease((t-7.0)/1.2); xe=1+12*p; xs=np.array([1,xe])
        ax.plot(xs,[0.45,0.45],103.8+(xs-4),color="white",lw=2.6)
    ax.set_xlim(-1,13); ax.set_ylim(-2,2); ax.set_zlim(FL,121)
    ax.set_box_aspect((14,4,15))
    az=-80+30*(t/DUR); el=26-8*(t/DUR)
    ax.view_init(elev=el,azim=az)
    fig.texts.clear()
    fig.text(0.5,0.855,"How to spot an",color="#94a3b8",ha="center",fontsize=17,weight="bold")
    fig.text(0.5,0.805,"UPTREND",color=G,ha="center",fontsize=34,weight="bold")
FuncAnimation(fig,draw,frames=N).save("/mnt/user-data/outputs/uptrend_3d_demo.mp4",writer=FFMpegWriter(fps=FPS,bitrate=7000,codec="libx264",extra_args=["-pix_fmt","yuv420p"]),savefig_kwargs={"facecolor":BG})
