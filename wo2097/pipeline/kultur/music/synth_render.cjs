// The deployed race music as updateAudio plays it: scheduleStep from bar 0, musicGain 0.24+e*0.13, mFilter 520+e^2*15500 (tc 0.5).
// Optionally also the player's engine at race speed. node synth_render.cjs <index.html> <seconds> <out.wav> [engine]
const PW='/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs');
const [,,IDX,SEC,OUT,ENG]=process.argv; const src=fs.readFileSync(IDX,'utf8');
const grab=n=>{ const i=src.indexOf('function '+n+'('); let d=0,j=src.indexOf('{',i); for(;j<src.length;j++){ if(src[j]==='{') d++; else if(src[j]==='}'){ d--; if(d===0) break; } } return src.slice(i,j+1); };
const line=re=>src.split('\n').find(l=>re.test(l));
const code=[line(/^const BPM=130/),line(/^const BUILD_BARS=/),line(/^const ACID_A=/),line(/^const ACID_B=/),
  ...['noiseSrc','mKick','mSnare','mHat','mAcid','mRiser','mStab','mPad','mImpact','musicEnergy','scheduleStep'].map(grab)].join('\n');
(async()=>{ const b=await chromium.launch({channel:'chrome',headless:true}); const p=await b.newPage();
  const res=await p.evaluate(async({code,sec,eng})=>{
    const SR=44100; let actx=new OfflineAudioContext(2,SR*sec,SR), musicGain, mFilter, sharedNoise, distCurve, mstep=0;
    eval(code.replace(/^const /gm,'var ').replace(/function (\w+)\(/g,'var $1=function(').replace(/\}\nvar /g,'};\nvar ')+';');
    distCurve=new Float32Array(1024); for(let i=0;i<1024;i++) distCurve[i]=Math.tanh((i/1024*2-1)*2.2);
    const nb=actx.createBuffer(1,SR,SR), ch=nb.getChannelData(0); for(let i=0;i<SR;i++) ch[i]=Math.random()*2-1; sharedNoise=nb;
    mFilter=actx.createBiquadFilter(); mFilter.type='lowpass'; mFilter.frequency.value=520; mFilter.Q.value=0.7; mFilter.connect(actx.destination);
    musicGain=actx.createGain(); musicGain.gain.value=0; musicGain.connect(mFilter);
    let t=0.1; for(let s=0;t<sec;s++,t+=STEPDUR){ mstep=s; if(s%4===0){ const e=Math.min(1,(s/16)/BUILD_BARS);
        musicGain.gain.setTargetAtTime(0.24+e*0.13,t,0.5); mFilter.frequency.setTargetAtTime(520+e*e*15500,t,0.5); } scheduleStep(t,s); }
    if(eng){ const g=actx.createGain(); g.gain.value=0.026+70*0.0004; const lp=actx.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=600; g.connect(lp); lp.connect(actx.destination);
      for(const det of [0,7]){ const o=actx.createOscillator(); o.type='sawtooth'; o.frequency.value=45+70*1.5; o.detune.value=det; o.connect(g); o.start(0); } }
    const buf=await actx.startRendering(); const out=[];
    for(let c=0;c<2;c++){ const d=buf.getChannelData(c); const u8=new Uint8Array(d.buffer); let s=''; for(let i=0;i<u8.length;i+=0x8000) s+=String.fromCharCode.apply(null,u8.subarray(i,i+0x8000)); out.push(btoa(s)); }
    return {n:buf.length,ch:out}; },{code,sec:+SEC,eng:ENG==='engine'});
  const L=Buffer.from(res.ch[0],'base64'), R=Buffer.from(res.ch[1],'base64'), n=res.n, data=Buffer.alloc(n*8), hdr=Buffer.alloc(44);
  for(let i=0;i<n;i++){ data.writeFloatLE(L.readFloatLE(i*4),i*8); data.writeFloatLE(R.readFloatLE(i*4),i*8+4); }
  hdr.write('RIFF',0); hdr.writeUInt32LE(36+data.length,4); hdr.write('WAVE',8); hdr.write('fmt ',12); hdr.writeUInt32LE(16,16); hdr.writeUInt16LE(3,20); hdr.writeUInt16LE(2,22);
  hdr.writeUInt32LE(44100,24); hdr.writeUInt32LE(44100*8,28); hdr.writeUInt16LE(8,32); hdr.writeUInt16LE(32,34); hdr.write('data',36); hdr.writeUInt32LE(data.length,40);
  fs.writeFileSync(OUT,Buffer.concat([hdr,data])); console.log('wrote',OUT); await b.close(); })();
