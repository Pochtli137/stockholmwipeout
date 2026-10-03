# stockholmwipeout

Anti-grav-racing över Stockholm. Staden är **Googles Photorealistic 3D Tiles** (Cesium ion, `config.js`),
allt ovanpå är byggt i **Blender** och laddas som glb: bana, barriärer, pyloner, portal, bågar, skyltar och
sex skepp. HUD, skärmeffekter och bloom är three.js/DOM. Pipeline och kommandon: `wo2097/pipeline/README.md`.

Publikt repo `Pochtli137/stockholmwipeout`. Live https://stockholmwipeout.vercel.app (= `main`).
**Deploy = `vercel --prod --yes` från katalogen.** `.vercelignore` håller `blender/` och pipelinen utanför.

## Beslut (Kim, 2026-09-29)
- **Staden är Google.** En Blender-stad från OSM provades (gren `blender`) och fick nej: "det ser inte ut som riktiga Stockholm".
- **En look: NEON** (Kim 2026-09-29: "varför har vi neon och used? ta bort used"). USED-temat är pensionerat, sista commit
  med det är `730a8f7`. Med det försvann partiannonserna, parodiloggorna, pappersaffischerna och den grå asfalten.
  Flödet är **titelskärm → CHOOSE VEHICLE → race**: titeln ligger över en långsam kamera över Slussen medan tiles laddar,
  ENTER eller tryck lämnar över med en neonsvepning och en kamerasvep in i hangaren. I karusellen skymtar föregående och
  nästa skepp i vänster och höger kant. `?theme` ignoreras.
- **Skyltar måste läsas i full fart.**
- **Svenska varumärken som dystopiska parodier** (partiparodierna försvann med USED 2026-09-29).
- **Ljudet är det deployade.** Nytt motorljud, 3D-ljud, pad-ljud, partiklar och gnistor ligger avstängda bakom flaggor
  (`FX.particles`, `SFX.padSound`, `SFX.newPlayerEngine`, `SFX.spatial`, `SFX.hangar`).
- **Runor (yngre futharken) i stället för katakana**, Noto Sans Runic inbäddad.
- WebGPU provat och avvisat: tiles-biblioteket kräver WebGLRenderer.
- **Rälsen är spelet (Kim 2026-09-30):** "ett spel som handlar mer om upplevelse och samhällskritik". Fri styrning finns bara
  bakom den dolda utvecklarflaggan `?grepp=hart` (ingen G-växel, inget sparat val). `AI_EASE` (motståndarnas fart, 0,5) gäller
  alltid; `HARD_EASE` bara under flaggan. Rattarna står överst i fysikdelen av index.html.
- **Titelskärmen har Stockholms riktiga stadsvapen, S:t Erik** (Kim 2026-09-30: "vi kan använda riktiga st erik här").
  Filen är `wo2097/assets/stockholm_vapen.svg` från Wikimedia Commons (Koyos, CC BY-SA 2.5, märkt som skyddat insignia), krediterad
  i raden under laddningslinjen. Risken är flaggad för Kim: vapnet skyddas av lagen 1970:498 och staden kräver tillstånd för
  användning, främst ett problem i kommersiell kontext. Kreditraden får inte tas bort (CC BY-SA).
- **Banan är en berg-och-dalbana (2026-10-01):** fall på 22–37 m, tre krön med luftfärd och ett hopp över Västerbron (lucka
  260 m, 32 m över brons krön). Tuberna provades och togs bort. **Speakern provades och togs bort** (grenen
  `worktree-agent-a6f5d7aa01afc8d29` finns kvar i historiken; ElevenLabs-nyckeln ligger i `.env`).
- **Skölden är ett fält runt skeppet, men bara i 5 s efter en SHIELD-upplockning** (väggar biter inte, AI knuffas, missiler tas).
  Inget fält i vila (Kim 2026-10-01: "ta bort den där defaultskölden"); meshen göms helt, noll opacitet lämnade en artefakt.
- **Starten ligger mitt på Guldbron** (2026-10-01), 140 m in i varvet, så att IKÖA-skylten syns. Nedräkningsbandet är borta, bara siffran.
- **ENTERING-titlar** på Östermalm, Norrmalm (Vasastan ligger inte på varvet), Kungsholmen och Södermalm. Bara titeln: inga
  portar, inga moves, ingen musik (den versionen rullades tillbaka 2026-09-29).
- **Västerbron (2026-10-02):** bullet time i hoppet (0,37x, en roll, dämpad musik, vind, duns vid landning). Googles bro klipps bort
  vid rendering i en korridor över vattnet (datan orörd) och Mälaren fyller hålet på sin riktiga nivå (−20,69 m i spelets ram,
  nollan ligger 45 m över ellipsoiden vid Medborgarplatsen). Pylonerna går ner i vattnet med skumringar. Porten över avstampet
  säger bara **"DU HAR MYCKET ATT LEVA FÖR"**, utan stödlinjens nummer (Kim: "det här är en dystopi"). Brostumpar i betong provades
  och togs bort (grenen `stump`): de drog mer blick än skarven. Kilen under brons ände vid Långholmen syns svagt, accepterad.
- **Studs vid landningen efter Västerbron** (Kim 2026-10-02): cirka 1 m, sedan 0,17 m, stilla efter 1,4 s. Ratten är `BOUNCE` vid `AIR`.
- **Utvecklarläge:** `?test=vasterbron` startar 500 m före hoppet och startar om 3 s efter landning (R direkt). `?test=<meter>` valfri plats.
- **Partiannonserna är tillbaka i neon**, åtta partier lika, utan Direktdemokraterna. Slogans och symboler i `wo2097/pipeline/README.md`.
- **Mobil styrs bara med tilt** (tillstånd frågas vid TAP på titeln, kräver HTTPS). Styrplattan är borta.
- **UI-ljud:** titel, ENTER, svep vid byte av skepp, lock-in vid val. Racets ljud är oförändrat.
- **Musik: nästa steg** (ElevenLabs Music, provlyssning först; kontot behöver credits).

## WIPEOUT KULTURSTOCKHOLM (live sedan 2026-10-04)
- **Andra banan** bakom `?bana=kultur` (Kim: "kör kulturstockholm, nya racers som passar scenariot ... jag vill ha en racer som heter
  'De aderton'"). Samma Google-Stockholm, 8,2 km, start vid Börshuset. Koncept i `kultur/KONCEPT.md`, **all text i
  `wo2097/assets/kultur/copy.json`**, pipeline i `wo2097/pipeline/kultur/` (README: Kulturstockholm).
- **Stockholm är standard och ska bete sig exakt som förut**: varje banväxel i index.html är `KULTUR ? … : <det gamla>`.
  Enda tillägget på Stockholm: raden *DU HAR LÅST UPP WIPEOUT KULTURSTOCKHOLM · KLICKA HÄR* (K) på resultatet.
- Sex egna farkoster (DE ADERTON är bossen), förmånerna STIPENDIUM, LIVSTIDSSTOL, SÅGNING, depåer vid **Riche** (alla) och
  **Den Gyldene Freden** (bara DE ADERTON), krogskyltar riktade mot gästerna, aldrig verksamheten. Inga partiannonser.
- **Musiken (2026-10-03, Kim valde variant A):** Vivaldis Sommaren, Presto (John Harrison, Wichita State University Chamber Players,
  Wikimedia Commons, CC BY-SA) på rakt tempo 160 med spelets egna big beat-trummor under, i stället för syntslingan. Tyst i
  nedräkningen, från början vid RIDÅ, P/M/dold flik stoppar den. Krediten på titeln (`copy.json title.musicCredit`) får inte tas bort.
  Källor i `wo2097/assets/kultur/music/sources.json`, bygget i `wo2097/pipeline/kultur/music/`, provsidan (A/B/C) i `kultur/musikprov/`.
  `/kultur/` står i `.vercelignore`: konceptet och provsidan deployas inte. Titel och hangar har kvar syntens UI-slinga.
- Österlen är lagt på hyllan: Googles tiles där är 2.5D (fas 0 och utseendetestet, TODO.md).

## Grenar
- `main`: live, neon-2097-versionen.
- `crafts`: gammal gren, allt ligger på `main`.
- `blender`: den avvisade OSM-staden. Lokal.
- `vasterbron`: inslagen i `main` 2026-10-02. `stump`: de avvisade brostumparna. Lokal.
- `osterlen`: fas 0 och utseendetestet för Österlen (hyllat). `kultur`: Wipeout Kulturstockholm. Båda inslagna i `main` 2026-10-04.

## Öppet
- **Cesium ion-token i `config.js` i det publika repot. Kim roterar den i Cesium ion.**
- Processbilder från 2026-09-28/29 i `~/Projects/_process/2026-09-28/stockholmwipeout/` (privat, utanför repot).
