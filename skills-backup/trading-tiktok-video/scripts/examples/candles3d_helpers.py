import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
BG="#0b1220"; G="#22c55e"; R="#ef4444"
C=[(100,103.5,99.5,103),(103,106.5,102.5,106),(106,109.5,105.5,109),(109,109.6,106.5,107),(107,107.5,104.5,105),
   (105,108.5,104.8,108),(108,111.5,107.5,111),(111,114.5,110.5,114),(114,114.6,111.5,112),(112,112.5,109.5,110),
   (110,113.5,109.8,113),(113,116.5,112.5,116),(116,119.5,115.5,119)]
def box(x,z0,z1,w=0.6,d=0.6):
    X=[x-w/2,x+w/2]; Y=[-d/2,d/2]; Z=[z0,z1]
    v=np.array([[a,b,c] for a in X for b in Y for c in Z])
    f=[[0,1,3,2],[4,5,7,6],[0,1,5,4],[2,3,7,6],[0,2,6,4],[1,3,7,5]]
    return [[v[i] for i in q] for q in f]
def shade(hexc,k):
    c=np.array(matplotlib.colors.to_rgb(hexc)); return tuple(np.clip(c*k,0,1))
def render(az,fn):
    fig=plt.figure(figsize=(5.4,9.6),dpi=200,facecolor=BG)
    ax=fig.add_axes([-0.25,0.2,1.5,0.62],projection="3d"); ax.set_facecolor(BG)
    ax.set_axis_off()
    # floor grid
    for x in np.arange(-1,14,1): ax.plot([x,x],[-3,3],[97,97],color="#1c2740",lw=0.6)
    for y in np.arange(-3,3.1,1): ax.plot([-1,13],[y,y],[97,97],color="#1c2740",lw=0.6)
    for i,(o,h,l,c) in enumerate(C):
        col=G if c>=o else R
        faces=box(i,min(o,c),max(o,c))
        ks=[0.55,0.55,0.75,1.0,0.85,0.65]  # bottom top front back left right ish
        pc=Poly3DCollection(faces,facecolors=[shade(col,k) for k in [0.4,1.15,0.7,0.95,0.8,0.6]],edgecolors=shade(col,1.3),linewidths=0.4)
        ax.add_collection3d(pc)
        ax.plot([i,i],[0,0],[l,min(o,c)],color=col,lw=1.8); ax.plot([i,i],[0,0],[max(o,c),h],color=col,lw=1.8)
        # shadow on floor
        ax.add_collection3d(Poly3DCollection([[[i-0.3,-0.3,97],[i+0.3,-0.3,97],[i+0.3,0.9,97],[i-0.3,0.9,97]]],facecolors=(0,0,0,0.35)))
    xs=np.linspace(1,13,2); ax.plot(xs,[0,0],103.8+(xs-4),color="white",lw=2.2)
    ax.set_xlim(-1,13); ax.set_ylim(-3,3); ax.set_zlim(97,121)
    ax.set_box_aspect((14,4,16)); ax.view_init(elev=14,azim=az); ax.dist=7
    fig.text(0.5,0.9,"UPTREND 3D test",color="white",ha="center",fontsize=24,weight="bold")
    fig.savefig(fn,facecolor=BG); plt.close(fig)
render(-62,"t3d.png")
