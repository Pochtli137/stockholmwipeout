# stockholmwipeout

Anti-grav-racing över Stockholm. Staden är **Googles Photorealistic 3D Tiles** (Cesium ion, `config.js`),
allt ovanpå är byggt i **Blender** och laddas som glb: bana, barriärer, pyloner, portal, bågar, skyltar och
sex skepp. HUD, skärmeffekter och bloom är three.js/DOM. Pipeline och kommandon: `wo2097/pipeline/README.md`.

Publikt repo `Pochtli137/stockholmwipeout`. Live https://stockholmwipeout.vercel.app (= `main`).
**Deploy = `vercel --prod --yes` från katalogen.** `.vercelignore` håller `blender/` och pipelinen utanför.

## Beslut (Kim, 2026-09-29)
- **Staden är Google.** En Blender-stad från OSM provades (gren `blender`) och fick nej: "det ser inte ut som riktiga Stockholm".
- **Två teman, spelaren väljer först:** titel → tema (NEON eller USED) → skepp → race. Bara det valda temats glb laddas
  (neon 4,8 MB, used 12,1 MB). `?theme=neon|used` för länkar och kontroller. NEON är 2097-looken från `b08a156`.
  USED är sliten Slussen-betong, tunnelbanekakel, lysrör och natrium, **annonser som tryckt papper** (ingen neon, inga
  ljuslådor), strålkastare på mörka tavlor och motorkäglor på 50 %.
- **Skyltar måste läsas i full fart**, minst lika bra som på neonbanan. Slitage på ram och vägg, aldrig över bokstäverna.
- **Svenska varumärken och de åtta riksdagspartierna som dystopiska parodier.** Parodinamn, egen typografi, inga riktiga
  loggor eller politiker, satiren mot makten och aldrig mot grupper av människor. **Direktdemokraterna tas inte med.**
- **Ljudet är det deployade.** Nytt motorljud, 3D-ljud, pad-ljud, partiklar och gnistor ligger avstängda bakom flaggor
  (`FX.particles`, `SFX.padSound`, `SFX.newPlayerEngine`, `SFX.spatial`, `SFX.hangar`).
- **Runor (yngre futharken) i stället för katakana**, Noto Sans Runic inbäddad.
- WebGPU provat och avvisat: tiles-biblioteket kräver WebGLRenderer.
- **Grepp hårt = fri styrning** bakom `?grepp=hart` (och G i pausen), av som standard. Kim: räls-versionen "railar ändå".
  Detaljer i `wo2097/pipeline/README.md`.
- **Used-asfalten är grå** (inte brun), med spricknät, lagningar och påhittade taggar i ytterfilerna, aldrig över plattorna.

## Grenar
- `main`: live, neon-2097-versionen.
- `crafts`: allt nytt (Blender-skepp, temaval, skeppsval, used universe, partier, runor). Lokal, inte pushad.
- `blender`: den avvisade OSM-staden. Lokal.

## Partiernas slogans
Listan står i `wo2097/pipeline/README.md`. Två tavlor och en affisch per parti, lika för alla åtta.

## Öppet
- **Cesium ion-token i `config.js` i det publika repot. Kim roterar den i Cesium ion.**
- Processbilder från 2026-09-28/29 i `~/Projects/_process/2026-09-28/stockholmwipeout/` (privat, utanför repot).
