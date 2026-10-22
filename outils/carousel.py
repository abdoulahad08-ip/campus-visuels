"""Carrousel Campus des Bâtisseurs — v3 (charte couleur officielle du 22 oct 2026).

Palette : vert forêt #0E2A23 (principale) · or doré #E3A23B (accent) · ivoire #F4EEDF (claire)
+ couleurs « qui captent » en touche : corail #FF6B57, turquoise #2EC4B6, émeraude #1F8A5B.

Usage : python3 -I outils/carousel.py AAAA-MM-JJ/slides.json AAAA-MM-JJ
Produit fb_01.png… (1080x1350, Facebook/LinkedIn) et tt_01.jpg… (1080x1920, TikTok — JPEG obligatoire).

slides.json = {"slides": [ {"type": "...", "tag": "...", "title": "...", "body": "...", "big": "..."}, ... ]}
Types (un par diapo) :
  curiosite  -> accroche (diapo 1) : fond vert forêt, mots surlignés en or
  probleme   -> le piège : fond vert très sombre, touche corail
  solution   -> une étape concrète : fond ivoire, texte vert, surlignage or (accent qui varie : or/turquoise/corail)
  promesse   -> ce que la personne va obtenir : fond émeraude → vert forêt
  resultat   -> le résultat ; "big" = gros chiffre : fond or, texte vert
  marque     -> visuel de marque (story, question du soir) : vert forêt + motif briques
  cta        -> dernière diapo ; "big" = « @campusdesbatisseurs » : vert forêt, grosse pastille or
Option "theme": "ivoire" | "foret" | "or" | "corail" | "turquoise" pour forcer un fond (variété).
Clé optionnelle "cover" : visuel unique -> cover_fb.png (1080x1350) et cover_tt.jpg (1080x1920).
Clé optionnelle "story" : story.png (1080x1920).
Dans "title", entoure un ou deux mots avec *étoiles* pour les surligner.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

# --- Charte officielle -------------------------------------------------------
FORET = (14, 42, 35)        # #0E2A23 principale
FORET2 = (22, 61, 50)       # variante plus claire pour dégradés
NUIT = (8, 26, 21)          # variante plus sombre
OR = (227, 162, 59)         # #E3A23B accent
OR2 = (240, 186, 96)
IVOIRE = (244, 238, 223)    # #F4EEDF claire
# --- Touches vives (à petite dose) ------------------------------------------
CORAIL = (255, 107, 87)
TURQUOISE = (46, 196, 182)
EMERAUDE = (31, 138, 91)

# fond haut, fond bas, texte, texte secondaire, fond surlignage, texte surligné, accent, icône, tag par défaut
THEMES = {
    "curiosite": (FORET, NUIT, IVOIRE, (244, 238, 223, 210), OR, FORET, OR, "?", "Tu savais ?"),
    "probleme": (NUIT, (40, 22, 20), IVOIRE, (244, 238, 223, 210), CORAIL, NUIT, CORAIL, "!", "Le piège"),
    "solution": (IVOIRE, (236, 227, 204), FORET, (14, 42, 35, 200), OR, FORET, EMERAUDE, "✓", "La solution"),
    "promesse": (EMERAUDE, FORET, IVOIRE, (244, 238, 223, 215), OR, FORET, OR, "★", "La promesse"),
    "resultat": (OR2, OR, FORET, (14, 42, 35, 210), FORET, OR2, FORET, "↗", "Le résultat"),
    "marque": (FORET, NUIT, IVOIRE, (244, 238, 223, 215), OR, FORET, OR, "★", "Connecter • Accompagner • Bâtir"),
    "cta": (FORET2, FORET, IVOIRE, (244, 238, 223, 215), OR, FORET, OR, "→", "À toi de jouer"),
}
# fonds forcés (clé "theme")
FORCED = {
    "foret": (FORET, NUIT, IVOIRE, (244, 238, 223, 210), OR, FORET, OR),
    "ivoire": (IVOIRE, (236, 227, 204), FORET, (14, 42, 35, 200), OR, FORET, EMERAUDE),
    "or": (OR2, OR, FORET, (14, 42, 35, 210), FORET, OR2, FORET),
    "corail": (CORAIL, (232, 80, 64), IVOIRE, (244, 238, 223, 225), FORET, IVOIRE, FORET),
    "turquoise": (TURQUOISE, (20, 150, 140), FORET, (14, 42, 35, 215), FORET, IVOIRE, FORET),
}
SOLUTION_ACCENTS = [EMERAUDE, TURQUOISE, CORAIL]


def font(p, s):
    return ImageFont.truetype(p, s)


def gradient(W, H, c1, c2):
    base = Image.new("RGB", (W, H), c1)
    top = Image.new("RGB", (W, H), c2)
    mask = Image.linear_gradient("L").resize((W, H))
    return Image.composite(top, base, mask)


def is_dark(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) < 140


def tokens(title):
    out, hl = [], False
    for raw in [w for w in title.split(" ") if w]:
        w = raw
        if w.startswith("*") or w.startswith("«*") or w.startswith("(*"):
            hl = True
        end = w.rstrip(".,!?:;»)…").endswith("*")
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
    """Logo brique (3 rangs) du Campus."""
    w, h, g = s, s // 2, max(3, s // 10)
    d.rectangle([x, y, x + w - g, y + h - g], fill=color)
    d.rectangle([x + w, y, x + 2 * w - g, y + h - g], fill=color)
    d.rectangle([x, y + h, x + w // 2 - g, y + 2 * h - g], fill=color)
    d.rectangle([x + w // 2, y + h, x + w // 2 + w - g, y + 2 * h - g], fill=color)
    d.rectangle([x + w // 2 + w, y + h, x + 2 * w - g, y + 2 * h - g], fill=color)


def brick_wall(im, x0, y0, x1, y1, color, alpha):
    """Motif de briques très léger (texture de marque)."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bw, bh, g = 120, 52, 8
    row = 0
    y = y0
    while y < y1:
        off = (bw // 2) if row % 2 else 0
        x = x0 - off
        while x < x1:
            d.rounded_rectangle([x, y, x + bw - g, y + bh - g], radius=6, outline=color + (alpha,), width=3)
            x += bw
        y += bh
        row += 1
    im.alpha_composite(layer)


def glow(im, cx, cy, r, color, alpha):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(r // 2))
    im.alpha_composite(layer)


def text_sym(d, xy, txt, f, fill):
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


def save(im, path):
    im = im.convert("RGB")
    if path.endswith(".jpg"):
        im.save(path, "JPEG", quality=93, optimize=True)
    else:
        im.save(path, optimize=True)


def render(s, idx, total, W, H, path):
    typ = s.get("type", "solution")
    t = THEMES.get(typ, THEMES["solution"])
    c1, c2, tc, tc2, hlbg, hlfg, acc, icon, deftag = t
    if s.get("theme") in FORCED:
        c1, c2, tc, tc2, hlbg, hlfg, acc = FORCED[s["theme"]]
    if typ == "solution" and "theme" not in s and idx > 0:
        acc = SOLUTION_ACCENTS[(idx - 1) % len(SOLUTION_ACCENTS)]
    dark = is_dark(c1)

    im = gradient(W, H, c1, c2).convert("RGBA")
    # texture et lumières de marque
    if dark:
        glow(im, W - 120, 160, 260, OR, 46)
        glow(im, 80, H - 200, 300, acc if acc != OR else EMERAUDE, 40)
        brick_wall(im, W - 520, H - 520, W + 60, H + 60, OR, 26)
    else:
        brick_wall(im, W - 520, H - 520, W + 60, H + 60, FORET, 20)
    d = ImageDraw.Draw(im, "RGBA")
    M = 84
    maxw = W - 2 * M
    tall = H > 1500
    gold_line = OR if dark or c1 == IVOIRE else FORET

    # bande d'accent verticale à gauche
    d.rectangle([0, 0, 16, H], fill=acc)

    # haut : tag + compteur
    top = (250 if total == 0 else 170) if tall else 104
    ftag = font(F_BOLD, 34)
    tag = (s.get("tag") or deftag).upper()
    tw = d.textlength(tag, font=ftag)
    if dark:
        pill_bg, pill_fg = OR, FORET
    elif c1 in (OR2, OR):
        pill_bg, pill_fg = FORET, OR2
    else:
        pill_bg, pill_fg = FORET, IVOIRE
    d.rounded_rectangle([M, top, M + tw + 56, top + 66], radius=33, fill=pill_bg)
    d.text((M + 28, top + 12), tag, font=ftag, fill=pill_fg)
    if total > 0:
        fc = font(F_BOLD, 34)
        cnt = f"{idx:02d} / {total:02d}"
        cw = d.textlength(cnt, font=fc)
        d.text((W - M - cw, top + 13), cnt, font=fc, fill=tc2)
    else:
        r = 40
        cx, cy = W - M - r, top + 33
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=acc, width=5)
        fi = font(F_SYM if icon in "✓★↗→" else F_BOLD, 44)
        bb = d.textbbox((0, 0), icon, font=fi)
        d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), icon, font=fi, fill=acc)

    # zone de contenu
    ctop = top + 150
    cbot = H - ((420 if total == 0 else 250) if tall else 200)
    title, body, big = s.get("title", ""), s.get("body", ""), s.get("big", "")

    tsize = 112 if typ in ("curiosite", "marque") else 90
    while True:
        ft = font(F_BOLD, tsize)
        fb = font(F_MED, max(40, int(tsize * 0.5)))
        fbig = font(F_BOLD, int(tsize * 1.3))
        tl = layout_title(d, title, ft, maxw) if title else []
        bl = wrap(d, body, fb, maxw) if body else []
        lh = int(tsize * 1.2)
        bigh = 0
        if big:
            bw = d.textlength(big, font=fbig)
            while bw > maxw - 70:
                fbig = font(F_BOLD, int(fbig.size * 0.9))
                bw = d.textlength(big, font=fbig)
            bigh = int(fbig.size * 1.55) + 56
        th = len(tl) * lh
        bh = len(bl) * int(fb.size * 1.45)
        total_h = th + (70 if bl else 0) + bh + bigh
        if total_h <= cbot - ctop or tsize <= 56:
            break
        tsize = int(tsize * 0.93)

    y = ctop + max(0, (cbot - ctop - total_h) // 2)
    sp = d.textlength(" ", font=ft)
    for line in tl:
        x = M
        prev_hl = False
        for w, hl, ww in line:
            if hl and not prev_hl and x > M:
                x += 10
            if not hl and prev_hl:
                x += 10
            prev_hl = hl
            if hl:
                # surligneur décalé (effet marqueur)
                d.rounded_rectangle([x - 12, y + int(tsize * 0.30), x + ww + 12, y + int(tsize * 1.16)],
                                    radius=10, fill=hlbg)
                d.text((x, y), w, font=ft, fill=hlfg)
            else:
                d.text((x, y), w, font=ft, fill=tc)
            x += ww + sp
        y += lh
    if bl:
        y += 26
        d.rectangle([M, y, M + 120, y + 8], fill=acc)
        y += 44
        for ln in bl:
            text_sym(d, (M, y), ln, fb, tc2)
            y += int(fb.size * 1.45)
    if big:
        y += 56
        bw = d.textlength(big, font=fbig)
        bh2 = int(fbig.size * 1.55)
        if typ == "resultat" or c1 in (OR2, OR):
            box_bg, box_fg = FORET, OR2
        elif dark:
            box_bg, box_fg = OR, FORET
        else:
            box_bg, box_fg = FORET, OR
        d.rounded_rectangle([M + 10, y + 10, M + bw + 80, y + bh2 + 10], radius=26, fill=(0, 0, 0, 60))
        d.rounded_rectangle([M, y, M + bw + 70, y + bh2], radius=26, fill=box_bg)
        bb = d.textbbox((0, 0), big, font=fbig)
        d.text((M + 35, y + (bh2 - (bb[1] + bb[3])) / 2), big, font=fbig, fill=box_fg)

    # pied : filet or, logo, progression
    fy = H - (160 if tall else 124)
    d.rectangle([M, fy - 30, W - M, fy - 27], fill=gold_line + (170,))
    ff = font(F_BOLD, 30)
    name = "CAMPUS DES BÂTISSEURS"
    brick(d, M, fy + 4, 26, OR if dark else FORET)
    d.text((M + 66, fy), name, font=ff, fill=tc)
    if total == 0:  # story
        fs = font(F_BOLD, 40)
        lines2 = ["Une brique par jour.", "Dans quelques mois, tu verras la différence."]
        lh2 = 56
        tw2 = max(d.textlength(t2, font=fs) for t2 in lines2)
        if tw2 > W - 2 * M - 60:
            fs = font(F_BOLD, 34)
            tw2 = max(d.textlength(t2, font=fs) for t2 in lines2)
        py = fy - 80 - lh2 * len(lines2) - 40
        bg, fg = (OR, FORET) if dark else (FORET, IVOIRE)
        d.rounded_rectangle([(W - tw2) / 2 - 40, py, (W + tw2) / 2 + 40, py + lh2 * len(lines2) + 36], radius=36, fill=bg)
        for k, t2 in enumerate(lines2):
            d.text(((W - d.textlength(t2, font=fs)) / 2, py + 16 + k * lh2), t2, font=fs, fill=fg)
    if total > 0:
        segw, gap = 30, 8
        x = W - M - total * (segw + gap) + gap
        for i in range(total):
            on = i + 1 <= idx
            col = acc if on else (tc[:3] + (70,))
            d.rounded_rectangle([x, fy + 10, x + segw, fy + 22], radius=6, fill=col)
            x += segw + gap
    else:
        fh = font(F_MED, 30)
        h = "@campusdesbatisseurs"
        d.text((W - M - d.textlength(h, font=fh), fy + 2), h, font=fh, fill=tc2)
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
