"""Swedish to Younger Futhark (long-branch), the way a Viking-age carver would spell it: 16 runes, no doubled
consonants, voiced and voiceless stops share a rune, words split by the separator ᛫ (phrases by ᛬).
Used for the baked textures; the HUD strings in index.html were generated with it too."""
MAP={'a':'ᛅ','ä':'ᛅ','æ':'ᛅ','b':'ᛒ','p':'ᛒ','d':'ᛏ','t':'ᛏ','e':'ᛁ','i':'ᛁ','j':'ᛁ','f':'ᚠ','v':'ᚠ','g':'ᚴ','k':'ᚴ','q':'ᚴ',
     'h':'ᚼ','l':'ᛚ','m':'ᛘ','n':'ᚾ','o':'ᚢ','u':'ᚢ','w':'ᚢ','y':'ᚢ','ö':'ᚢ','ø':'ᚢ','å':'ᚬ','r':'ᚱ','s':'ᛋ','z':'ᛋ','x':'ᚴᛋ'}
SEP='᛫'
def word(w):
    w=w.lower().replace('ck','k').replace('ph','f').replace('th','t')
    out=[]
    for i,ch in enumerate(w):
        if ch=='c': r='ᛋ' if w[i+1:i+2] in ('e','i','y') else 'ᚴ'
        else: r=MAP.get(ch,'')
        for rr in r:
            if not out or out[-1]!=rr: out.append(rr)   # no doubled runes, as on the stones
    return ''.join(out)
def runes(text):
    import re
    return SEP.join(filter(None,(word(w) for w in re.split(r'[^A-Za-zÅÄÖåäöÆØæø]+',text))))
if __name__=='__main__':
    for s in ['VARV','PLATS','VAPEN','TURBO','SKÖLD','MÅL','START','RESULTAT','STOCKHOLMS STORA PRIS','LADDAR STADEN','HANGAR',
              'VÄLJ FARKOST','STOCKHOLM','IKÖA','VOLVÖ','SAAPH','SPOTIFAI','ERIXON','KLARNÅ','SYSTEMBÖLAGET','BANK ID']:
        print(f'{s:24s} {runes(s)}')
