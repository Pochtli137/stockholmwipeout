// Do the set pieces (gantry, sponsor arches, billboards and party boards) clear Google's tiles? Serve the REPO ROOT first:
//   python3 -m http.server 8820
//   blender -b --factory-startup -P neon/build.py -- --nobake --probe /tmp/probe.json   # every set-piece box, tagged
//   node setpieces_probe.cjs /tmp/probe.json [report.json]
// For each structure the player is parked just before it (the chase camera pulls the finest tiles in), then every box is
// tested two ways, the same raycasts as dump_track.cjs and check_lap.cjs: a 4x4 lattice of segments along each of its
// three axes (a tile surface crossing the box: a facade through a post, a roof through a board) and a 3x3 grid of
// vertical rays over its footprint (a tile surface inside the box or above it: a post buried in a building, an overhang).
// Posts may stand 0.8 m into the street and masts 2 m into the roof they stand on, by design.
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs');
const IN=process.argv[2], OUT=process.argv[3];
const P=JSON.parse(fs.readFileSync(IN,'utf8')), L=P.trackLen;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
// structures: an arch or the gantry is one object, the billboards share one mesh and are told apart by their part tag
const S={}; for(const b of P.boxes){ const k=b.obj==='billboards'?b.part.split(':')[0]:b.obj, part=b.obj==='billboards'?b.part.split(':')[1]:(b.part.includes(':')?b.part.split(':')[1]:b.part);
  (S[k]=S[k]||{key:k,boxes:[],meta:P.meta[k]||{}}).boxes.push({part,c:b.c}); }
(async()=>{ const br=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const p=await br.newPage({viewport:{width:1280,height:800}}); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:'+(process.env.PORT||8820)+'/index.html?check&grepp=normal'+(process.env.BANA?'&bana='+process.env.BANA:''));   // BANA=kultur
  for(let i=0;i<240;i++){ if(await p.evaluate(()=>!!window.__sw&&__sw.state()!=='loading')) break; await sleep(500); }
  await p.evaluate(()=>{ __sw.setPaused(true); document.getElementById('msg').style.visibility='hidden'; });
  const out=[];
  const ONLY=process.env.ONLY?process.env.ONLY.split(','):null;   // ONLY=arch_skeppsbron,board18: just these
  for(const s of Object.values(S).filter(s=>!ONLY||ONLY.includes(s.key)).sort((a,b)=>a.meta.t-b.meta.t)){
    await p.evaluate(t=>__sw.placeAt(t),((s.meta.t-30/L)%1+1)%1); await sleep(400);
    for(let w=0;w<60;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(150); } await sleep(300);
    const r=await p.evaluate(boxes=>{ const V=a=>__sw.camera.position.clone().set(a[0],a[1],a[2]);   // a THREE.Vector3 without the module
      const res=[]; for(const b of boxes){ const c=b.c.map(V);   // corner index = xi*4 + yi*2 + zi, y = the box's own up
        const skip=b.part==='mast'?2.0:b.part==='post'?0.8:0.0, h=c[2].distanceTo(c[0]), k=Math.min(0.9,skip/Math.max(h,0.01));
        for(const i of [0,1,4,5]) c[i].lerp(c[i+2],k);
        const pt=(fx,fy,fz)=>{ const a=c[0].clone().lerp(c[4],fx), b2=c[2].clone().lerp(c[6],fx), a2=c[1].clone().lerp(c[5],fx), b3=c[3].clone().lerp(c[7],fx);
          const lo=a.lerp(a2,fz), hi=b2.lerp(b3,fz); return lo.lerp(hi,fy); };
        const F=[0,1/3,2/3,1]; let cross=0, inside=0, above=0, worst=-1e9;
        for(const u of F) for(const v of F){
          if(__sw.segHit(pt(0,u,v),pt(1,u,v))!==null) cross++;
          if(__sw.segHit(pt(u,0,v),pt(u,1,v))!==null) cross++;
          if(__sw.segHit(pt(u,v,0),pt(u,v,1))!==null) cross++; }
        const ys=c.map(q=>q.y), y0=Math.min(...ys), y1=Math.max(...ys);
        for(const u of [0.1,0.5,0.9]) for(const v of [0.1,0.5,0.9]){ const q=pt(u,0.5,v), hs=__sw.hitsAt(q.x,q.z);
          for(const y of hs){ if(y>y1) above++; else if(y>y0) inside++; worst=Math.max(worst,y-y0); } }
        res.push({part:b.part,cross,inside,above,worst:+worst.toFixed(2)}); }
      return res; },s.boxes);
    // a mast that only sinks deeper into the roof it stands on (no facade crossed, nothing over it) is hidden: 'roof'
    const sunk=x=>x.part==='mast'&&x.cross<=2&&!x.above, bad=r.filter(x=>(x.cross||x.inside||x.above)&&!sunk(x)), roof=r.filter(x=>x.inside&&sunk(x));
    const row={key:s.key, t:+s.meta.t.toFixed(5), m:Math.round(s.meta.t*L), meta:s.meta, clip:bad.length>0, roof:roof.length>0,
      parts:[...bad,...roof].map(x=>`${x.part} x${x.cross} in${x.inside} up${x.above} (${x.worst} m over its foot)`)};
    out.push(row); console.log(row.clip?'CLIP':row.roof?'roof':'ok  ',row.key.padEnd(24),row.m+' m',JSON.stringify(s.meta.party||s.meta.brand),row.parts.join(' | ')); }
  console.log('clipping',out.filter(o=>o.clip).length,'of',out.length,'· masts sunk into their roof',out.filter(o=>o.roof&&!o.clip).length,'errors',errs.slice(0,3));
  if(OUT) fs.writeFileSync(OUT,JSON.stringify(out,null,1)); await br.close(); })();
