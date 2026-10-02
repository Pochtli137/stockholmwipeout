"""The OFL fonts of WIPEOUT KULTURSTOCKHOLM, fetched once from the Google Fonts repository into ../../fonts/ (embedded by
the game and used by make_textures.py, so bakes and web match). All SIL Open Font License 1.1; the licence texts are
saved next to them.   python3 get_fonts.py"""
import os, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(H, '..', '..', 'fonts')
BASE = 'https://raw.' + 'githubusercontent.com/google/fonts/main/ofl/'
FILES = {   # local name: path in the repository
    'PlayfairDisplay.ttf': 'playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf',
    'PlayfairDisplay-Italic.ttf': 'playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf',
    'OFL-PlayfairDisplay.txt': 'playfairdisplay/OFL.txt',
    'DMSerifDisplay-Regular.ttf': 'dmserifdisplay/DMSerifDisplay-Regular.ttf',
    'OFL-DMSerifDisplay.txt': 'dmserifdisplay/OFL.txt',
    'Inter.ttf': 'inter/Inter%5Bopsz,wght%5D.ttf',
    'OFL-Inter.txt': 'inter/OFL.txt',
}
for name, path in FILES.items():
    out = os.path.join(FD, name)
    if os.path.exists(out): continue
    req = urllib.request.Request(BASE + path, headers={'User-Agent': 'stockholmwipeout-fonts/1'})
    open(out, 'wb').write(urllib.request.urlopen(req, timeout=60).read()); print(name, os.path.getsize(out))
