"""Transforme une « liste valeur » en carrousel TikTok lisible (TikTok supprime les sauts de ligne des légendes).

Usage : python3 -I outils/liste_tiktok.py valeur/AAAA-MM-JJ
Lit valeur/AAAA-MM-JJ/liste.txt (format : titre, « (Parce que …) », puis points « N. emoji Titre. » suivis de lignes courtes)
et visuel.json (couverture). Écrit valeur/AAAA-MM-JJ/tiktok/slides.json puis génère tiktok/tt_01.jpg … :
  diapo 1 = couverture, puis 1 diapo par point (titre + une idée par ligne), dernière diapo = conclusion communauté.
"""
import json, os, re, subprocess, sys

d = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(d, "liste.txt"), encoding="utf-8").read().strip()
cover = json.load(open(os.path.join(d, "visuel.json"), encoding="utf-8"))["cover"]

blocks = [b.strip() for b in re.split(r"\n\s*\n", txt) if b.strip()]
points = []
for b in blocks:
    m = re.match(r"^(\d+)\.\s*(.+)$", b.split("\n")[0])
    if m:
        points.append({"n": int(m.group(1)), "title": m.group(2).strip(), "lines": []})
    elif points and not b.startswith("Ici, on partage"):
        points[-1]["lines"] += [l.strip() for l in b.split("\n") if l.strip()]

def clean(t):
    # retire les emojis (non affichables par la police) et espaces superflus
    t = "".join(ch for ch in t if ord(ch) < 0x2190 or ch in "→✓★↗’«»…–—")
    return re.sub(r"\s+", " ", t).strip()

n = len(points)
types = ["solution", "promesse", "curiosite", "resultat"]
slides = [dict(cover, body=(cover.get("body", "").split("\n")[0] + "\nGlisse pour lire →"))]
for i, p in enumerate(points):
    words = clean(p["title"]).rstrip(".").split(" ")
    # surligne le dernier mot du titre
    words[-1] = "*" + words[-1] + "*"
    slides.append({"type": types[i % len(types)], "tag": f"{p['n']} / {n}",
                   "title": " ".join(words), "body": "\n".join(clean(l) for l in p["lines"])})
slides.append({"type": "cta", "tag": "Ce qu'on construit ici",
               "title": "Une brique par jour. Dans quelques mois, tu verras la *différence.*",
               "body": "Ici, on partage chaque jour ce qui marche vraiment, sans promesse magique.",
               "big": "@campusdesbatisseurs"})

out = os.path.join(d, "tiktok")
os.makedirs(out, exist_ok=True)
json.dump({"slides": slides}, open(os.path.join(out, "slides.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, "-I", os.path.join(here, "carousel.py"), os.path.join(out, "slides.json"), out], check=True)
for f in os.listdir(out):
    if f.startswith("fb_"):
        os.remove(os.path.join(out, f))
print("diapos TikTok :", len(slides))
