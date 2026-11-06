"""Étape 6 - Génération d'une réponse sourcée.
SANS_LLM = True  : pas de modèle, on affiche le passage trouvé (en attendant le téléchargement).
SANS_LLM = False : LLM local avec transformers.
"""
from etape5_recherche import rechercher

SANS_LLM = True
MODELE_LLM = "Qwen/Qwen2.5-0.5B-Instruct"
REPLI = "Je n'ai pas trouvé cette information dans la documentation d'Altéa."

_tok = _llm = None


def _charger():
    global _tok, _llm
    if _llm is None:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        _tok = AutoTokenizer.from_pretrained(MODELE_LLM)
        _llm = AutoModelForCausalLM.from_pretrained(MODELE_LLM, low_cpu_mem_usage=True)
    return _tok, _llm


def _generer(prompt, max_tokens=250):
    tok, llm = _charger()
    texte = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                    tokenize=False, add_generation_prompt=True)
    entree = tok(texte, return_tensors="pt")
    # do_sample=False : décodage glouton, équivalent de temperature=0
    sortie = llm.generate(**entree, max_new_tokens=max_tokens, do_sample=False)
    return tok.decode(sortie[0][entree["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def construire_prompt(question, chunks):
    consigne = (
        "Tu es l'assistant documentaire d'Altéa Services. Réponds en français, UNIQUEMENT à partir "
        "des extraits ci-dessous. Cite la source (nom du fichier et page) pour chaque information. "
        f"Si la réponse n'est pas dans les extraits, réponds exactement : « {REPLI} »"
    )
    extraits = "\n\n".join(f"[Extrait {i}] (source : {c['source']}, page {c['page']})\n{c['texte']}"
                           for i, c in enumerate(chunks, start=1))
    return f"{consigne}\n\n=== EXTRAITS ===\n{extraits}\n\n=== QUESTION ===\n{question}\n\nRéponse :"


def repondre(question, k=3, service=None):
    chunks = rechercher(question, k=k, service=service)
    if SANS_LLM:
        c = chunks[0]
        return (f"[Mode sans LLM] Passage le plus proche ({c['source']}, page {c['page']}) :\n"
                f"{c['texte']}"), chunks
    return _generer(construire_prompt(question, chunks)), chunks


def repondre_sans_rag(question):
    if SANS_LLM:
        return "[Mode sans LLM] Non disponible : un LLM est nécessaire."
    return _generer(question)


if __name__ == "__main__":
    q = "Combien de jours de télétravail par semaine sont autorisés chez Altéa ?"
    print("--- PROMPT ---\n", construire_prompt(q, rechercher(q)))
    print("\n--- RAG ---\n", repondre(q)[0])
    print("\n--- LLM seul ---\n", repondre_sans_rag(q))
    for q in ["Comment poser un congé ?", "Comment configurer le VPN ?",
              "Comment demander du matériel ?", "Quel temps fera-t-il demain ?",
              "Qui a gagné la Coupe du monde 2018 ?"]:
        print(f"\n### {q}\n{repondre(q)[0]}")