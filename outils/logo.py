"""Logo Campus Bourse (marque/logo_campus_bourse_source.jpg, fourni le 25 nov 2026).
badge(h, mode) -> RGBA : logo posé sur un badge ivoire arrondi (comme la barre du site), lisible sur fond vert.
mode "h" = horizontal (icône + CAMPUS BOURSE), "v" = logo complet avec la devise."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "marque", "logo_campus_bourse.png")
CREME = (250, 248, 243)
_cache = {}

def _lockup(mode):
    if mode in _cache: return _cache[mode]
    im = Image.open(SRC).convert("RGB")
    import numpy as np
    a = np.array(im).astype(int); light = a.min(axis=2)
    t = np.clip((light - 215) / 25.0, 0, 1)[..., None]   # fond clair -> crème uniforme
    a = a * (1 - t) + np.array(CREME) * t
    im = Image.fromarray(a.astype("uint8"))
    d = ImageDraw.Draw(im)
    if mode == "v":
        out = im.crop((300, 300, 1750, 1720))
    else:
        icon = im.crop((490, 350, 1560, 1140))
        d.rectangle((340, 1230, 570, 1275), fill=CREME); d.rectangle((1480, 1230, 1710, 1275), fill=CREME)
        txt = im.crop((345, 1185, 1705, 1595))  # CAMPUS / BOURSE (filets effacés)
        k = 0.95 * icon.height / txt.height
        txt = txt.resize((int(txt.width * k), int(txt.height * k)), Image.LANCZOS)
        out = Image.new("RGB", (icon.width + 60 + txt.width, icon.height), CREME)
        out.paste(icon, (0, 0)); out.paste(txt, (icon.width + 60, (icon.height - txt.height) // 2))
    _cache[mode] = out
    return out

def badge(h, mode="h", pad=None):
    lk = _lockup(mode); pad = pad if pad is not None else int(h * 0.16)
    ih = h - 2 * pad; k = ih / lk.height
    lk = lk.resize((int(lk.width * k), ih), Image.LANCZOS)
    W = lk.width + 2 * pad + int(h * 0.12)
    b = Image.new("RGBA", (W, h), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    d.rounded_rectangle((0, 0, W - 1, h - 1), int(h * 0.22), fill=CREME + (255,))
    b.paste(lk, ((W - lk.width) // 2, pad))
    return b

if __name__ == "__main__":
    badge(140).save("/tmp/badge_h.png"); badge(400, "v").save("/tmp/badge_v.png")
