"""Logo transparent (ivoire + or) pour fonds verts, tiré de la version sombre fournie le 25 nov.
-> marque/logo_clair.png (transparent) ; marque/avatar_sombre_1080.png"""
import os, numpy as np
from PIL import Image
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
im = Image.open(os.path.join(R, "marque/logo_campus_bourse_sombre.png")).convert("RGB")
a = np.array(im).astype(float)
bg = np.array([10, 66, 48.0])
al = np.clip((a[..., 0] - 30) / 130, 0, 1)[..., None]
fg = np.clip((a - (1 - al) * bg) / np.maximum(al, 1e-3), 0, 255)
rgba = np.dstack([fg, al[..., 0] * 255]).astype("uint8")
lg = Image.fromarray(rgba, "RGBA").crop((300, 300, 1750, 1720))
lg.save(os.path.join(R, "marque/logo_clair.png"))
av = im.crop((180, 180, 1868, 1868)).resize((1080, 1080), Image.LANCZOS)
av.save(os.path.join(R, "marque/avatar_sombre_1080.png")); print("ok")
