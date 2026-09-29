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
- **Grepp hårt = fri styrning, standard sedan 2026-09-29.** `?grepp=normal` eller G i pausen ger rälsen. Rattar: `HARD_EASE`
  (styrhjälp och grepptak, 0,5) och `AI_EASE` (motståndarnas fart, 0,5), överst i fysikdelen av index.html.
  Detaljer i `wo2097/pipeline/README.md`.

## Grenar
- `main`: live, neon-2097-versionen.
- `crafts`: gammal gren, allt ligger på `main`.
- `blender`: den avvisade OSM-staden. Lokal.

## Öppet
- **Cesium ion-token i `config.js` i det publika repot. Kim roterar den i Cesium ion.**
- Processbilder från 2026-09-28/29 i `~/Projects/_process/2026-09-28/stockholmwipeout/` (privat, utanför repot).
