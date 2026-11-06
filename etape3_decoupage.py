"""Étape 3 - Découpage en chunks avec chevauchement."""
from etape1_collecte import collecter
from etape2_nettoyage import nettoyer_pages


def decouper(texte, taille=500, chevauchement=50):
    if chevauchement >= taille:
        raise ValueError("chevauchement doit être < taille")
    pas = taille - chevauchement
    chunks, debut = [], 0
    while debut < len(texte):
        chunks.append(texte[debut:debut + taille])
        if debut + taille >= len(texte):   # le texte est entièrement couvert
            break
        debut += pas
    return chunks


def decouper_pages(pages, taille=500, chevauchement=50):
    chunks = []
    for p in pages:
        for i, c in enumerate(decouper(p["texte"], taille, chevauchement)):
            chunks.append({"texte": c, "source": p["source"], "page": p["page"],
                           "service": p["service"], "chunk": i})
    return chunks


if __name__ == "__main__":
    assert decouper("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"]
    print("Test OK : pas = 4-1 = 3 -> débuts 0, 3, 6 -> abcd / defg / ghij")
    pages = nettoyer_pages(collecter())
    print(f"{'Taille':>7} {'Chev.':>6} {'Chunks':>7} {'Long. moy.':>11}")
    for t, c in [(200, 20), (500, 50), (1000, 100)]:
        ch = decouper_pages(pages, t, c)
        moy = sum(len(x["texte"]) for x in ch) / len(ch)
        print(f"{t:>7} {c:>6} {len(ch):>7} {moy:>11.0f}")
