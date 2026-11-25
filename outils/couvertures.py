"""Couvertures Facebook (1640x624), X (1500x500), LinkedIn (1128x191 + 2x) avec le tableau de bord réel.
Usage : python3 -I outils/couvertures.py marque/couvertures"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from logo import badge
R = os.path.join(HERE, "..")
def fnt(n, s):
    for d in (os.path.join(HERE, "fonts"), "/usr/share/fonts/truetype/google-fonts"):
        p = os.path.join(d, n)
        if os.path.exists(p): return ImageFont.truetype(p, s)
B, M = "Poppins-Bold.ttf", "Poppins-Medium.ttf"
NUIT, FORET, EMER, OR, IVOIRE = (7, 24, 19), (12, 38, 31), (31, 138, 91), (232, 168, 62), (246, 241, 228)

def capture():
    im = Image.open(os.path.join(R, "campus-bourse/captures/sources/tableau-de-bord.png")).convert("RGB")
    for box in ([150, 365, 505, 440], [556, 362, 910, 412]):   # montants personnels floutés
        r = im.crop(box).filter(ImageFilter.GaussianBlur(14)); im.paste(r, box[:2])
    return im.crop((112, 128, 1748, 862))

def bg(W, H, gx=.78, gy=.1):
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    g = np.clip(1 - np.hypot((xx - W*gx)/W, (yy - H*gy)/H*(H/W)*2.2) * 1.5, 0, 1)[..., None] * .6
    a = np.array(NUIT) + (np.array(EMER) - np.array(NUIT)) * g
    im = Image.fromarray(a.astype("uint8")); d = ImageDraw.Draw(im, "RGBA")
    step = max(28, H // 12)
    for x in range(0, W, step): d.line((x, 0, x, H), fill=(255, 255, 255, 7))
    for y in range(0, H, step): d.line((0, y, W, y), fill=(255, 255, 255, 7))
    return im

def frame(im, shot, x, y, w, rad=None):
    k = w / shot.width; h = int(shot.height * k); bar = max(14, int(w * .028)); rad = rad or max(8, int(w * .018))
    sh = Image.new("RGBA", im.size); ImageDraw.Draw(sh).rounded_rectangle((x - 4, y + 14, x + w + 4, y + bar + h + 26), rad, fill=(0, 0, 0, 180))
    sh = sh.filter(ImageFilter.GaussianBlur(max(10, w // 40))); im.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((x, y, x + w, y + bar + h), rad, fill=(236, 236, 236))
    r = bar // 4
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = x + bar * .7 + i * r * 3.2; d.ellipse((cx - r, y + bar/2 - r, cx + r, y + bar/2 + r), fill=c)
    ux = x + bar * .7 + r * 9; d.rounded_rectangle((ux, y + bar*.2, x + w - bar*.5, y + bar*.8), bar*.3, fill=(255, 255, 255))
    d.text((ux + bar*.4, y + bar/2), "campusbourse.com", font=fnt(M, max(9, int(bar*.45))), fill=(90, 90, 90), anchor="lm")
    im.paste(shot.resize((w, h), Image.LANCZOS), (x, y + bar))
    d = ImageDraw.Draw(im, "RGBA"); d.rounded_rectangle((x, y, x + w, y + bar + h), rad, outline=OR, width=max(2, w // 400))
    return y + bar + h

def texte(im, x, y, s, logo_h, maxw, sous=True, site=True):
    lg = badge(logo_h); im.paste(lg, (x, y), lg); d = ImageDraw.Draw(im, "RGBA")
    y += logo_h + int(s * .5)
    f = fnt(B, s)
    lines = [[("Comprendre.", IVOIRE), ("Analyser.", IVOIRE), ("Décider.", OR)]]
    if d.textlength("Comprendre. Analyser. Décider.", font=f) > maxw:
        lines = [[("Comprendre.", IVOIRE), ("Analyser.", IVOIRE)], [("Décider.", OR)]]
    for ln in lines:
        xx = x
        for w, col in ln:
            d.text((xx, y), w, font=f, fill=col); xx += d.textlength(w + " ", font=f)
        y += int(s * 1.12)
    y += int(s * .2)
    if sous:
        fs = fnt(M, int(s * .44)); cur = ""
        for w in "Les sociétés cotées à la BRVM, expliquées simplement pour mieux décider.".split(" "):
            if cur and d.textlength(cur + " " + w, font=fs) > maxw:
                d.text((x, y), cur, font=fs, fill=IVOIRE + (215,)); y += int(s * .62); cur = w
            else: cur = (cur + " " + w).strip()
        d.text((x, y), cur, font=fs, fill=IVOIRE + (215,)); y += int(s * .75)
    if site:
        fc = fnt(B, int(s * .38)); t = "Ratios  ·  Dividendes  ·  Comparaisons  ·  Alertes"; tw = d.textlength(t, font=fc)
        ph = int(s * .8); y += int(s * .2)
        d.rounded_rectangle((x, y, x + tw + ph, y + ph), ph // 2, fill=OR)
        d.text((x + ph / 2, y + ph / 2), t, font=fc, fill=FORET, anchor="lm")
        y += ph + int(s * .22)
        d.text((x + 4, y), "campusbourse.com", font=fnt(B, int(s * .4)), fill=IVOIRE); y += int(s * .5)
    return y

def legal(im, W, H, s, x=None, anchor="rs"):
    d = ImageDraw.Draw(im, "RGBA")
    d.text((x if x else W - int(s*1.5), H - int(s*.9)), "Outil d'aide à l'analyse. Pas un conseil en investissement.", font=fnt(M, s), fill=IVOIRE + (140,), anchor=anchor)

def main(out):
    os.makedirs(out, exist_ok=True); shot = capture()
    # Facebook 1640x624 — zone sûre mobile ≈ centre 1110 px ; photo de profil en bas à gauche
    W, H = 1640, 624; im = bg(W, H)
    frame(im, shot, 1010, 118, 760)
    texte(im, 290, 56, 58, 84, maxw=680)
    legal(im, W, H, 17, x=1375)
    im.save(os.path.join(out, "couverture_facebook_1640x624.png"), optimize=True)
    # X 1500x500 — photo de profil en bas à gauche, bords haut/bas parfois rognés
    W, H = 1500, 500; im = bg(W, H)
    frame(im, shot, 930, 72, 650)
    texte(im, 300, 40, 46, 66, maxw=590)
    legal(im, W, H, 16, x=1440)
    im.save(os.path.join(out, "couverture_x_1500x500.png"), optimize=True)
    # LinkedIn page 1128x191 (rendu en 2x : 2256x382) — logo de page en bas à gauche
    W, H = 2256, 382; im = bg(W, H, .8, .2)
    frame(im, shot, 1640, 44, 560, rad=12)
    lg = badge(110); im.paste(lg, (430, 56), lg); d = ImageDraw.Draw(im, "RGBA")
    f = fnt(B, 62); xx = 430
    for w, col in (("Comprendre.", IVOIRE), ("Analyser.", IVOIRE), ("Décider.", OR)):
        d.text((xx, 190), w, font=f, fill=col); xx += d.textlength(w + " ", font=f)
    d.text((430, 290), "Ratios, dividendes, alertes : la BRVM en clair  ·  campusbourse.com", font=fnt(M, 34), fill=IVOIRE + (215,))
    im.save(os.path.join(out, "couverture_linkedin_2256x382.png"), optimize=True)
    im.resize((1128, 191), Image.LANCZOS).save(os.path.join(out, "couverture_linkedin_1128x191.png"), optimize=True)
    print("ok")

if __name__ == "__main__":
    main(sys.argv[1])
