"""Habillage vertical (1080x1920) d'une leçon vidéo 16:9 pour TikTok / Reels.

Usage : python3 -I outils/video_vertical.py videos/<dossier>/habillage.json
habillage.json = {"tag": "LEÇON D'ANGLAIS", "titre": ["ligne 1", "ligne 2"], "surligne": "ligne surlignée en jaune",
                  "formule_titre": "Used to :", "formule": "habitude passée qui n'est plus vraie", "cta": "Enregistre pour réviser !"}
Produit fond.png dans le même dossier. La vidéo est ensuite posée par ffmpeg (voir outils/video_build.sh).
Zone vidéo : y = 760 à 1368 (1080 x 608).
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "fonts", "Poppins-Bold.ttf")
M = os.path.join(HERE, "fonts", "Poppins-Medium.ttf")
W, H = 1080, 1920
VY, VH = 760, 608
YEL, WHITE, DARK = (255, 214, 0), (255, 255, 255), (20, 20, 35)

p = sys.argv[1]
cfg = json.load(open(p, encoding="utf-8"))
out = os.path.join(os.path.dirname(p), "fond.png")

img = Image.new("RGB", (W, H))
top, bot = (24, 32, 72), (70, 20, 110)
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))


def fit(text, font_path, size, maxw):
    while size > 20:
        f = ImageFont.truetype(font_path, size)
        if d.textlength(text, font=f) <= maxw:
            return f
        size -= 2
    return ImageFont.truetype(font_path, size)


X = 70
# tag
ft = ImageFont.truetype(B, 38)
tw = d.textlength(cfg["tag"], font=ft)
d.rounded_rectangle([X, 150, X + tw + 56, 150 + 70], radius=35, fill=YEL)
d.text((X + 28, 150 + 10), cfg["tag"], font=ft, fill=DARK)
# titre
y = 270
for line in cfg["titre"]:
    f = fit(line, B, 86, W - 2 * X)
    d.text((X, y), line, font=f, fill=WHITE)
    y += 108
s = cfg["surligne"]
f = fit(s, B, 86, W - 2 * X - 40)
sw = d.textlength(s, font=f)
d.rounded_rectangle([X - 12, y + 8, X + sw + 16, y + 112], radius=14, fill=YEL)
d.text((X, y), s, font=f, fill=DARK)
assert y + 112 < VY - 20, "titre trop long"
# zone vidéo (placeholder blanc)
d.rectangle([0, VY, W, VY + VH], fill=(255, 255, 255))
# bas
y = VY + VH + 70
f = fit(cfg["formule_titre"], B, 56, W - 2 * X)
d.text((X, y), cfg["formule_titre"], font=f, fill=WHITE)
y += 80
for line in cfg["formule"].split("\n"):
    f = fit(line, M, 48, W - 2 * X)
    d.text((X, y), line, font=f, fill=WHITE)
    y += 66
y += 20
f = fit(cfg["cta"], B, 50, W - 2 * X)
d.text((X, y), cfg["cta"], font=f, fill=YEL)
fb = ImageFont.truetype(B, 36)
lab = "Campus des Bâtisseurs"
d.text((W - X - d.textlength(lab, font=fb), H - 150), lab, font=fb, fill=WHITE)
img.save(out)
print(out)
