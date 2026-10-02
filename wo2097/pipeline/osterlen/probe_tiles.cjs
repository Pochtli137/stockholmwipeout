// PHASE 0 for Wipeout Österlen: does Google have real 3D along the coast? Serve the REPO ROOT first (any port):
//   python3 -m http.server 8830 &   PORT=8830 node probe_tiles.cjs <outdir> [only1,only2]
//   close look: DIST=150 ALT=60 ERR=2 PORT=8830 node probe_tiles.cjs <outdir> glimmingehus,simrishamn_centrum
// Result 2026-10-02: every Österlen place is 2.5D (imagery on terrain), 0 % standing; Slussen 54 %. See TODO.md.
// Every place: probe_tiles.html loads the tiles, parks an oblique camera ~200 m over the ground and ~320 m out, waits until
// the tiles have settled, then a screenshot and a roughness survey (a 5 m grid of rays over 200 x 200 m: the share of
// samples standing more than 4 m over the lowest hit within 15 m, i.e. walls, roofs, trees and cliffs with real volume).
// Slussen in Stockholm is the reference for a full photogrammetry mesh.
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const OUT=process.argv[2]||path.join(__dirname,'probe'); fs.mkdirSync(OUT,{recursive:true});
const ONLY=process.argv[3]?process.argv[3].split(','):null;
const PLACES=[   // lat, lon from OSM / sv.wikipedia (2026-10-02); az = where the camera stands, seen from the place
  ['stockholm_slussen_ref',59.3200,18.0720,200],
  ['simrishamn_hamn',55.5597,14.3533,110], ['simrishamn_centrum',55.5566,14.3500,220],
  ['kivik_hamn',55.6879,14.2278,60], ['kiviks_musteri',55.6735,14.2690,210], ['kungagraven',55.6826,14.2339,160],
  ['kivik_art_centre',55.6747,14.2450,200], ['stenshuvud',55.6631,14.2728,100],
  ['vitemolla',55.6992,14.2050,70], ['baskemolla',55.5915,14.3153,110], ['brantevik',55.5152,14.3460,120],
  ['skillinge',55.4743,14.2845,150], ['glimmingehus',55.5009,14.2309,200], ['sandhammaren',55.3946,14.2043,170],
  ['kaseberga',55.3871,14.0657,170], ['ales_stenar',55.3827,14.0544,190] ];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']}); const rows=[];
  for(const [name,lat,lon,az] of PLACES){ if(ONLY&&!ONLY.includes(name)) continue;
    const p=await b.newPage({viewport:{width:1440,height:900}}); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
    const t0=Date.now();
    await p.goto(`http://localhost:${process.env.PORT||8830}/wo2097/pipeline/osterlen/probe_tiles.html?name=${name}&lat=${lat}&lon=${lon}&az=${az}&dist=${process.env.DIST||320}&alt=${process.env.ALT||200}&err=${process.env.ERR||8}`);
    let r=null; for(let i=0;i<400;i++){ r=await p.evaluate(()=>window.__probe); if(r&&(r.settled||r.phase==='no-ground')) break; await sleep(300); }
    await p.screenshot({path:path.join(OUT,name+'.png')});
    const row={ name, lat, lon, ground:r&&r.ground!=null?+r.ground.toFixed(1):null, ...(r&&r.rough||{}), s:Math.round((Date.now()-t0)/1000), errs:errs.slice(0,2) };
    rows.push(row); console.log(JSON.stringify(row)); await p.close(); }
  fs.writeFileSync(path.join(OUT,'probe.json'),JSON.stringify(rows,null,1)); await b.close(); })();
