"""Visuel « choc » Campus Bourse : simple, concis, pro. 1 message + 1 preuve réelle zoomée + 1 bouton.
Usage : python3 -I outils/visuel_choc.py <choc.json> <dossier_sortie>
choc.json = liste de {
  "nom": "c01_alerte",
  "kicker": "MON PORTEFEUILLE",                 # petit sur-titre
  "titre": "Trop de *banques* dans ton portefeuille ?",   # ≤ 7 mots, *mot* = or
  "texte": "Campus Bourse te prévient au-delà de 35 % sur un secteur.",  # 1 phrase max
  "source": "campus-bourse/captures/sources/xxx.png", "crop": [x0,y0,x1,y1],   # capture RÉELLE, zoom serré
  "masquer": [[x0,y0,x1,y1]],                   # optionnel, coordonnées source
  "puces": ["Filtrer", "Comparer", ...]         # optionnel, si pas de capture (visuel texte)
  "cta": "Commence gratuitement"
}
Sorties : <nom>_fb.png 1080x1350, <nom>_tt.jpg 1080x1920, <nom>_carre.png 1080x1080
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from logo import badge
HERE = os.path.dirname(os.path.abspath(__file__))
def _f(n):
    for d in (os.path.join(HERE, "fonts"), "/usr/share/fonts/truetype/google-fonts"):
        p = os.path.join(d, n)
        if os.path.exists(p): return p
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
B, M, X = _f("Poppins-Bold.ttf"), _f("Poppins-Medium.ttf"), _f("Poppins-ExtraBold.ttf")
X = B
F = lambda p, s: ImageFont.truetype(p, s)
NUIT, FORET, EMER, OR, IVOIRE = (7, 24, 19), (12, 38, 31), (31, 138, 91), (232, 168, 62), (246, 241, 228)

def shot(c):
    im = Image.open(c["source"]).convert("RGB")
    for x0, y0, x1, y1 in c.get("masquer", []):
        r = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(16))
        im.paste(Image.blend(r, Image.new("RGB", r.size, FORET), .4), (x0, y0))
        d = ImageDraw.Draw(im); fs = max(14, min(30, (y1 - y0) // 2))
        lab = "🔒" if False else "Premium"; f = F(B, fs); w = d.textlength(lab, font=f)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.rounded_rectangle((cx - w/2 - 12, cy - fs*.75, cx + w/2 + 12, cy + fs*.75), 10, fill=OR)
        d.text((cx, cy), lab, font=f, fill=FORET, anchor="mm")
    return im.crop(tuple(c["crop"])) if c.get("crop") else im

def wrap(d, t, f, mw):
    L, cur = [], []
    for w in t.split(" "):
        if cur and d.textlength(" ".join(cur + [w]).replace("*", ""), font=f) > mw: L.append(cur); cur = [w]
        else: cur.append(w)
    return L + [cur]

def render(c, W, H, out):
    import numpy as np
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    g = np.clip(1 - np.hypot((xx - W*.85)/W, (yy - H*.05)/H) * 1.6, 0, 1)[..., None] * .55
    arr = np.array(NUIT) + (np.array(EMER) - np.array(NUIT)) * g
    bg = Image.fromarray(arr.astype("uint8"), "RGB")
    d = ImageDraw.Draw(bg, "RGBA"); m = 72
    # marque
    lg = badge(84); bg.paste(lg, (m, 52), lg); d = ImageDraw.Draw(bg, "RGBA")
    y = 172 if H > W else 160
    if c.get("kicker"):
        d.text((m, y), c["kicker"].upper(), font=F(B, 26), fill=OR); y += 52
    fs = 92 if H >= 1350 else 78
    fT = F(X, fs); hl = False
    for ln in wrap(d, c["titre"], fT, W - 2*m):
        x = m
        for w in ln:
            if w.startswith("*"): hl = True
            end = w.rstrip(".!?,:;»").endswith("*"); t = w.replace("*", "")
            d.text((x, y), t, font=fT, fill=OR if hl else IVOIRE)
            x += d.textlength(t + " ", font=fT)
            if end: hl = False
        y += int(fs * 1.12)
    if c.get("texte"):
        y += 26
        for ln in wrap(d, c["texte"], F(M, 34), W - 2*m):
            d.text((m, y), " ".join(ln), font=F(M, 34), fill=(246, 241, 228, 215)); y += 46
    foot = 230
    top, bot = y + 50, H - foot - 30
    st = c.get("stats", [])
    if c.get("source"):
        s = shot(c); mw = W - 2*m + 30
        mh = (bot - top) - (240 if st else 0)
        k = min(mw / s.width, mh / s.height); sw, sh = int(s.width*k), int(s.height*k)
        sx = (W - sw)//2
        sy = top + ((bot - top) - (sh + (240 if st else 0)))//2
        sl = Image.new("RGBA", (W, H)); ImageDraw.Draw(sl).rounded_rectangle((sx-6, sy+20, sx+sw+6, sy+sh+34), 28, fill=(0,0,0,170))
        sl = sl.filter(ImageFilter.GaussianBlur(26)); bg.paste(sl, (0, 0), sl)
        d = ImageDraw.Draw(bg, "RGBA")
        msk = Image.new("L", (sw, sh), 0); ImageDraw.Draw(msk).rounded_rectangle((0, 0, sw, sh), 24, fill=255)
        bg.paste(s.resize((sw, sh), Image.LANCZOS), (sx, sy), msk)
        d.rounded_rectangle((sx, sy, sx+sw, sy+sh), 24, outline=OR, width=3)
        if st:
            n = len(st); g = 20; tw = (W - 2*m - g*(n-1)) / n; ty = sy + sh + 40
            for i, t in enumerate(st):
                x0 = m + i*(tw + g)
                d.rounded_rectangle((x0, ty, x0 + tw, ty + 200), 26, fill=(255,255,255,16), outline=(232,168,62,120), width=2)
                col = {"rouge": (240, 96, 84), "vert": (60, 200, 130)}.get(t.get("couleur"), OR)
                fv = 72 if n <= 2 else (60 if n == 3 else 48)
                while d.textlength(t["v"], font=F(B, fv)) > tw - 30: fv -= 4
                d.text((x0 + tw/2, ty + 82), t["v"], font=F(B, fv), fill=col, anchor="mm")
                fl = F(M, 24 if n <= 3 else 21)
                lines = wrap(d, t["l"], fl, tw - 24)
                for j, ln in enumerate(lines[:2]):
                    d.text((x0 + tw/2, ty + 145 + j*28), " ".join(ln), font=fl, fill=(246,241,228,200), anchor="mm")
    elif c.get("puces"):
        n = len(c["puces"]); fb = F(B, 46); gap = 22
        bh = min(120, (bot - top - gap*(n-1)) // n); yy = top + ((bot - top) - (bh*n + gap*(n-1)))//2
        for i, p in enumerate(c["puces"]):
            d.rounded_rectangle((m, yy, W - m, yy + bh), 26, fill=(255, 255, 255, 18), outline=(232,168,62,140), width=2)
            d.ellipse((m + 28, yy + bh//2 - 30, m + 88, yy + bh//2 + 30), fill=OR)
            d.text((m + 58, yy + bh//2), str(i+1), font=F(X, 34), fill=FORET, anchor="mm")
            d.text((m + 120, yy + bh//2), p, font=fb, fill=IVOIRE, anchor="lm"); yy += bh + gap
    # CTA
    fc = F(B, 36); cta = c.get("cta", "Commence gratuitement"); cw = d.textlength(cta, font=fc) + 46
    cy = H - foot + 20
    d.rounded_rectangle((m, cy, m + cw + 70, cy + 84), 42, fill=OR)
    d.text((m + 35, cy + 42), cta, font=fc, fill=FORET, anchor="lm")
    ax = m + 35 + d.textlength(cta, font=fc) + 22
    d.line((ax, cy + 42, ax + 26, cy + 42), fill=FORET, width=5)
    d.polygon([(ax + 30, cy + 42), (ax + 16, cy + 31), (ax + 16, cy + 53)], fill=FORET)
    d.text((W - m, cy + 42), "campusbourse.com", font=F(B, 32), fill=IVOIRE, anchor="rm")
    d.text((m, H - 62), "Outil d'aide à l'analyse. Pas un conseil en investissement.", font=F(M, 22), fill=(246, 241, 228, 150))
    bg.save(out, quality=93) if out.endswith(".jpg") else bg.save(out, optimize=True)

if __name__ == "__main__":
    L = json.load(open(sys.argv[1], encoding="utf-8")); od = sys.argv[2]
    for c in L:
        dd = os.path.join(od, c["nom"]); os.makedirs(dd, exist_ok=True)
        for W, H, suf in ((1080, 1350, "_fb.png"), (1080, 1920, "_tt.jpg"), (1080, 1080, "_carre.png")):
            render(c, W, H, os.path.join(dd, c["nom"] + suf))
        print("ok", c["nom"])
