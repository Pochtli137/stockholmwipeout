#!/bin/sh
# Rebuild textures + Blender models (the track dump is separate: see README.md). Run from anywhere.
set -e; cd "$(dirname "$0")"
python3 make_textures.py
blender -b --factory-startup -P build.py "$@"
