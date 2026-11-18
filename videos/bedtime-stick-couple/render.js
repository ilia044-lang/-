const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const [,, html, out, fpsArg] = process.argv; const fps = +(fpsArg||24);
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+html); await p.evaluate(()=>document.fonts.ready);
  const dur = await p.evaluate(()=>window.DURATION);
  const ff = spawn('ffmpeg', ['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-movflags','+faststart',out], {stdio:['pipe','inherit','inherit']});
  const n = Math.round(dur*fps);
  for (let i=0;i<n;i++){ await p.evaluate(t=>window.render(t), i/fps); const buf = await p.screenshot({type:'png'}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('frames',n);
})();
