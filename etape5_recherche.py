"""Étape 5 - Recherche des chunks les plus proches."""
from etape4_indexation import get_modele, get_collection


def rechercher(question, k=3, service=None):
    vecteur = get_modele().encode([question], normalize_embeddings=True).tolist()
    filtre = {"service": service} if service else None
    res = get_collection().query(query_embeddings=vecteur, n_results=k, where=filtre)
    return [{"texte": d, "source": m["source"], "page": m["page"],
             "service": m["service"], "score": round(1 - dist, 3)}
            for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])]


if __name__ == "__main__":
    for q in ["Combien de jours de télétravail par semaine ?",
              "Comment configurer le VPN ?",
              "Comment me faire rembourser mes frais de déplacement ?"]:
        print("\n###", q)
        for r in rechercher(q, k=3):
            print(f"  {r['source']} p.{r['page']} (score {r['score']})")
