// Kulturstockholm's race music in the real game, headless Chrome: loads, silent in the countdown, starts at RIDÅ, P/M/hidden tab
// stop it, resume continues, R restarts from the top, the loop seam wraps without a gap, the synth never runs.
const PW='/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const URL='http://127.0.0.1:'+(process.env.PORT||8831)+'/index.html?check&bana='+(process.env.BANA||'kultur');
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu','--autoplay-policy=no-user-gesture-required']});
  const p=await b.newPage({viewport:{width:1280,height:800}}); const errs=[], logs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ const t=m.text(); if(m.type()==='error'&&!/404/.test(t)) errs.push(t); if(/kultur-music/.test(t)) logs.push(t); });
  await p.goto(URL);
  const st=()=>p.evaluate(()=>({ s:window.__sw?__sw.state():'boot', k:window.__kmus?__kmus():null, mus:window.__mus?__mus():null }));
  for(let i=0;i<240;i++){ const s=await st(); if(s.s!=='boot'&&s.s!=='loading') break; await sleep(500); }
  await p.keyboard.press('Shift');   // the first gesture: the AudioContext, and the music starts loading
  const R={};
  let s=await st(); R.afterGesture={ state:s.s, k:s.k };
  for(let i=0;i<60&&!(s.k&&s.k.loaded);i++){ await sleep(250); s=await st(); }
  R.loadedAt={ state:s.s, loaded:s.k.loaded };
  // restart so we see a whole countdown with the file already decoded
  await p.keyboard.press('KeyR'); await sleep(300); s=await st(); R.countdown={ state:s.s, playing:s.k.playing, rms:s.k.rms };
  let tGo=null, tPlay=null; const t0=Date.now();
  for(let i=0;i<400;i++){ s=await st(); if(s.s==='race'&&tGo===null) tGo=Date.now(); if(s.k.playing&&tPlay===null){ tPlay=Date.now(); R.startPos=s.k.pos; break; } await sleep(10); }
  R.goToMusicMs=tPlay-tGo; await sleep(1500); s=await st(); R.racing={ state:s.s, playing:s.k.playing, pos:s.k.pos, rms:s.k.rms, gain:s.k.gain, lpHz:s.k.lpHz, synthBar:s.mus&&s.mus.bar };
  // P
  await p.keyboard.press('KeyP'); await sleep(400); s=await st(); R.paused={ paused:s.k.paused, playing:s.k.playing, pos:s.k.pos, rms:s.k.rms };
  await sleep(1000); s=await st(); R.pausedLater={ pos:s.k.pos, rms:s.k.rms };
  await p.keyboard.press('KeyP'); await sleep(400); s=await st(); R.resumed={ playing:s.k.playing, pos:s.k.pos, rms:s.k.rms };
  // M
  await p.keyboard.press('KeyM'); await sleep(400); s=await st(); R.muted={ audioOn:s.k.audioOn, playing:s.k.playing, rms:s.k.rms, gain:s.k.gain };
  await p.keyboard.press('KeyM'); await sleep(900); s=await st(); R.unmuted={ audioOn:s.k.audioOn, playing:s.k.playing, rms:s.k.rms, gain:s.k.gain, pos:s.k.pos };
  // hidden tab
  await p.evaluate(()=>{ Object.defineProperty(document,'hidden',{value:true,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); });
  await sleep(300); s=await st(); R.hidden={ playing:s.k.playing, rms:s.k.rms, pos:s.k.pos };
  await p.evaluate(()=>{ Object.defineProperty(document,'hidden',{value:false,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); });
  await sleep(400); s=await st(); R.visible={ playing:s.k.playing, rms:s.k.rms, pos:s.k.pos };
  // the loop seam: jump to 1.5 s before loopEnd and sample the level every 40 ms across it
  await p.evaluate(()=>__kmusSeek(151.2919-1.5)); const seam=[];
  for(let i=0;i<70;i++){ s=await st(); seam.push([s.k.pos,s.k.rms]); await sleep(40); }
  R.seam={ first:seam[3], wrapped:seam.find(x=>x[0]<5), minRmsAcross:Math.min(...seam.slice(5).map(x=>x[1])), last:seam[seam.length-1] };
  // R: from the top at the next RIDÅ
  await p.keyboard.press('KeyR'); await sleep(300); s=await st(); R.restart={ state:s.s, playing:s.k.playing, pos:s.k.pos };
  for(let i=0;i<600;i++){ s=await st(); if(s.k.playing) break; await sleep(10); } R.restartPlay={ state:s.s, pos:s.k.pos };
  R.errors=errs; R.logs=logs; console.log(JSON.stringify(R,null,1)); await b.close(); })();
