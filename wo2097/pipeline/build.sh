#!/bin/sh
# Rebuild the NEON textures + Blender track and craft (the track dump is separate: see README.md). Run from anywhere.
# The top-level make_textures.py / build.py / build_craft.py / faux_logos.py built the retired USED theme (2026-09-29).
set -e; cd "$(dirname "$0")/neon"
python3 make_textures.py
blender -b --factory-startup -P build.py "$@"
