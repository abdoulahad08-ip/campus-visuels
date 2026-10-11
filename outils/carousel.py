"""Génère un carrousel Campus des Bâtisseurs.
Usage: python3 carousel.py slides.json outdir
slides.json = {"slides":[{"label":"LA RÈGLE DU JOUR","title":"...","body":"..."}, ...]}
Produit fb_01.png... (1080x1350) et tt_01.png... (1080x1920).
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

BG = (11, 11, 11)
GOLD = (201, 162, 39)
WHITE = (245, 245, 240)
GREY = (150, 150, 145)
FD = "/usr/share/fonts/truetype/google-fonts/"
F_BOLD = FD + "Poppins-Bold.ttf"
F_SEMI = FD + "Poppins-SemiBold.ttf" if os.path.exists(FD + "Poppins-SemiBold.ttf") else F_BOLD
F_REG = FD + "Poppins-Regular.ttf"


def font(p, s):
    return ImageFont.truetype(p, s)


def wrap(draw, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        cur = ""
        for w in [x for x in para.split(" ") if x]:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def brick(draw, x, y, s, color):
    # petit mur de briques : 2 rangées décalées
    w, h, g = s, s // 2, max(3, s // 10)
    draw.rectangle([x, y, x + w - g, y + h - g], fill=color)
    draw.rectangle([x + w, y, x + 2 * w - g, y + h - g], fill=color)
    draw.rectangle([x, y + h, x + w // 2 - g, y + 2 * h - g], fill=color)
    draw.rectangle([x + w // 2, y + h, x + w // 2 + w - g, y + 2 * h - g], fill=color)
    draw.rectangle([x + w // 2 + w, y + h, x + 2 * w - g, y + 2 * h - g], fill=color)


F_SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def text_fb(draw, xy, txt, f, fill):
    """Dessine le texte ; les flèches → passent par DejaVu (absentes de Poppins)."""
    x, y = xy
    parts = txt.split("→")
    sym = font(F_SYM, int(f.size * 0.85))
    for i, part in enumerate(parts):
        draw.text((x, y), part, font=f, fill=fill)
        x += draw.textlength(part, font=f)
        if i < len(parts) - 1:
            draw.text((x, y + int(f.size * 0.12)), "→", font=sym, fill=GOLD)
            x += draw.textlength("→", font=sym)


def fit_block(draw, title, body, maxw, maxh, tsize, bsize):
    while True:
        ft, fb = font(F_BOLD, tsize), font(F_REG, bsize)
        tl = wrap(draw, title, ft, maxw) if title else []
        bl = wrap(draw, body, fb, maxw) if body else []
        th = len(tl) * int(tsize * 1.18)
        bh = len(bl) * int(bsize * 1.45)
        gap = 50 if (tl and bl) else 0
        if th + gap + bh <= maxh or tsize <= 60:
            return ft, fb, tl, bl, th, gap, bh, tsize, bsize
        tsize = int(tsize * 0.93)
        bsize = max(40, int(bsize * 0.95))


def render(slide, idx, total, W, H, path):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    M = 90
    maxw = W - 2 * M
    # cadre fin doré
    d.rectangle([40, 40, W - 40, H - 40], outline=(60, 50, 20), width=2)
    # label
    top = 150 if H > 1500 else 120
    fl = font(F_BOLD, 34)
    label = slide.get("label", "")
    if label:
        d.rectangle([M, top, M + 70, top + 6], fill=GOLD)
        d.text((M, top + 30), label.upper(), font=fl, fill=GOLD)
    # zone de contenu
    ctop = top + 130
    cbot = H - 230
    big = slide.get("big", False)
    ft, fb, tl, bl, th, gap, bh, ts, bs = fit_block(
        d, slide.get("title", ""), slide.get("body", ""), maxw, cbot - ctop,
        110 if big else 84, 48)
    y = ctop + max(0, ((cbot - ctop) - (th + gap + bh)) // 2)
    for ln in tl:
        d.text((M, y), ln, font=ft, fill=GOLD if slide.get("gold_title", True) else WHITE)
        y += int(ts * 1.18)
    y += gap
    for ln in bl:
        text_fb(d, (M, y), ln, fb, WHITE)
        y += int(bs * 1.45)
    # pied de page
    fy = H - 140
    ff = font(F_BOLD, 32)
    name = "Campus des Bâtisseurs"
    nw = d.textlength(name, font=ff)
    d.text((W - M - nw, fy), name, font=ff, fill=WHITE)
    brick(d, int(W - M - nw - 92), fy + 6, 34, GOLD)
    d.text((M, fy), f"{idx}/{total}", font=font(F_REG, 32), fill=GREY)
    if idx < total:
        arrow = "→"
        d.text((M + 90, fy - 2), arrow, font=font(F_SYM, 34), fill=GOLD)
    im.save(path, optimize=True)


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    slides = data["slides"]
    n = len(slides)
    for i, s in enumerate(slides, 1):
        render(s, i, n, 1080, 1350, os.path.join(out, f"fb_{i:02d}.png"))
        render(s, i, n, 1080, 1920, os.path.join(out, f"tt_{i:02d}.png"))
    print("ok", n)


if __name__ == "__main__":
    main()
