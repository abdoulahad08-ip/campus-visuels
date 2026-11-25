"""Visuel X (Twitter) Campus Bourse : UNE image pro 1600x900, sans « glisse ».

Usage : python3 -I outils/visuel_x.py <dossier>/x.json <dossier>   -> <dossier>/x.png
x.json = {
  "tag": "Campus Bourse",                       # pastille en haut (court)
  "title": "Analysez la BRVM avec *méthode.*",  # 1 à 2 lignes, *mot* surligné en or
  "points": [                                   # exactement 3 : valeur, facilité, solution
    {"label": "Valeur",   "text": "4 piliers notés sur 100"},
    {"label": "Facilité", "text": "Fiches en 3 niveaux de lecture"},
    {"label": "Solution", "text": "Projections à 5 et 10 ans"}
  ],
  "cta": "Essai gratuit 7 jours",              # bouton
  "site": "campusbourse.com"
}
Pas d'emoji ; espaces insécables avant « : ? ! ». Mention légale en bas, fixe.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from logo import badge
HERE = os.path.dirname(os.path.abspath(__file__))
def _f(n):
    for d in (os.path.join(HERE, "fonts"), "/usr/share/fonts/truetype/google-fonts"):
        p = os.path.join(d, n)
        if os.path.exists(p): return p
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
B, M = _f("Poppins-Bold.ttf"), _f("Poppins-Medium.ttf")
FORET, NUIT, OR, OR2, IVOIRE = (14,42,35), (8,26,21), (227,162,59), (240,186,96), (244,238,223)
CORAIL, TURQ, EMER = (255,107,87), (46,196,182), (31,138,91)
W, H = 1600, 900

def F(p, s): return ImageFont.truetype(p, s)

def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    im = Image.new("RGB", (W, H), FORET)
    px = im.load()
    for y in range(H):  # dégradé diagonal vert forêt -> nuit
        for x in range(0, W, 4):
            t = (x / W * 0.6 + y / H * 0.4)
            c = tuple(int(FORET[i] * (1 - t) + NUIT[i] * t) for i in range(3))
            for k in range(4):
                if x + k < W: px[x + k, y] = c
    d = ImageDraw.Draw(im, "RGBA")
    # halo or en haut à droite + bande or à gauche
    for r in range(420, 0, -6):
        d.ellipse((W - 260 - r, -160 - r, W - 260 + r, -160 + r), fill=OR + (int(3 + (420 - r) / 30),))
    d.rectangle((0, 0, 14, H), fill=OR)
    lg = badge(84); im.paste(lg, (W - 80 - lg.width, 74), lg); d = ImageDraw.Draw(im, "RGBA")
    # tag
    ft = F(B, 26); tag = cfg.get("tag", "BRVM").upper()
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle((80, 90, 80 + tw + 44, 90 + 52), 26, fill=OR)
    d.text((102, 100), tag, font=ft, fill=FORET)
    # titre avec *surlignage*
    fT = F(B, 76); x, y = 80, 190; maxw = W - 160
    words = cfg["title"].split(" "); lines, cur = [], []
    for w_ in words:
        test = " ".join(cur + [w_]).replace("*", "")
        if d.textlength(test, font=fT) > maxw and cur: lines.append(cur); cur = [w_]
        else: cur.append(w_)
    lines.append(cur)
    hl = False
    for ln in lines:
        x = 80
        for w_ in ln:
            start, end = w_.startswith("*"), w_.endswith("*") or w_.rstrip(".!?,").endswith("*")
            if start: hl = True
            txt = w_.replace("*", "")
            ww = d.textlength(txt, font=fT)
            if hl:
                d.rounded_rectangle((x - 8, y + 10, x + ww + 8, y + 92), 10, fill=OR)
                d.text((x, y), txt, font=fT, fill=FORET)
            else:
                d.text((x, y), txt, font=fT, fill=IVOIRE)
            if end: hl = False
            x += ww + d.textlength(" ", font=fT)
        y += 96
    # 3 cartes : valeur / facilité / solution
    cols = [OR, TURQ, CORAIL]; cw, ch, gap = 450, 250, 35; cy = max(y + 100, 390)
    fl, fx = F(B, 30), F(M, 32)
    for i, p in enumerate(cfg["points"][:3]):
        cx = 80 + i * (cw + gap)
        d.rounded_rectangle((cx, cy, cx + cw, cy + ch), 28, fill=(244, 238, 223, 18), outline=cols[i], width=3)
        d.rounded_rectangle((cx + 28, cy + 28, cx + 28 + 64, cy + 28 + 64), 18, fill=cols[i])
        d.text((cx + 60, cy + 60), str(i + 1), font=F(B, 38), fill=FORET, anchor="mm")
        d.text((cx + 112, cy + 42), p["label"].upper(), font=fl, fill=cols[i])
        # texte du point, retour à la ligne
        words, line, ty = p["text"].split(" "), "", cy + 120
        for w_ in words:
            t = (line + " " + w_).strip()
            if d.textlength(t, font=fx) > cw - 56: d.text((cx + 28, ty), line, font=fx, fill=IVOIRE); ty += 44; line = w_
            else: line = t
        d.text((cx + 28, ty), line, font=fx, fill=IVOIRE)
    # bouton CTA + site
    by = cy + ch + 45; fb = F(B, 34)
    cta = cfg.get("cta", "Essai gratuit 7 jours"); bw = d.textlength(cta, font=fb) + 70
    d.rounded_rectangle((80, by, 80 + bw, by + 72), 36, fill=OR)
    d.text((80 + 35, by + 14), cta, font=fb, fill=FORET)
    d.text((80 + bw + 30, by + 14), cfg.get("site", "campusbourse.com"), font=fb, fill=OR2)
    d.text((W - 80, H - 40), "Outil d'aide à l'analyse. Pas un conseil en investissement.", font=F(M, 20), fill=(244, 238, 223, 150), anchor="rs")
    os.makedirs(out, exist_ok=True)
    im.save(os.path.join(out, "x.png"), optimize=True)
    print("ok x.png")

if __name__ == "__main__":
    main()
