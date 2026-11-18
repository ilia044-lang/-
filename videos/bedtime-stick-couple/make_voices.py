import numpy as np, soundfile as sf, json, subprocess, os, sys
from kokoro_onnx import Kokoro
S=sys.argv[1]
names=['am_michael','af_heart','af_sky','af_bella']
vo={n: np.fromfile(f'voices/{n}.bin',dtype=np.float32).reshape(-1,1,256) for n in names}
np.savez('voices.npz', **vo)
k=Kokoro('onnx/model.onnx','voices.npz')
CAST={'dad':('am_michael',1.0,0),'mom':('af_heart',1.0,0),'kid':('af_sky',0.92,4)}
LINES=[('mom',"They're finally asleep."),('dad',"Movie. Snacks. Total silence."),
 ('kid',"Mom... I'm thirsty."),('mom',"Your water is right by your bed, sweetie."),
 ('kid',"Dad... I need to pee."),('dad',"You just went. Twice."),
 ('kid',"Mom... what happens when we die?"),('dad',"So... movie?"),('mom',"Don't. Move.")]
os.makedirs('lines',exist_ok=True); out=[]
for i,(who,text) in enumerate(LINES):
    v,spd,semi=CAST[who]
    a,sr=k.create(text,voice=v,speed=spd,lang='en-us')
    raw=f'lines/raw_{i}.wav'; sf.write(raw,a,sr)
    fin=f'lines/line_{i}.wav'
    if semi:
        r=2**(semi/12)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',raw,'-af',f'asetrate={sr}*{r:.5f},aresample={sr},atempo={1/r:.5f}',fin],check=True)
    else:
        os.replace(raw,fin)
    d=sf.info(fin).duration; out.append({'who':who,'text':text,'dur':round(d,3),'file':fin}); print(i,who,round(d,2),text)
json.dump(out,open('lines.json','w'),indent=1)
