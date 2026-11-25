"""Visuel « Preuve produit » Campus Bourse : une VRAIE capture du site mise en scène.

Usage : python3 -I outils/capture_cadre.py <dossier>/capture.json <dossier>
-> <nom>_fb.png (1080x1350, Facebook/LinkedIn), <nom>_tt.jpg (1080x1920, TikTok), <nom>_carre.png (1080x1080)

capture.json = {
  "nom": "capture_01",
  "source": "campus-bourse/captures/fiche-xxx.png",  # capture RÉELLE fournie par l'utilisateur, jamais générée
  "crop": [x0, y0, x1, y1],          # optionnel : zone utile de la capture (zoom sur 2-3 indicateurs max)
  "masquer": [[x0, y0, x1, y1]],     # zones floutées (pixels de la capture source) : statut, note, badge,
                                     # prix sécurisé, projections... d'une société NOMMÉE = TOUJOURS masqués
  "etiquette_masque": "Réservé Premium",
  "tag": "Preuve produit",
  "titre": "3 chiffres à lire *avant de décider*",   # 1 ou 2 mots *surlignés* en or
  "sous_titre": "Fiche société Campus Bourse"         # optionnel
}
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
def _f(n):
    for d in (os.path.join(HERE, "fonts"), "/usr/share/fonts/truetype/google-fonts"):
        p = os.path.join(d, n)
        if os.path.exists(p): return p
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
B, M = _f("Poppins-Bold.ttf"), _f("Poppins-Medium.ttf")
FORET, NUIT, EMER, OR, IVOIRE = (14,42,35), (8,26,21), (31,138,91), (227,162,59), (244,238,223)

def F(p, s): return ImageFont.truetype(p, s)

def prepare(cfg):
    im = Image.open(cfg["source"]).convert("RGB")
    for box in cfg.get("masquer", []):
        x0, y0, x1, y1 = box
        reg = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(18))
        ov = Image.new("RGB", reg.size, FORET)
        reg = Image.blend(reg, ov, 0.35)
        im.paste(reg, (x0, y0))
        d = ImageDraw.Draw(im)
        lab = cfg.get("etiquette_masque", "Réservé Premium")
        fs = max(14, min(40, (y1 - y0) // 2)); lab0 = lab
        while fs > 14 and d.textlength(lab, font=F(B, fs)) > (x1 - x0) - 36: fs -= 2
        if d.textlength(lab, font=F(B, fs)) > (x1 - x0) - 36: lab = "Premium"
        f = F(B, fs); w = d.textlength(lab, font=f); lab = lab if lab else lab0
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.rounded_rectangle((cx - w / 2 - 14, cy - fs * 0.8, cx + w / 2 + 14, cy + fs * 0.8), 12, fill=OR)
        d.text((cx, cy), lab, font=f, fill=FORET, anchor="mm")
    if cfg.get("empiler"):  # plusieurs zones empilées verticalement (captures très larges)
        parts = [im.crop(tuple(b)) for b in cfg["empiler"]]; g = 24
        W = max(p.width for p in parts); H = sum(p.height for p in parts) + g * (len(parts) - 1)
        out = Image.new("RGB", (W, H), (12, 30, 25)); y = 0
        for p in parts: out.paste(p, ((W - p.width) // 2, y)); y += p.height + g
        return out
    if cfg.get("crop"):
        im = im.crop(tuple(cfg["crop"]))
    return im

def title_lines(d, title, f, maxw):
    words = title.split(" "); lines, cur = [], []
    for w in words:
        t = " ".join(cur + [w]).replace("*", "")
        if d.textlength(t, font=f) > maxw and cur: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur); return lines

def render(cfg, shot, W, H, out):
    bg = Image.new("RGB", (W, H), FORET)
    px = bg.load()
    for y in range(H):
        t = y / H
        c = tuple(int(EMER[i] * (1 - t) * 0.55 + FORET[i] * (0.45 + t * 0.2) + NUIT[i] * t * 0.35) for i in range(3))
        for x in range(W): px[x, y] = c
    d = ImageDraw.Draw(bg, "RGBA")
    m = 60
    # tag
    ft = F(B, 28); tag = cfg.get("tag", "Preuve produit").upper(); tw = d.textlength(tag, font=ft)
    d.rounded_rectangle((m, 70, m + tw + 44, 122), 26, fill=OR); d.text((m + 22, 80), tag, font=ft, fill=FORET)
    # titre
    fT = F(B, 62 if W == H else 68); y = 150; hl = False
    for ln in title_lines(d, cfg["titre"], fT, W - 2 * m):
        x = m; segs = []
        for w in ln:
            if w.startswith("*"): hl = True
            end = w.rstrip(".!?,:;»").endswith("*")
            txt = w.replace("*", "")
            if segs and segs[-1][1] == hl: segs[-1][0] += " " + txt
            else: segs.append([txt, hl])
            if end: hl = False
        for txt, h in segs:
            ww = d.textlength(txt, font=fT)
            if h:
                d.rounded_rectangle((x - 8, y + 10, x + ww + 8, y + fT.size + 12), 10, fill=OR); d.text((x, y), txt, font=fT, fill=FORET)
            else:
                d.text((x, y), txt, font=fT, fill=IVOIRE)
            x += ww + d.textlength(" ", font=fT)
        y += int(fT.size * 1.22)
    if cfg.get("sous_titre"):
        d.text((m, y + 12), cfg["sous_titre"], font=F(M, 30), fill=(244, 238, 223, 200)); y += 58
    # zone capture : cadre navigateur
    top = y + 30; bottom = H - 150
    bar = 46
    maxw, maxh = W - 2 * m, bottom - top - bar
    s = min(maxw / shot.width, maxh / shot.height)
    sw, sh = int(shot.width * s), int(shot.height * s)
    fx = (W - sw) // 2; fy = top + (maxh - sh) // 2
    sh_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh_layer)
    sd.rounded_rectangle((fx + 10, fy + 18, fx + sw + 10, fy + bar + sh + 18), 22, fill=(0, 0, 0, 120))
    bg.paste(sh_layer.filter(ImageFilter.GaussianBlur(18)), (0, 0), sh_layer.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(bg, "RGBA")
    d.rounded_rectangle((fx, fy, fx + sw, fy + bar + sh), 18, fill=(236, 236, 236))
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((fx + 20 + i * 26, fy + 15, fx + 36 + i * 26, fy + 31), fill=col)
    d.rounded_rectangle((fx + 110, fy + 10, fx + sw - 20, fy + 36), 13, fill=(255, 255, 255))
    d.text((fx + 126, fy + 23), "campusbourse.com", font=F(M, 18), fill=(90, 90, 90), anchor="lm")
    bg.paste(shot.resize((sw, sh), Image.LANCZOS), (fx, fy + bar))
    # pied
    d.text((m, H - 118), "CAMPUS BOURSE", font=F(B, 30), fill=OR)
    d.text((W - m, H - 118), "campusbourse.com", font=F(B, 30), fill=IVOIRE, anchor="ra")
    d.text((W // 2, H - 38), "Outil d'aide à l'analyse. Pas un conseil en investissement.", font=F(M, 20), fill=(244, 238, 223, 160), anchor="mm")
    bg.save(out, quality=92) if out.endswith(".jpg") else bg.save(out, optimize=True)

def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8")); outd = sys.argv[2]; os.makedirs(outd, exist_ok=True)
    shot = prepare(cfg); n = cfg.get("nom", "capture")
    render(cfg, shot, 1080, 1350, os.path.join(outd, n + "_fb.png"))
    render(cfg, shot, 1080, 1920, os.path.join(outd, n + "_tt.jpg"))
    render(cfg, shot, 1080, 1080, os.path.join(outd, n + "_carre.png"))
    print("ok", n)

if __name__ == "__main__":
    main()
