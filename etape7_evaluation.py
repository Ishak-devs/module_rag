"""Étape 7 - Évaluation de la recherche puis des réponses."""
import csv
from etape5_recherche import rechercher
from etape6_generation import repondre


def taux_recherche(chemin="evaluation.csv", k=3):
    with open(chemin, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    ok = 0
    for l in lignes:
        trouves = [r["source"] for r in rechercher(l["question"], k=k)]
        reussi = l["document_attendu"] in trouves
        ok += reussi
        print(("OK  " if reussi else "RATE"), l["question"], "->", trouves)
    print(f"\nTaux de réussite de la recherche (k={k}) : {ok}/{len(lignes)} = {100*ok/len(lignes):.0f} %")


def generer_reponses(chemin="evaluation.csv", sortie="resultats.csv", k=3):
    """Génère les réponses ; à noter ensuite à la main (colonnes vides)."""
    with open(chemin, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    with open(sortie, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question", "document_attendu", "reponse", "sources", "note(juste/partielle/fausse)", "sources_exactes(oui/non)"])
        for l in lignes:
            rep, chunks = repondre(l["question"], k=k)
            w.writerow([l["question"], l["document_attendu"], rep,
                        "; ".join(sorted({c["source"] for c in chunks})), "", ""])
    print("Écrit :", sortie, "-> remplir les deux dernières colonnes à la main")


def bilan(chemin="resultats.csv"):
    with open(chemin, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    n = len(lignes)
    justes = sum(l["note(juste/partielle/fausse)"].strip() == "juste" for l in lignes)
    sources = sum(l["sources_exactes(oui/non)"].strip() == "oui" for l in lignes)
    print(f"Réponses justes : {100*justes/n:.0f} % | correctement sourcées : {100*sources/n:.0f} %")


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "recherche"
    {"recherche": taux_recherche, "generer": generer_reponses, "bilan": bilan}[cmd]()
