"""Étape 1 - Collecte : lire les fichiers et garder texte + origine."""
from pathlib import Path
from pypdf import PdfReader

DOSSIER_DOCS = Path("docs")


def collecter(dossier=DOSSIER_DOCS):
    """Retourne une liste de pages : {texte, source, page, service}."""
    pages = []
    for chemin in sorted(Path(dossier).rglob("*")):
        if not chemin.is_file():
            continue
        service = chemin.parent.name  # RH, IT ou General
        if chemin.suffix.lower() == ".pdf":
            lecteur = PdfReader(str(chemin))
            for i, page in enumerate(lecteur.pages, start=1):
                pages.append({"texte": page.extract_text() or "",
                              "source": chemin.name, "page": i, "service": service})
        elif chemin.suffix.lower() == ".txt":
            pages.append({"texte": chemin.read_text(encoding="utf-8"),
                          "source": chemin.name, "page": 1, "service": service})
    return pages


if __name__ == "__main__":
    pages = collecter()
    compte = {}
    for p in pages:
        compte[(p["service"], p["source"])] = compte.get((p["service"], p["source"]), 0) + 1
    for (service, source), n in compte.items():
        print(f"{service:8} {source:40} {n} page(s)")
    print(f"Total : {len(compte)} documents, {len(pages)} pages")
