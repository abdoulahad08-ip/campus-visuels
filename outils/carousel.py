"""Carrousel Campus des Bâtisseurs — v2 (couleurs vives, orienté solution).

Usage : python3 -I outils/carousel.py AAAA-MM-JJ/slides.json AAAA-MM-JJ
Produit fb_01.png… (1080x1350, Facebook) et tt_01.jpg… (1080x1920, TikTok — JPEG obligatoire).

slides.json = {"slides": [ {"type": "...", "tag": "...", "title": "...", "body": "...", "big": "..."}, ... ]}
Types (un par diapo, dans cet ordre conseillé) :
  curiosite  -> accroche qui intrigue (diapo 1)
  probleme   -> le piège / la vraie cause
  solution   -> une étape concrète (tag ex. « Solution 1/3 »)
  promesse   -> ce que la personne va obtenir
  resultat   -> le résultat chiffré ; "big" = gros chiffre (ex. « 180 000 FCFA »)
  cta        -> appel à l'action ; "big" = « campusdesbatisseurs.com »
Clé optionnelle "story" (même format qu'une diapo, type conseillé « curiosite ») :
  génère story.png (1080x1920) pour la story Facebook, avec « Suis le Campus : dans quelques mois, tu verras la différence. ».
Clé optionnelle "cover" (même format) : visuel UNIQUE des posts « liste valeur » de 10h
  -> cover_fb.png (1080x1350) et cover_tt.jpg (1080x1920, JPEG pour TikTok), sans points de progression.
  Texte total de la story (tag + title + body) ≤ 100 caractères.
Dans "title", entoure un ou deux mots avec *étoiles* pour les surligner.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = [os.path.join(HERE, "fonts"), "/usr/share/fonts/truetype/google-fonts"]


def _f(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


F_BOLD = _f("Poppins-Bold.ttf")
F_MED = _f("Poppins-Medium.ttf")
F_SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(F_SYM):
    F_SYM = F_BOLD

WHITE = (255, 255, 255)
DARK = (20, 20, 35)
YELLOW = (255, 214, 0)

# type -> (couleur haut, couleur bas, couleur texte, couleur surlignage, texte surligné, icône, tag par défaut)
THEMES = {
    "curiosite": ((255, 94, 20), (255, 30, 110), WHITE, YELLOW, DARK, "?", "Tu savais ?"),
    "probleme": ((24, 32, 72), (52, 20, 90), WHITE, (255, 70, 90), WHITE, "!", "Le piège"),
    "solution": ((0, 168, 120), (0, 120, 190), WHITE, YELLOW, DARK, "✓", "La solution"),
    "promesse": ((110, 40, 220), (40, 100, 240), WHITE, YELLOW, DARK, "★", "La promesse"),
    "resultat": ((255, 200, 0), (255, 140, 0), DARK, WHITE, DARK, "↗", "Le résultat"),
    "cta": ((255, 30, 110), (255, 94, 20), WHITE, YELLOW, DARK, "→", "À toi de jouer"),
}


def font(p, s):
    return ImageFont.truetype(p, s)


def gradient(W, H, c1, c2):
    base = Image.new("RGB", (W, H), c1)
    top = Image.new("RGB", (W, H), c2)
    mask = Image.linear_gradient("L").resize((W, H))
    return Image.composite(top, base, mask)


def tokens(title):
    """Découpe le titre en mots (texte, surligné?)."""
    out, hl = [], False
    for raw in [w for w in title.split(" ") if w]:
        w = raw
        start = w.startswith("*")
        if start:
            hl = True
            w = w[1:]
        end = w.endswith("*") or w.endswith("*,") or w.endswith("*.") or w.endswith("*!") or w.endswith("*?")
        w = w.replace("*", "")
        out.append((w, hl))
        if end:
            hl = False
    return out


def layout_title(d, title, f, maxw):
    lines, cur, curw = [], [], 0
    sp = d.textlength(" ", font=f)
    for w, hl in tokens(title):
        ww = d.textlength(w, font=f)
        if cur and curw + sp + ww > maxw:
            lines.append(cur)
            cur, curw = [], 0
        cur.append((w, hl, ww))
        curw += (sp if len(cur) > 1 else 0) + ww
    if cur:
        lines.append(cur)
    return lines


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in [x for x in para.split(" ") if x]:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def brick(d, x, y, s, color):
    w, h, g = s, s // 2, max(3, s // 10)
    d.rectangle([x, y, x + w - g, y + h - g], fill=color)
    d.rectangle([x + w, y, x + 2 * w - g, y + h - g], fill=color)
    d.rectangle([x, y + h, x + w // 2 - g, y + 2 * h - g], fill=color)
    d.rectangle([x + w // 2, y + h, x + w // 2 + w - g, y + 2 * h - g], fill=color)
    d.rectangle([x + w // 2 + w, y + h, x + 2 * w - g, y + 2 * h - g], fill=color)


def text_sym(d, xy, txt, f, fill):
    """Texte Poppins ; les symboles absents de Poppins (→ ✓ ★) passent par DejaVu."""
    x, y = xy
    sym = font(F_SYM, int(f.size * 0.9))
    buf = ""
    for ch in txt + "\0":
        if ch in "→✓★↗" or ch == "\0":
            if buf:
                d.text((x, y), buf, font=f, fill=fill)
                x += d.textlength(buf, font=f)
                buf = ""
            if ch != "\0":
                d.text((x, y + int(f.size * 0.08)), ch, font=sym, fill=fill)
                x += d.textlength(ch, font=sym)
        else:
            buf += ch


def centered(d, cx, y, txt, f, fill):
    w = d.textlength(txt, font=f)
    d.text((cx - w / 2, y), txt, font=f, fill=fill)


def save(im, path):
    """PNG pour Facebook ; JPEG obligatoire pour les photos TikTok (Metricool refuse le PNG)."""
    if path.endswith(".jpg"):
        im.convert("RGB").save(path, "JPEG", quality=92, optimize=True)
    else:
        im.save(path, optimize=True)


def render(s, idx, total, W, H, path):
    typ = s.get("type", "solution")
    c1, c2, tc, hlc, hltc, icon, deftag = THEMES.get(typ, THEMES["solution"])
    im = gradient(W, H, c1, c2)
    d = ImageDraw.Draw(im, "RGBA")
    M = 80
    maxw = W - 2 * M
    tall = H > 1500

    # formes décoratives douces
    d.ellipse([W - 330, -170, W + 170, 330], fill=(255, 255, 255, 28))
    d.ellipse([-200, H - 420, 260, H + 40], fill=(255, 255, 255, 22))

    # tag en pastille + icône
    top = (260 if total == 0 else 170) if tall else 110
    ftag = font(F_BOLD, 36)
    tag = s.get("tag") or deftag
    tag = tag.upper()
    tw = d.textlength(tag, font=ftag)
    pill_bg = (255, 255, 255, 235) if tc == WHITE else (20, 20, 35, 235)
    pill_fg = c1 if tc == WHITE else WHITE
    d.rounded_rectangle([M, top, M + tw + 60, top + 70], radius=35, fill=pill_bg)
    d.text((M + 30, top + 13), tag, font=ftag, fill=pill_fg)
    # icône ronde à droite
    r = 60
    cx, cy = W - M - r, top + 35
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=pill_bg)
    fi = font(F_SYM if icon in "✓★↗→" else F_BOLD, 64)
    iw = d.textlength(icon, font=fi)
    bb = d.textbbox((0, 0), icon, font=fi)
    d.text((cx - iw / 2, cy - (bb[1] + bb[3]) / 2), icon, font=fi, fill=pill_fg)

    # zone de contenu
    ctop = top + 140
    cbot = H - ((400 if total == 0 else 230) if tall else 190)
    title = s.get("title", "")
    body = s.get("body", "")
    big = s.get("big", "")

    tsize = 104 if typ == "curiosite" else 86
    while True:
        ft = font(F_BOLD, tsize)
        fb = font(F_MED, max(42, int(tsize * 0.52)))
        fbig = font(F_BOLD, int(tsize * 1.25))
        tl = layout_title(d, title, ft, maxw) if title else []
        bl = wrap(d, body, fb, maxw) if body else []
        lh = int(tsize * 1.25)
        bigh = 0
        if big:
            bw = d.textlength(big, font=fbig)
            while bw > maxw - 60:
                fbig = font(F_BOLD, int(fbig.size * 0.9))
                bw = d.textlength(big, font=fbig)
            bigh = int(fbig.size * 1.5) + 50
        th = len(tl) * lh
        bh = len(bl) * int(fb.size * 1.45)
        total_h = th + (40 if bl else 0) + bh + bigh
        if total_h <= cbot - ctop or tsize <= 58:
            break
        tsize = int(tsize * 0.93)

    y = ctop + max(0, (cbot - ctop - total_h) // 2)
    sp = d.textlength(" ", font=ft)
    for line in tl:
        x = M
        prev_hl = False
        for w, hl, ww in line:
            if hl and not prev_hl and x > M:
                x += 14
            if not hl and prev_hl:
                x += 14
            prev_hl = hl
            if hl:
                d.rounded_rectangle([x - 12, y + int(tsize * 0.08), x + ww + 12, y + int(tsize * 1.2)],
                                    radius=14, fill=hlc)
                d.text((x, y), w, font=ft, fill=hltc)
            else:
                d.text((x, y), w, font=ft, fill=tc)
            x += ww + sp
        y += lh
    if bl:
        y += 40
        for ln in bl:
            text_sym(d, (M, y), ln, fb, tc)
            y += int(fb.size * 1.45)
    if big:
        y += 50
        bw = d.textlength(big, font=fbig)
        bh2 = int(fbig.size * 1.5)
        box_bg = DARK if typ == "resultat" else WHITE
        box_fg = YELLOW if typ == "resultat" else c1
        d.rounded_rectangle([M, y, M + bw + 60, y + bh2], radius=bh2 // 2, fill=box_bg)
        bb = d.textbbox((0, 0), big, font=fbig)
        d.text((M + 30, y + (bh2 - (bb[1] + bb[3])) / 2), big, font=fbig, fill=box_fg)

    # pied : marque + progression
    fy = H - (150 if tall else 120)
    ff = font(F_BOLD, 32)
    name = "Campus des Bâtisseurs"
    nw = d.textlength(name, font=ff)
    d.text((W - M - nw, fy), name, font=ff, fill=tc)
    brick(d, int(W - M - nw - 88), fy + 6, 32, tc)
    if total == 0:  # story : message communauté (pas d'« abonne-toi »)
        fs = font(F_BOLD, 40)
        lines2 = ["Suis le Campus : dans quelques mois,", "tu verras la différence."]
        lh2 = 54
        tw2 = max(d.textlength(t, font=fs) for t in lines2)
        py = fy - 60 - lh2 * len(lines2) - 40
        bg = WHITE if tc == WHITE else DARK
        fg = c1 if tc == WHITE else YELLOW
        d.rounded_rectangle([(W - tw2) / 2 - 40, py, (W + tw2) / 2 + 40, py + lh2 * len(lines2) + 40], radius=40, fill=bg)
        for k, t in enumerate(lines2):
            d.text(((W - d.textlength(t, font=fs)) / 2, py + 18 + k * lh2), t, font=fs, fill=fg)
    # points de progression
    x = M
    for i in range(max(total, 0)):
        on = i + 1 == idx
        col = tc if on else (tc + (90,))
        wdot = 44 if on else 18
        d.rounded_rectangle([x, fy + 14, x + wdot, fy + 32], radius=9, fill=col)
        x += wdot + 12
    save(im, path)


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    slides = data.get("slides", [])
    n = len(slides)
    for i, s in enumerate(slides, 1):
        render(s, i, n, 1080, 1350, os.path.join(out, f"fb_{i:02d}.png"))
        render(s, i, n, 1080, 1920, os.path.join(out, f"tt_{i:02d}.jpg"))
    if data.get("cover"):
        render(data["cover"], 0, -1, 1080, 1350, os.path.join(out, "cover_fb.png"))
        render(data["cover"], 0, -1, 1080, 1920, os.path.join(out, "cover_tt.jpg"))
        print("cover ok")
    if data.get("story"):
        render(data["story"], 0, 0, 1080, 1920, os.path.join(out, "story.png"))
        print("story ok")
    print("ok", n)


if __name__ == "__main__":
    main()
