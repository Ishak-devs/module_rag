"""Étape 2 - Nettoyage du texte extrait."""
import re
from collections import Counter
from etape1_collecte import collecter


def nettoyer(texte):
    texte = texte.replace("\r", "")
    texte = re.sub(r"-\n(\w)", r"\1", texte)           # mots coupés en fin de ligne
    texte = re.sub(r"[ \t]+", " ", texte)               # espaces multiples
    lignes = [l.strip() for l in texte.split("\n")]
    lignes = [l for l in lignes if l]                   # lignes vides
    lignes = [l for l in lignes if not re.fullmatch(r"(page\s*)?\d+(\s*/\s*\d+)?", l, re.I)]  # n° de page
    return "\n".join(lignes)


def retirer_en_tetes(pages, seuil=0.5):
    """Supprime les lignes présentes sur plus de `seuil` des pages d'un même document."""
    par_doc = {}
    for p in pages:
        par_doc.setdefault(p["source"], []).append(p)
    for source, ps in par_doc.items():
        if len(ps) < 2:
            continue
        compteur = Counter(l for p in ps for l in set(p["texte"].split("\n")))
        repetees = {l for l, n in compteur.items() if n / len(ps) > seuil}
        for p in ps:
            p["texte"] = "\n".join(l for l in p["texte"].split("\n") if l not in repetees)
    return pages


def nettoyer_pages(pages):
    for p in pages:
        p["texte"] = nettoyer(p["texte"])
    pages = retirer_en_tetes(pages)
    return [p for p in pages if p["texte"].strip()]


if __name__ == "__main__":
    brutes = collecter()
    p0 = brutes[0]
    print("=== AVANT ===\n", repr(p0["texte"][:600]))
    propres = nettoyer_pages(brutes)
    print("\n=== APRÈS ===\n", repr(propres[0]["texte"][:600]))
    print(f"\n{len(brutes)} pages -> {len(propres)} pages non vides")
