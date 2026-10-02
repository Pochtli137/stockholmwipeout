// FEEL flythrough: a frame-stepped film of the best ~48 s of the lap (Nybroviken airtime + tube, the Norrmalm cut,
// the Klara sjö airtime), race camera with HUD, 1920x1080 at 30 fps. The fake clock drives the game one frame at a
// time and the tiles get real time to stream between frames (same method as the promo capture).
//   node film.cjs [outdir] [fromM] [seconds]     (server: PORT, default 8871)  then ffmpeg the frames (see README)
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const OUT=process.argv[2]||path.join(__dirname,'out','film'); const FROM=+(process.argv[3]||1250), SECS=+(process.argv[4]||48);
const PORT=process.env.PORT||8871, FR=1000/30, W=1920, H=1080;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const p=await b.newPage({viewport:{width:W,height:H},deviceScaleFactor:1}); const errs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error'&&!/404|favicon/.test(m.text())) errs.push(m.text()); });
  await p.clock.install(); await p.goto(`http://localhost:${PORT}/index.html?check${process.env.BANA?"&bana="+process.env.BANA:""}`);   // BANA=kultur
  const t0=Date.now(); while(Date.now()-t0<180000){ await p.clock.runFor(33); await sleep(25);
    if(await p.evaluate(()=>!!window.__sw&&__sw.state()==='race').catch(()=>false)) break; }
  const now=await p.evaluate(()=>Date.now()); await p.clock.pauseAt(now+50);
  await p.addStyleTag({content:'#msg,#sub{visibility:hidden!important}'});   // settle() pauses the game between frames: no PAUSE banner in the film
  const step=async()=>{ await p.evaluate(()=>{ const pl=__sw.player(); __sw.keys.ArrowUp=true; __sw.keys.ArrowLeft=pl.lat>0.8; __sw.keys.ArrowRight=pl.lat<-0.8; }); await p.clock.runFor(FR); };
  const settle=async ms=>{ const s=Date.now(); await p.evaluate(()=>__sw.setPaused(true));
    try{ while(Date.now()-s<ms){ if(await p.evaluate(()=>__sw.tilesIdle())) return; await p.clock.runFor(16); await sleep(60); } } finally{ await p.evaluate(()=>__sw.setPaused(false)); } };
  await p.evaluate(m=>{ const L=__sw.len(), t=m/L; __sw.placeAt(t); const pl=__sw.player(); pl.speed=__sw.MAXV;
    for(const o of __sw.ships()){ o.crossedStart=false; o.lap=1; o.done=false; }
    let k=0; for(const o of __sw.ships()){ if(o===pl) continue; k++; o.t=(t+(40+k*30)/L)%1; o.lat=[-4,4,-1.5,3,-3.5][k%5]; o.speed=__sw.MAXV*0.9; } },FROM-480);
  for(let i=0;i<400;i++){ await step(); if(await p.evaluate(m=>(((__sw.player().t%1)+1)%1)*__sw.len()>=m,FROM)) break; }   // pre-roll: up to speed, the film starts at FROM
  await settle(5000);
  fs.mkdirSync(OUT,{recursive:true}); const N=Math.round(SECS*30), log=[];
  for(let i=0;i<N;i++){ await step(); await settle(700);
    await p.screenshot({path:path.join(OUT,String(i).padStart(5,'0')+'.png')});
    if(i%30===0){ const s=await p.evaluate(()=>{ const pl=__sw.player(); return { m:Math.round((((pl.t%1)+1)%1)*__sw.len()), kmh:Math.round((pl.speed+pl.boost+(pl.gv||0))*3.6), air:+(pl.air||0).toFixed(2), airtime:__sw.stats().airtime }; });
      log.push({s:i/30,...s}); console.log(JSON.stringify(log[log.length-1])); } }
  fs.writeFileSync(path.join(OUT,'log.json'),JSON.stringify({log,errs},null,1));
  console.log(JSON.stringify({frames:N,errs:errs.slice(0,6)})); await b.close(); })();
