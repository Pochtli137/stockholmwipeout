// Play-through check of the whole lap over Google's tiles. Serve the REPO ROOT first: python3 -m http.server 8820
//   node check_lap.cjs [outdir]
// A) SWEEP: the player's craft is placed every 8 m around the lap with the real chase camera, the tiles stream in
//    around that camera, then: any tile geometry inside the track volume (highest hit across +-9 m above the slab
//    bottom), a tile between craft and camera, the camera inside a tile. Screenshots at every district and at the
//    three tightest corners.
// B) RACE: a bot drives the full lap against the AI in real time: frame time, yaw rate, lateral g, camera occlusion
//    every third frame, and whether the race finishes.
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const OUT=process.argv[2]||path.join(__dirname,'check'); fs.mkdirSync(OUT,{recursive:true});
const BANA=process.env.BANA||'';   // BANA=kultur: WIPEOUT KULTURSTOCKHOLM
const URL='http://localhost:'+(process.env.PORT||8820)+'/index.html?check&theme='+(process.env.THEME||'neon')+'&grepp='+(process.env.GREPP||'normal')+(BANA?'&bana='+BANA:'');   // THEME=neon|used, GREPP=normal|hart
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function open(b){ const p=await b.newPage({viewport:{width:1440,height:900}}); const errs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error'&&!/404/.test(m.text())) errs.push(m.text()); });
  await p.goto(URL); for(let i=0;i<120;i++){ const ok=await p.evaluate(()=>!!window.__sw&&window.__sw.state()!=='loading'); if(ok) break; await sleep(500); }
  return {p,errs}; }
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const report={ sweep:{}, race:{} };
  // ---------------------------------------------------------------- A) sweep
  { const {p,errs}=await open(b);
    await p.evaluate(()=>{ __sw.setPaused(true); document.getElementById('msg').style.visibility='hidden'; });
    const len=await p.evaluate(()=>__sw.len()), STEP=8, N=Math.round(len/STEP);
    // where to photograph: the districts (arches in track.json + start) and the three tightest corners
    const shots=await p.evaluate(async(B)=>{ const d=await fetch('wo2097/assets/'+(B==='kultur'?'kultur/':'')+'track.json').then(r=>r.json()); const L=__sw.len(), pts=[];
      const k=[]; for(let i=0;i<2000;i++) k.push([i/2000,__sw.curvAhead(i/2000,1).m]); k.sort((a,b)=>b[1]-a[1]);
      const worst=[]; for(const [t,m] of k){ if(worst.every(w=>Math.min(Math.abs(w.t-t),1-Math.abs(w.t-t))*L>400)) worst.push({t,n:'corner_R'+Math.round(1/m)+'m'}); if(worst.length===3) break; }
      pts.push({t:0.004,n:'start_slussen'}); for(const a of d.arches) if(a.d<260) pts.push({t:a.t,n:a.n.toLowerCase()});
      pts.push({t:0.5,n:'mid_lap'}); return pts.concat(worst); },BANA);
    const viol=[], occl=[], inside=[], tops=[]; let worstRel=-1e9, worstAt=null; const t0=Date.now();
    for(let i=0;i<N;i++){ const t=i/N;
      await p.evaluate(t=>__sw.placeAt(t),t);
      await sleep(120); for(let w=0;w<25;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(120); }
      const r=await p.evaluate(t=>{ const f=__sw.frameAt(t,__sw.mkFrame()); let hi=-1e9, hiLat=0;
        for(const lat of [-9,-7.5,-6,-4.5,-3,-1.5,0,1.5,3,4.5,6,7.5,9]){ const h=__sw.hitsAt(f.p.x+f.right.x*lat,f.p.z+f.right.z*lat); if(h.length&&h[0]-f.p.y>hi){ hi=h[0]-f.p.y; hiLat=lat; } }
        const cam=__sw.camera.position.clone(), ship=__sw.player().mesh.position.clone();
        const occ=__sw.segHit(ship,cam), ch=__sw.hitsAt(cam.x,cam.z);
        return { rel:hi, lat:hiLat, occ, camIn: ch.length? ch[0]-cam.y : null, x:f.p.x, z:f.p.z, y:f.p.y }; },t);
      const m=Math.round(t*len); tops.push([m, r.rel>-1e8? +(r.rel+r.y).toFixed(2) : null]);
      if(r.rel>worstRel){ worstRel=r.rel; worstAt={m,lat:r.lat}; }
      if(r.rel>-0.6) viol.push({m,lat:r.lat,rel:+r.rel.toFixed(2)});
      if(r.occ!==null) occl.push({m,d:+r.occ.toFixed(1)});
      if(r.camIn!==null&&r.camIn>-0.3) inside.push({m,above:+r.camIn.toFixed(1)});
      for(const s of shots) if(Math.abs(s.t-t)<0.5/N||(s.t>t&&s.t<t+1/N&&!s.done)){ s.done=true;
        await p.evaluate(t=>__sw.placeAt(t),s.t); await sleep(400); for(let w=0;w<40;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(150); } await sleep(600);
        await p.screenshot({path:path.join(OUT,`${s.n}.png`)}); }
      if(i%100===0) console.log(`sweep ${m}/${Math.round(len)} m · track ${viol.length} · camera ${occl.length+inside.length} · ${((Date.now()-t0)/1000)|0} s`); }
    fs.writeFileSync(path.join(OUT,'sweep_tops.json'),JSON.stringify(tops));   // the chase camera sees finer tiles than the survey: merge_sweep.py folds these back in
    report.sweep={ lengthM:Math.round(len), samples:N, trackIntrusions:viol.length, cameraOccluded:occl.length, cameraInside:inside.length,
      worstTileAboveDeck:{ rel:+worstRel.toFixed(2), ...worstAt }, first:{ track:viol.slice(0,8), occl:occl.slice(0,8), inside:inside.slice(0,8) }, errors:errs.slice(0,5) };
    await p.close(); }
  // ---------------------------------------------------------------- B) race
  { const {p,errs}=await open(b);
    await p.evaluate(()=>{ const S=window.__chk={ ft:[], yaw:0, latg:0, occ:0, frames:0, last:performance.now(), head:null, done:false, t0:performance.now() };
      const tick=()=>{ const now=performance.now(), dt=(now-S.last)/1000; S.last=now; S.frames++; if(S.frames>5) S.ft.push(dt*1000);
        const pl=__sw.player(); if(pl&&__sw.state()==='race'){
          const h=Math.atan2(pl.frame.fwd.x,pl.frame.fwd.z); if(S.head!==null&&dt>0){ let d=h-S.head; d=(d+Math.PI*3)%(Math.PI*2)-Math.PI; S.yaw=Math.max(S.yaw,Math.abs(d)/dt); } S.head=h;
          const v=pl.speed+pl.boost, k=__sw.curvAhead(((pl.t%1)+1)%1,1).m; S.latg=Math.max(S.latg,v*v*k/9.81);
          if(S.frames%3===0&&__sw.segHit(pl.mesh.position,__sw.camera.position)!==null) S.occ++;
          // the bot: full throttle, hold the middle of the track
          __sw.keys['ArrowUp']=true;
          if(!__sw.stats().hard){ __sw.keys['ArrowLeft']=pl.lat>0.8; __sw.keys['ArrowRight']=pl.lat<-0.8; }
          else { // hard mode is free steering: feed-forward the bend, PD on heading and lat, airbrake when steering runs out
            const K=__sw.keys, L=__sw.len(), t=((pl.t%1)+1)%1, v=pl.speed+pl.boost; K.ArrowLeft=K.ArrowRight=K.KeyQ=K.KeyE=false;
            const kf=0.5*__sw.curvAhead(t,1).signed+0.5*__sw.curvAhead((t+v*0.25/L)%1,1).signed;
            const auth=1.25/(1+v/170)*(pl.ph?pl.ph.steer:1), cap=__sw.grip()*(pl.ph?pl.ph.grip:1)/Math.max(v,12);
            const w=-kf*v+4*(Math.max(-0.3,Math.min(0.3,-pl.lat*0.05))-(pl.psi||0))+0.25*(pl.psi||0); let sc=w/auth;
            if(Math.abs(w)>cap*0.95||Math.abs(sc)>1){ if(w<0) K.KeyQ=true; else K.KeyE=true; sc=(w-(w<0?-0.55:0.55))/auth; }
            if(Math.abs(kf*v)>cap*1.3) K.ArrowUp=false;
            if(sc<-0.15) K.ArrowLeft=true; else if(sc>0.15) K.ArrowRight=true; } }
        if(__sw.state()==='done') S.done=true; requestAnimationFrame(tick); };
      requestAnimationFrame(tick); });
    const midShots=[0.30,0.52,0.74]; let ms=0, midSpeed=[];
    for(let i=0;i<960;i++){ const st=await p.evaluate(()=>({done:__chk.done,t:__sw.player().t,s:__sw.state(),v:__sw.player().speed+__sw.player().boost}));
      if(i%40===0) console.log('race',st.s,'lap progress',(st.t*100).toFixed(1)+'%');
      const u=((st.t%1)+1)%1; if(st.s==='race'&&ms<midShots.length&&u>midShots[ms]&&u<midShots[ms]+0.05){   // the ads at race speed, as the player sees them
        await p.screenshot({path:path.join(OUT,`race_fullspeed_${Math.round(midShots[ms]*100)}pct.png`)}); midSpeed.push(Math.round(st.v*3.6)); ms++; }
      if(st.done) break; await sleep(500); }
    const r=await p.evaluate(()=>{ const f=__chk.ft.slice().sort((a,b)=>a-b), q=x=>+f[Math.floor(x*(f.length-1))].toFixed(1);
      const res=document.getElementById('results'); return { finished:__chk.done, results:getComputedStyle(res).display!=='none', raceS:+((performance.now()-__chk.t0)/1000).toFixed(0),
        frameMs:{ median:q(0.5), p95:q(0.95), p99:q(0.99), max:q(1) }, fpsMedian:+(1000/q(0.5)).toFixed(0), maxYawDegPerS:+(__chk.yaw*57.3).toFixed(0), maxLateralG:+__chk.latg.toFixed(1),
        cameraOccludedFrames:__chk.occ, checkedFrames:Math.floor(__chk.frames/3), airtimeLandings:__sw.stats().airtime }; });
    await p.screenshot({path:path.join(OUT,'race_end.png')});
    report.race={ ...r, screenshotSpeedsKmh:midSpeed, errors:errs.slice(0,5) }; await p.close(); }
  fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,1)); console.log(JSON.stringify(report,null,1)); await b.close(); })();
