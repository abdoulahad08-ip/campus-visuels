"""Version claire du logo (ivoire + or, fond transparent) pour fonds verts. -> marque/logo_clair.png"""
import os, numpy as np
from PIL import Image
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
im = Image.open(os.path.join(R, "marque/logo_campus_bourse.png")).convert("RGB").crop((300, 300, 1750, 1720))
a = np.array(im).astype(float)
dist = (255 - a.min(axis=2))                       # écart au fond clair
alpha = np.clip((dist - 12) / 70, 0, 1)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
vert = (r < 120) & (g > r)                          # parties vert foncé -> ivoire
out = a.copy(); out[vert] = (246, 241, 228)
lum = a.mean(axis=2)
alpha = np.where(vert, np.clip((150 - lum) / 90, 0, 1), alpha)
gris = (~vert) & (np.abs(r - b) < 18) & (lum > 150)   # ombres grises -> retirées
alpha = np.where(gris, 0, alpha)
# reconstituer la couleur pure des pixels d'anti-crénelage dorés
rgba = np.dstack([out, alpha * 255]).astype("uint8")
Image.fromarray(rgba, "RGBA").save(os.path.join(R, "marque/logo_clair.png")); print("ok")
