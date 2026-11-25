"""Couverture « version utilisateur » (composition du 25 nov) refaite avec le vrai logo et les vraies captures.
Usage : python3 -I outils/couverture_v2.py marque/couvertures  -> couverture_v2_2576x981.png + couverture_v2_facebook_1640x624.png"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
R = os.path.join(HERE, "..")
def fnt(n, s):
    for d in (os.path.join(HERE, "fonts"), "/usr/share/fonts/truetype/google-fonts", "/usr/share/fonts/truetype/dejavu"):
        p = os.path.join(d, n)
        if os.path.exists(p): return ImageFont.truetype(p, s)
MB, PM = "Montserrat-Bold.ttf", "Poppins-Medium.ttf"
NUIT, FORET, EMER, OR, OR2, IVOIRE = (6, 38, 28), (10, 60, 42), (24, 110, 74), (214, 166, 72), (238, 204, 120), (250, 247, 238)
S = os.path.join(R, "campus-bourse/captures/sources/")

def src(n, crop, flous=()):
    im = Image.open(S + n).convert("RGB")
    for b in flous: im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(14)), b[:2])
    return im.crop(crop)

def carte(base, img, x, y, w, nav=False, titre=None):
    k = w / img.width; h = int(img.height * k); bar = 26 if nav else 0; th = 44 if titre else 0
    H = h + bar + th
    sh = Image.new("RGBA", base.size); ImageDraw.Draw(sh).rounded_rectangle((x - 6, y + 18, x + w + 6, y + H + 30), 18, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(22)); base.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(base, "RGBA")
    d.rounded_rectangle((x, y, x + w, y + H), 16, fill=(12, 30, 25))
    if nav:
        d.rounded_rectangle((x, y, x + w, y + bar + 10), 16, fill=(236, 236, 236)); d.rectangle((x, y + bar, x + w, y + bar + 10), fill=(12, 30, 25))
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse((x + 16 + i * 20, y + 8, x + 28 + i * 20, y + 20), fill=c)
        d.rounded_rectangle((x + 90, y + 5, x + w - 16, y + 22), 8, fill=(255, 255, 255))
        d.text((x + 102, y + 13), "campusbourse.com", font=fnt(PM, 13), fill=(90, 90, 90), anchor="lm")
    if titre:
        d.text((x + 18, y + bar + 24), titre, font=fnt(MB, 20), fill=OR2, anchor="lm")
    base.paste(img.resize((w, h), Image.LANCZOS), (x, y + bar + th))
    d = ImageDraw.Draw(base, "RGBA"); d.rounded_rectangle((x, y, x + w, y + H), 16, outline=OR, width=3)

def main(out):
    W, H = 2576, 981
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    g = np.clip(1 - np.hypot((xx - W * .55) / W, (yy - H * .45) / H * .5) * 1.4, 0, 1)[..., None]
    a = np.array(NUIT) + (np.array(EMER) - np.array(NUIT)) * g * .75
    im = Image.fromarray(a.astype("uint8")); d = ImageDraw.Draw(im, "RGBA")
    # géométrie de fond : facettes et filets or
    for poly, al in (([(0, 0), (520, 0), (0, 600)], 14), ([(W, H), (W - 900, H), (W, 300)], 16), ([(1500, H), (2100, 520), (2600, H)], 10)):
        d.polygon(poly, fill=(255, 255, 255, al))
    for x0 in (1650, 1900, 2150):
        d.line((x0, H, x0 + 900, 0), fill=OR + (40,), width=2)
    pts = [(1760, 760), (1900, 640), (2010, 690), (2160, 520), (2280, 580), (2420, 360), (2576, 230)]
    d.line(pts, fill=OR + (90,), width=6, joint="curve")
    # logo clair
    lg = Image.open(os.path.join(R, "marque/logo_clair.png")); k = 600 / lg.height
    lg = lg.resize((int(lg.width * k), 600), Image.LANCZOS); im.paste(lg, (100, 160), lg); d = ImageDraw.Draw(im, "RGBA")
    # titre (taille ajustée pour ne jamais toucher les captures)
    x0, maxw = 790, 960
    L = [[("ANALYSEZ ET", IVOIRE)], [("COMPAREZ ", IVOIRE), ("LES SOCIÉTÉS", OR2)], [("DE LA ", IVOIRE), ("BRVM", OR2)]]
    sz = 100
    while max(sum(d.textlength(t, font=fnt(MB, sz)) for t, _ in ln) for ln in L) > maxw: sz -= 2
    f = fnt(MB, sz); y = 175
    for ln in L:
        x = x0
        for t, c in ln: d.text((x, y), t, font=f, fill=c); x += d.textlength(t, font=f)
        y += int(sz * 1.13)
    y += 26
    fs = fnt(PM, 36)
    for t in ("L'outil d'analyse fondamentale et d'aide à la décision", "dédié aux investisseurs de l'UEMOA."):
        d.text((x0, y), t, font=fs, fill=IVOIRE + (235,)); y += 48
    y += 34
    fb = fnt(MB, 40)
    for mots in ([("ÉVALUEZ ", IVOIRE), ("LA VALEUR DES SOCIÉTÉS", OR2)], [("COMPAREZ-LES ", IVOIRE), ("CÔTE À CÔTE", OR2)], [("REPÉREZ ", IVOIRE), ("LES RISQUES", OR2)]):
        d.ellipse((x0, y + 8, x0 + 32, y + 40), fill=OR); d.ellipse((x0 + 10, y + 18, x0 + 22, y + 30), fill=NUIT)
        x = x0 + 50
        for t, c in mots: d.text((x, y), t, font=fb, fill=c); x += d.textlength(t, font=fb)
        y += 60
    # contacts
    fc = fnt(MB, 52); cy = 905
    def rond(x, sym, sf):
        d.ellipse((x, cy - 36, x + 72, cy + 36), fill=OR); d.text((x + 36, cy), sym, font=sf, fill=NUIT, anchor="mm")
    rond(790, "www", fnt(MB, 20)); d.text((882, cy), "campusbourse.com", font=fc, fill=IVOIRE, anchor="lm")
    xp = 882 + d.textlength("campusbourse.com", font=fc) + 90
    rond(xp, "☎", fnt("DejaVuSans-Bold.ttf", 40)); d.text((xp + 92, cy), "+221 76 760 22 22", font=fc, fill=OR2, anchor="lm")
    d.text((W - 40, H - 22), "Outil d'aide à l'analyse. Pas un conseil en investissement.", font=fnt(PM, 20), fill=IVOIRE + (150,), anchor="rs")
    # vraies captures
    tdb = src("tableau-de-bord.png", (112, 128, 1748, 862), ([150, 365, 505, 440], [556, 362, 910, 412]))
    carte(im, tdb, 1850, 300, 690, nav=True)
    carte(im, src("trajectoire-5-ans.png", (130, 205, 1740, 650)), 2130, 70, 400, titre="Historique 5 ans")
    carte(im, src("comparer-radar.png", (720, 140, 1120, 495)), 1800, 560, 270, titre="Comparer")
    carte(im, src("dividende-rendement.png", (95, 95, 720, 185)), 1800, 120, 300, titre="Dividende & rendement")
    os.makedirs(out, exist_ok=True)
    im.save(os.path.join(out, "couverture_v2_2576x981.png"), optimize=True)
    im.resize((1640, 624), Image.LANCZOS).save(os.path.join(out, "couverture_v2_facebook_1640x624.png"), optimize=True)
    print("ok")

if __name__ == "__main__":
    main(sys.argv[1])
