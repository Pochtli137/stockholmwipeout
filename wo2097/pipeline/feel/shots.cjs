// FEEL screenshots at the new features, from the race camera: node shots.cjs [outdir]  (server: PORT, default 8871)
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const OUT=process.argv[2]||path.join(__dirname,'out','shots'); fs.mkdirSync(OUT,{recursive:true});
const PORT=process.env.PORT||8871;
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const p=await b.newPage({viewport:{width:1280,height:720}}); const errs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
  await p.goto(`http://localhost:${PORT}/index.html?check&solo`);
  await p.waitForFunction(()=>window.__sw&&__sw.state()==='race',null,{timeout:180000});
  const T=await p.evaluate(()=>{ const d=window.__track||null; return null; });
  const drops=await p.evaluate(async()=>{ const r=await fetch('wo2097/assets/track.json').then(r=>r.json()); return {drops:r.drops,tubes:r.tubes,len:r.trackLen}; });
  const spots=[];
  for(const d of drops.drops){ spots.push([d.n+' crest',d.crest-60/drops.len]); spots.push([d.n+' dive',d.crest+(d.low-d.crest)*0.45]); }
  for(const [a,b2] of drops.tubes) spots.push(['tube '+Math.round(a*drops.len),a+(b2-a)*0.4]);
  spots.push(['bank',0.30]); spots.push(['wide strömmen',0.06]);
  const res=[];
  for(const [name,t] of spots){
    await p.evaluate(t=>{ __sw.setPaused(false); __sw.placeAt(t,0); __sw.player().speed=60; },t);
    for(let w=0;w<40;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await p.waitForTimeout(250); }
    await p.waitForTimeout(700);
    const f=name.replace(/[^a-z0-9]+/gi,'_').toLowerCase()+'.png'; await p.screenshot({path:path.join(OUT,f)}); res.push(f); }
  console.log(JSON.stringify({shots:res,errs:errs.slice(0,6)})); await b.close(); })();
