// Screenshots for the sky pass: facing the sun, away from it and over the water, from the chase camera on the lap.
//   node sky_shots.cjs <outdir>        (repo root served on :8820)
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path'); const OUT=process.argv[2]||'sky'; fs.mkdirSync(OUT,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']}); const p=await b.newPage({viewport:{width:1440,height:900}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if((m.type()==='error'||m.type()==='warning')&&!/404|GPU stall|ReadPixels/.test(m.text())) errs.push(m.type()+': '+m.text().slice(0,300)); });
  await p.goto('http://localhost:8820/index.html?check');
  for(let i=0;i<120;i++){ if(await p.evaluate(()=>!!window.__sw&&window.__sw.state()!=='loading')) break; await sleep(500); }
  await p.evaluate(()=>{ __sw.setPaused(true); for(const id of ['msg','band','sub']){ const e=document.getElementById(id); if(e) e.style.visibility='hidden'; } });
  const views=await p.evaluate(()=>{ const f=__sw.mkFrame(); let best={d:-2}, worst={d:2}; const sun=window.__SUN;
    for(let i=0;i<1200;i++){ const t=i/1200; __sw.frameAt(t,f); const d=f.fwd.x*sun.x+f.fwd.z*sun.z; if(d>best.d) best={t,d}; if(d<worst.d) worst={t,d}; }
    return { sun:best.t, away:worst.t }; });
  const water=await p.evaluate(async()=>{ const d=await fetch('wo2097/assets/track.json').then(r=>r.json()); const a=d.arches.find(a=>a.n==='SKEPPSBRON'); return a.t+0.004; });
  for(const [n,t] of [['facing_sun',views.sun],['away_from_sun',views.away],['over_water_skeppsbron',water]]){
    await p.evaluate(t=>__sw.placeAt(t),t); await sleep(500); for(let w=0;w<60;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(150); } await sleep(1500);
    await p.screenshot({path:path.join(OUT,n+'.png')}); }
  console.log(JSON.stringify({views,water,errors:errs.slice(0,8)})); await b.close(); })();
