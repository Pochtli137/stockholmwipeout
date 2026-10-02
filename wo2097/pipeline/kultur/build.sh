#!/bin/sh
# WIPEOUT KULTURSTOCKHOLM: rebuild the textures (from ../../assets/kultur/copy.json), the track set and the six craft.
# The line and the survey are separate (see ../README.md, Kulturstockholm). Run from anywhere; --nobake for a quick look.
set -e; cd "$(dirname "$0")"
python3 make_textures.py
python3 craft_textures.py
blender -b --factory-startup -P build.py -- "$@"
blender -b --factory-startup -P build_craft.py -- "$@"
