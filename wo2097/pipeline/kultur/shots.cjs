// WIPEOUT KULTURSTOCKHOLM · the eye check. Serve the REPO ROOT first (PORT, default 8830):
//   node shots.cjs <outdir> title|landmarks|powerups|pits|unlock|mobile|all
// title: the title screen and every craft in the hangar. landmarks: a bot race, a still as each landmark comes up at race speed.
// powerups: STIPENDIUM, LIVSTIDSSTOL and SÅGNING in use. pits: Riche, and Den Gyldene Freden as DE ADERTON and as anyone else.
// unlock: Stockholm's results with the unlock line, Kulturstockholm's with the way back. mobile: landscape phone (?mobile=1).
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const OUT=process.argv[2], WHAT=process.argv[3]||'all', PORT=process.env.PORT||8830, BASE=`http://localhost:${PORT}/index.html`;
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); fs.mkdirSync(OUT,{recursive:true});
// metres along the racing line (plot_route.py), the camera wants the landmark ~120-200 m ahead
const LANDMARKS=[['01_borshuset_start',40],['02_gamla_stan_freden',250],['03_slussen_gondolen',430],['04_fotografiska',1150],['05_saltsjon',1500],
  ['06_af_chapman_moderna',1950],['07_grona_lund',2900],['08_skansen_hasselbacken',3250],['09_nordiska_museet',4050],['10_strandvagen',4750],
  ['11_dramaten_riche',5150],['12_nationalmuseum',5620],['13_operan',6080],['14_kulturhuset',6500],['15_stadshuset',7250],['16_riddarholmen',7800]];
async function page(b,q,opt={}){ const p=await b.newPage({viewport:{width:opt.w||1600,height:opt.h||900},deviceScaleFactor:opt.dpr||1,isMobile:!!opt.mobile,hasTouch:!!opt.mobile});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error'&&!/404/.test(m.text())) errs.push(m.text()); });
  await p.goto(BASE+q); p.errs=errs; return p; }
const until=async(p,fn,ms=120000)=>{ const t0=Date.now(); while(Date.now()-t0<ms){ if(await p.evaluate(fn).catch(()=>false)) return true; await sleep(300); } return false; };
const settle=async(p,ms=6000)=>{ const t0=Date.now(); while(Date.now()-t0<ms){ if(await p.evaluate(()=>window.__sw?__sw.tilesIdle():true).catch(()=>true)) break; await sleep(150); } await sleep(300); };
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']}); const log={};
  const run=k=>WHAT==='all'||WHAT===k;
  if(run('title')){ const p=await page(b,'?bana=kultur');
    await until(p,()=>document.getElementById('tpress').classList.contains('ready')); await sleep(2500);
    await p.screenshot({path:path.join(OUT,'title_kulturstockholm.png')});
    await p.keyboard.press('Enter'); await until(p,()=>window.__select&&__select().state==='select'); await sleep(2200);
    for(let k=0;k<6;k++){ const n=await p.evaluate(()=>document.getElementById('selTeam').textContent);
      await p.screenshot({path:path.join(OUT,`select_${k}_${n.toLowerCase().replace(/[^a-zåäö]+/g,'_')}.png`)}); await p.keyboard.press('ArrowRight'); await sleep(1300); }
    log.title=p.errs.slice(0,4); await p.close(); }
  if(run('landmarks')){ const p=await page(b,'?bana=kultur&check');
    await until(p,()=>window.__sw&&__sw.state()==='race',180000);
    await p.evaluate(()=>{ const tick=()=>{ const pl=__sw.player(); if(pl&&__sw.state()==='race'){ __sw.keys.ArrowUp=true; __sw.keys.ArrowLeft=pl.lat>0.8; __sw.keys.ArrowRight=pl.lat<-0.8; } requestAnimationFrame(tick); }; requestAnimationFrame(tick); });
    const L=await p.evaluate(()=>__sw.len()); let k=0; const sp=[];
    for(let i=0;i<4000&&k<LANDMARKS.length;i++){ const st=await p.evaluate(()=>({ m:(((__sw.player().t%1)+1)%1)*__sw.len(), s:__sw.state(), v:__sw.player().speed+__sw.player().boost }));
      const [name,m]=LANDMARKS[k]; const d=st.m-m;
      if(st.s==='race'&&d>=0&&d<60){ await p.screenshot({path:path.join(OUT,`race_${name}.png`)}); sp.push([name,Math.round(st.v*8.5)]); k++; }
      else if(d>=60&&d<L/2){ k++; }   // passed it between polls
      if(st.s==='done') break; await sleep(40); }
    log.landmarks={ shots:sp, errs:p.errs.slice(0,4) }; await p.close(); }
  if(run('powerups')){ const p=await page(b,'?bana=kultur&check');
    await until(p,()=>window.__sw&&__sw.state()==='race',180000); await sleep(4500);
    await p.evaluate(()=>{ __sw.keys.ArrowUp=true; });
    for(const w of ['TURBO','SHIELD','MISSILE']){
      if(w==='MISSILE') await p.evaluate(()=>{ const pl=__sw.player(), o=__sw.ships()[1]; o.t=pl.t+90/__sw.len(); o.lat=pl.lat; });
      await p.evaluate(w=>{ __give(w); },w); await sleep(900); await p.screenshot({path:path.join(OUT,`powerup_${w.toLowerCase()}_pickup.png`)});
      await p.keyboard.press('Space'); await sleep(w==='MISSILE'?350:500); await p.screenshot({path:path.join(OUT,`powerup_${w.toLowerCase()}_in_use.png`)});
      if(w==='MISSILE'){ await sleep(500); await p.screenshot({path:path.join(OUT,`powerup_missile_hit.png`)}); }
      await sleep(1500); }
    log.powerups=p.errs.slice(0,4); await p.close(); }
  if(run('pits')){ for(const [team,tag] of [[3,'naturvin'],[0,'de_aderton']]){ const p=await page(b,`?bana=kultur&check&team=${team}`);
      await until(p,()=>window.__sw&&__sw.state()==='race',180000); await sleep(4000);
      const P=await p.evaluate(()=>__pits().pits);
      for(const pit of P){ if(tag==='de_aderton'&&pit.k==='riche') continue;
        await p.evaluate(pit=>{ const pl=__sw.player(); pl.t=Math.floor(pl.t)+pit.t0+20/__sw.len(); pl.lat=pit.side*6; pl.speed=60; },pit);
        await p.evaluate(pit=>{ const tick=()=>{ const pl=__sw.player(); __sw.keys.ArrowUp=true; __sw.keys.ArrowRight=pit.side>0&&pl.lat<6; __sw.keys.ArrowLeft=pit.side<0&&pl.lat>-6; requestAnimationFrame(tick); }; requestAnimationFrame(tick); },pit);
        await settle(p,3000); await sleep(600);
        const st=await p.evaluate(()=>({ msg:document.getElementById('msg').textContent, v:Math.round((__sw.player().speed+__sw.player().boost)*8.5), pit:__pits().key }));
        await p.screenshot({path:path.join(OUT,`pit_${pit.k}_${tag}.png`)}); (log.pits=log.pits||[]).push({ team:tag, pit:pit.k, ...st }); }
      await p.close(); } }
  if(run('unlock')){ for(const [q,name] of [['?test=600','stockholm_results_unlock'],['?bana=kultur&test=600','kultur_results_back']]){ const p=await page(b,q);
      await until(p,()=>window.__state&&__state().state==='race',180000); await settle(p,4000);
      await p.evaluate(()=>__finish()); await sleep(1200); await p.screenshot({path:path.join(OUT,name+'.png')});
      (log.unlock=log.unlock||[]).push({ name, line:await p.evaluate(()=>{ const e=document.getElementById('banaLink'); return e?e.textContent:null; }), stored:await p.evaluate(()=>localStorage.getItem('swKulturUnlocked')) });
      await p.close(); } }
  if(run('mobile')){ const p=await page(b,'?bana=kultur&mobile=1',{w:844,h:390,dpr:2,mobile:true});
    await until(p,()=>document.getElementById('tpress').classList.contains('ready'),180000); await sleep(2000);
    await p.screenshot({path:path.join(OUT,'mobile_title.png')}); await p.close();
    const q=await page(b,'?bana=kultur&mobile=1&test=1300',{w:844,h:390,dpr:2,mobile:true});
    await until(q,()=>window.__state&&__state().state==='race',180000); await settle(q,5000); await sleep(1500);
    await q.screenshot({path:path.join(OUT,'mobile_race.png')}); log.mobile=q.errs.slice(0,4); await q.close(); }
  fs.writeFileSync(path.join(OUT,'shots_'+WHAT+'.json'),JSON.stringify(log,null,1)); console.log(JSON.stringify(log)); await b.close(); })();
