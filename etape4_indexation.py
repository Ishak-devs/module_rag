"""Étape 4 - Embeddings et indexation (ChromaDB)."""
import chromadb
from sentence_transformers import SentenceTransformer
from etape1_collecte import collecter
from etape2_nettoyage import nettoyer_pages
from etape3_decoupage import decouper_pages

MODELE = "paraphrase-multilingual-MiniLM-L12-v2"   # multilingue, dimension 384
TAILLE, CHEVAUCHEMENT = 500, 50
CHEMIN_BASE = "base_vectorielle"

_modele = None
def get_modele():
    global _modele
    if _modele is None:
        _modele = SentenceTransformer(MODELE)
    return _modele


def get_collection():
    client = chromadb.PersistentClient(path=CHEMIN_BASE)
    return client.get_or_create_collection("altea", metadata={"hnsw:space": "cosine"})


def partie_a():
    """Q8-Q9 : dimension et matrice de similarité."""
    import numpy as np
    phrases = [
        "Comment poser des jours de congé ?",
        "Quelle est la procédure pour demander des vacances ?",
        "J'ai oublié mon mot de passe.",
        "Comment réinitialiser mon accès à l'ordinateur ?",
        "Quel est le menu de la cantine ?",
    ]
    emb = get_modele().encode(phrases, normalize_embeddings=True)
    print("Dimension d'un vecteur :", emb.shape[1])
    print(np.round(emb @ emb.T, 2))


def partie_b():
    """Q10 : enchaîne étapes 1 à 4."""
    pages = nettoyer_pages(collecter())
    chunks = decouper_pages(pages, TAILLE, CHEVAUCHEMENT)
    textes = [c["texte"] for c in chunks]
    embeddings = get_modele().encode(textes, normalize_embeddings=True, show_progress_bar=True)
    ids = [f"{c['source']}_p{c['page']}_c{c['chunk']}" for c in chunks]
    metas = [{"source": c["source"], "page": c["page"], "service": c["service"]} for c in chunks]
    col = get_collection()
    col.upsert(ids=ids, embeddings=embeddings.tolist(), documents=textes, metadatas=metas)
    print(f"Chunks produits : {len(chunks)} | indexés : {col.count()}")
    assert col.count() == len(chunks)
    print(f"Nombres stockés : {len(chunks)} x {embeddings.shape[1]} = {len(chunks) * embeddings.shape[1]}")


if __name__ == "__main__":
    partie_a()
    partie_b()
