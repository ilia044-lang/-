"""Mix voice + SFX + music for the bedtime video.
Run from this folder after make_voices.py + the retime step produced voice_mix.wav and timing.json.
SFX/music files go in sfx/ (download from Soundza, ids in SOUNDZA-LICENSE.txt)."""
import re, json, numpy as np, subprocess, soundfile as sf
h=open('scene_voiced.html').read()
WN=json.loads(re.search(r'const WARP_NEW=(\[[^\]]*\])',h).group(1)); WO=json.loads(re.search(r'WARP_OLD=(\[[^\]]*\])',h).group(1))
fromOld=lambda t: float(np.interp(t,WO,WN))
T=json.load(open('timing.json')); dur=T['dur']; SR=44100
def load(p):
    pcm=subprocess.run(['ffmpeg','-loglevel','error','-i',p,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(pcm,dtype=np.float32).copy()
N=int((dur+0.3)*SR)
voice=load('voice_mix.wav'); voice=np.pad(voice,(0,max(0,N-len(voice))))[:N]
sfx=np.zeros(N,np.float32); mus=np.zeros(N,np.float32)
def put(buf,a,t,g):
    s=int(t*SR); e=min(N,s+len(a)); buf[s:e]+=a[:e-s]*g
creak=load('sfx/soundza-old-wooden-door-creak.wav'); bonk=load('sfx/soundza-deep-bonk-hit.wav')
for i,t in enumerate([4.6,10.1,14.6]): put(sfx,creak,fromOld(t)-0.05,0.45 if i<2 else 0.6)   # door opens
put(sfx,bonk,fromOld(23.8),0.7)                                                             # the kick
music=load('sfx/soundza-pizzicato-comedy-2.wav')
a_end=T['lines'][6][1]   # music stops dead after "what happens when we die?"
seg=music[:int(a_end*SR)].copy(); seg[-int(0.05*SR):]*=np.linspace(1,0,int(0.05*SR)); mus[:len(seg)]=seg*0.14
b0=T['cut']; seg2=music[int(40*SR):int(40*SR)+int((dur-b0+0.3)*SR)].copy()
fi=int(0.8*SR); seg2[:fi]*=np.linspace(0,1,fi); fo=int(1.5*SR); seg2[-fo:]*=np.linspace(1,0,fo); put(mus,seg2,b0,0.08)
mix=voice*0.9+sfx+mus; mix=mix/np.abs(mix).max()*0.95
sf.write('full_mix.wav',np.stack([mix,mix],1),SR)
