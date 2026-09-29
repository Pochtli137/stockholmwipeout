# STOCKHOLM WIPEOUT 2097 · Blender-byggda banan och skeppen

Staden är Googles Photorealistic 3D Tiles (via Cesium ion, som förut). Allt nytt ovanpå den är byggt i Blender
och laddas som glb i spelets egen koordinatram: banan, barriärerna, neonkanterna, fart- och vapenplattorna,
pylonerna ner till gatan, startportalen vid Slussen, sponsorbågarna, skyltarna och de sex skeppen.
Bara HUD:en, skärmeffekterna (fartstreck, blixtar, sköldkant), motorglöd, spår och bloom är three.js/DOM.

## Bygga om

    cd ~/Projects/stockholmwipeout && python3 -m http.server 8820 &      # repots rot, med config.js (ion-token)
    node wo2097/pipeline/dump_track.cjs          # 1. spelet i ?dump flyger varvet, snappar varje punkt mot gatan -> assets/track.json
    cd wo2097/pipeline
    python3 make_textures.py                     # 2. alla texturer med PIL -> tex/
    blender -b --factory-startup -P build.py     # 3. banan + skeppen, AO-bakade, Draco -> ../assets/track.glb, craft_<i>.glb

`--nobake` hoppar över AO-bakningen (snabbare iteration). Dumpen tar ett par minuter och behöver bara göras om
när rutten eller höjdlogiken ändras; spelet läser samma `track.json` och hoppar då över sin egen höjdsnappning,
så banan i glb:n och fysiken är exakt samma kurva.

## Regler

- **Bara egen design:** ligan (SAGL), lagen (KRONA AG, VALKYR SYSTEMS, AURORA-X, MÄLAR FANG, NORRSKEN DYNAMICS, ICEBREAKER)
  och varumärkena (VOLTA, SYNTHOLM, HYPERFJORD, NORDSONIC, ÖRE-X, MÄLARVÄRME, PSY-NUDEL) är påhittade. Inga Sony-, Psygnosis- eller DR-loggor.
- Materialnamnen i Blender styr beteendet i spelet: `pad_speed`/`pad_weapon` blir additiva (farten rullar, glyfen snurrar),
  `neon_*`/`light_*`/`core_*` får gå över 1.0 för bloomen, `light_0..4` är nedräkningsljusen på portalen.
- Skeppens noder: `flap_L`/`flap_R` (luftbromsarnas gångjärn), `eng_L`/`eng_R` (munstyckena).
- Bloomtröskeln är 1.4: bara emission (neon 2.6, kärnor 3.0, plattor 1.6) ska över. Blanka ytor i lågt solljus blev en vit boll; banan är därför satin (roughness 0.62).
- Typsnitt: Orbitron och Rajdhani (SIL Open Font License, `fonts/`), katakana från systemets Hiragino.
