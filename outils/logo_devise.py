"""Remplace la devise du logo source par « COMPRENDRE ◆ ANALYSER ◆ DÉCIDER » (25 nov 2026).
Entrée : marque/logo_campus_bourse_source.jpg -> sortie : marque/logo_campus_bourse.png"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOMBRE = len(sys.argv) > 1 and sys.argv[1] == "sombre"
im = Image.open(os.path.join(R, "marque/logo_campus_bourse_sombre_source.jpg" if SOMBRE else "marque/logo_campus_bourse_source.jpg")).convert("RGB")
a = np.array(im).astype(int)
band = a[1600:1720]; ys, xs = np.where((band.mean(axis=2) > 120) if SOMBRE else (band.min(axis=2) < 200))
y0, y1, x0, x1 = ys.min() + 1600, ys.max() + 1600, xs.min(), xs.max()
ref = a[y0 - 25].copy()
for y in range(y0 - 10, y1 + 11): a[y] = ref
out = Image.fromarray(a.astype("uint8")); cap = y1 - y0
FP = os.path.join(R, "outils/fonts/Montserrat-Bold.ttf")
s = 20
while True:
    f = ImageFont.truetype(FP, s); bb = f.getbbox("COMPRENDRE")
    if bb[3] - bb[1] >= cap: break
    s += 1
words = ["COMPRENDRE", "ANALYSER", "DÉCIDER"]; ws = [f.getlength(w) for w in words]
gap = ((x1 - x0) - sum(ws)) / 2  # même largeur totale que la devise d'origine
m = Image.new("L", im.size, 0); md = ImageDraw.Draw(m); x = x0; top = y0 - f.getbbox("C")[1]
for i, w in enumerate(words):
    md.text((x, top), w, font=f, fill=255); x += ws[i]
    if i < 2:
        cx, cy, r = x + gap / 2, y0 + cap / 2, cap * 0.26
        md.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=255); x += gap
W = im.width; gx = np.linspace(0, 1, W)[:, None]
c1, c2, c3 = np.array([168, 124, 48]), np.array([238, 206, 112]), np.array([176, 132, 52])
g = np.where(gx < .5, c1 + (c2 - c1) * gx / .5, c2 + (c3 - c2) * (gx - .5) / .5)
gold = Image.fromarray(np.tile(g[None], (im.height, 1, 1)).astype("uint8"))
if SOMBRE:  # texte ivoire, losanges or (comme le fichier d'origine)
    mt = Image.new("L", im.size, 0); ImageDraw.Draw(mt).bitmap((0, 0), m)
    md2 = Image.new("L", im.size, 0); dd = ImageDraw.Draw(md2); x = x0
    for i, w in enumerate(words):
        x += ws[i]
        if i < 2:
            cx, cy, r = x + gap / 2, y0 + cap / 2, cap * 0.26
            dd.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=255); x += gap
    from PIL import ImageChops
    out.paste(Image.new("RGB", im.size, (250, 245, 232)), (0, 0), ImageChops.subtract(m, md2))
    out.paste(gold, (0, 0), md2)
    out.save(os.path.join(R, "marque/logo_campus_bourse_sombre.png"))
else:
    out.paste(gold, (0, 0), m)
    out.save(os.path.join(R, "marque/logo_campus_bourse.png"))
print("ok", s, gap)
