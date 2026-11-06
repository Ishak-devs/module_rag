# Réponses écrites - TP RAG Altéa Services

> Les valeurs marquées **À REMPLIR** dépendent de votre corpus : lancez les scripts et copiez vos résultats.

## Exercice 1

### Q2 - Pourquoi conserver nom de fichier, page et service ?
Le texte seul ne dit pas d'où vient une information. Deux usages concrets :
1. **Citer les sources** : l'assistant indique « teletravail.pdf, p. 2 », ce qui permet au salarié de vérifier la réponse et de lui faire confiance.
2. **Filtrer** : avec `service` en métadonnée, on peut limiter la recherche à un service (RH, IT...) pour de meilleurs résultats et un début de gestion des droits. Le nom de fichier sert aussi à identifier les chunks à mettre à jour quand un document change, et à évaluer la recherche (le bon document est-il retrouvé ?).

### Q4 - Défaut restant après nettoyage
Mesuré sur `teletravail.pdf`, page 1. **Avant** : le texte commence par l'en-tête « Altéa Services — Document interne — Diffusion restreinte », suivi du numéro de page « 1 » et de « Document fictif réalisé à des fins pédagogiques », puis du contenu. **Après** `nettoyer` seul : espaces et lignes vides sont traités, le numéro de page isolé est retiré par regex, mais l'en-tête et le pied de page restent, car ils sont du vrai texte répété sur chaque page. Règle proposée (fonction `retirer_en_tetes`) : supprimer toute ligne présente sur plus de 50 % des pages d'un même document. Elle s'applique dès 2 pages ; avec un minimum de 3 pages, elle ne se déclenchait pas sur ce corpus (documents de 2 pages), d'où le seuil à 2. Après correction, la page commence directement par « Télétravail ».
**Défaut restant** : les tableaux. Dans `notes_de_frais.pdf`, le tableau des plafonds est aplati, une cellule par ligne (« Repas du midi en déplacement » / « 20 € par repas »). La correspondance libellé-montant n'est plus visible et un découpage peut séparer un libellé de son montant. Règle possible : extraire les tableaux avec `pdfplumber` et les reconstituer en lignes « libellé : valeur ».

### Q5 - Vérification de `decouper("abcdefghij", 4, 1)`
Le pas est taille − chevauchement = 4 − 1 = 3. Les chunks démarrent aux positions 0, 3 et 6 : `abcd` (0-3), `defg` (3-6), `ghij` (6-9). Chaque chunk reprend la dernière lettre du précédent (d, puis g). Le dernier atteint la fin du texte, donc on s'arrête (démarrer en 9 donnerait `j`, déjà contenu dans `ghij`).

### Q6 - Tableau
Corpus : 15 documents, 23 pages (aucune page vide après nettoyage). Résultats de `python etape3_decoupage.py` :

| Taille | Chevauchement | Nombre de chunks | Longueur moyenne |
|---|---|---|---|
| 200 | 20 | 148 | 187 |
| 500 | 50 | 62 | 437 |
| 1000 | 100 | 37 | 717 |

Plus la taille augmente, moins il y a de chunks ; la longueur moyenne est inférieure à la taille car le dernier chunk de chaque page est plus court.

### Q7 - Taille des chunks
- **Trop petit** : le chunk perd son contexte (une règle sans sa condition, un chiffre sans son sujet), la recherche renvoie des fragments peu informatifs et il faut beaucoup de chunks.
- **Trop grand** : le chunk mélange plusieurs sujets, son embedding est « dilué » donc moins précis, et il consomme beaucoup de place dans le prompt du LLM.
- **Chevauchement** : éviter qu'une phrase ou une information coupée en deux à la frontière soit perdue ; chaque morceau garde un peu du contexte du précédent.
- **Choix** : **500 caractères / 50 de chevauchement**, compromis courant pour des documents internes courts (à confirmer par l'évaluation de l'étape 7).

### Q8 - Dimension et volume
Le modèle `paraphrase-multilingual-MiniLM-L12-v2` produit des vecteurs de **dimension 384**. Nombre de valeurs à stocker = nombre de chunks × 384 avec 62 chunks de 500 caractères : 62 × 384 = **23 808 nombres**.

### Q9 - Matrice de similarité
Sont proches les phrases de même sens : « Comment poser des jours de congé ? » et « Quelle est la procédure pour demander des vacances ? » ; de même pour les deux phrases sur l'accès/mot de passe. Les phrases de sujets différents (cantine) ont une similarité faible. **Complétez avec vos valeurs réelles.** Les phrases 1 et 2 sont proches malgré le peu de mots communs parce que l'embedding représente le **sens** et non les mots : le modèle a appris que « congé » et « vacances », « poser » et « demander » apparaissent dans des contextes semblables. C'est ce qui distingue la recherche sémantique de la recherche par mots-clés.

### Q12 - Réindexation
Non, le nombre de chunks ne double pas : les identifiants sont déterministes (`fichier_page_chunk`), donc `upsert` **remplace** les chunks existants au lieu d'en ajouter. `add` créerait des doublons ou lèverait une erreur sur les ids déjà présents, et la recherche renverrait plusieurs fois le même passage. Quand un document est modifié : supprimer ses anciens chunks (`collection.delete(where={"source": "nom.pdf"})`) puis le réindexer, car si le nouveau texte est plus court, d'anciens chunks orphelins resteraient avec `upsert` seul.

### Q13 - Base vectorielle et GitHub
`base_vectorielle/` est un dossier **généré**, volumineux, binaire et reconstructible : on ne versionne pas les fichiers dérivés (il est dans `.gitignore`). De plus il contient le contenu des documents internes, qui ne doit pas être publié. Un collègue clone le dépôt, installe `requirements.txt`, place les documents dans `docs/` puis lance `python etape4_indexation.py`, qui recrée la base.

## Exercice 2

### Q2 - Effet de k
Quand k augmente, on **gagne** en rappel (plus de chances que le bon passage soit présent, utile si la réponse est répartie sur plusieurs chunks). On **perd** en précision : on ajoute du bruit (chunks hors sujet), le prompt s'allonge, la génération est plus lente et le LLM peut se laisser distraire ou mélanger les sources. k = 1 est précis mais fragile ; k = 10 est coûteux et bruité ; k = 3 à 5 est un bon compromis. **À REMPLIR** avec vos observations.

### Q3 - Filtre par service
Avec `service="RH"` les résultats viennent de documents RH ; avec `service="IT"` la même question RH renvoie des chunks IT peu pertinents (scores plus bas), voire rien d'utile. C'est une première étape vers la confidentialité : un salarié ne voit que les services auxquels il a droit. Mais ce filtre **ne suffit pas** : il est choisi par l'utilisateur (donc contournable), il est grossier (par service, pas par document ou par personne), et il n'y a ni authentification ni gestion de droits réels ; les données peuvent aussi fuiter par les logs ou le LLM.

### Q5 - Tableau de test (5 questions)
| Question | Réponse juste ? | Sources citées ? | Phrase de repli ? |
|---|---|---|---|
| Comment poser un congé ? | **À REMPLIR** | | n/a |
| Comment configurer le VPN ? | | | n/a |
| Comment demander du matériel ? | | | n/a |
| Quel temps fera-t-il demain ? | n/a | non | **attendu : oui** |
| Qui a gagné la Coupe du monde 2018 ? | n/a | non | **attendu : oui** |

### Q6 - Hallucination
Sans extraits, le LLM ne connaît pas Altéa et invente une réponse plausible (par ex. « 2 jours par semaine ») sans aucune source. Une **hallucination** est une affirmation fausse ou inventée, formulée avec assurance. Le RAG la limite en fournissant au modèle les passages réels et en lui imposant de répondre uniquement à partir d'eux, de citer ses sources et de dire « je ne sais pas » en l'absence d'information. Il ne l'élimine pas totalement (mauvais extraits retrouvés, mauvaise lecture). **Ajoutez vos deux réponses observées.**

### Q7 - temperature=0
Pour un assistant documentaire on veut des réponses **factuelles, reproductibles et fidèles** aux extraits. Une température 0 rend la génération quasi déterministe (le mot le plus probable à chaque étape), ce qui réduit la créativité et donc le risque d'invention ; la même question donne la même réponse, ce qui facilite les tests et l'évaluation.

### Q9 à Q10 - Résultats d'évaluation
- Taux de réussite de la recherche (`python etape7_evaluation.py recherche`) : **À REMPLIR** / 10
- Réponses justes : **À REMPLIR** % ; correctement sourcées : **À REMPLIR** % (`python etape7_evaluation.py generer`, noter à la main `resultats.csv`, puis `bilan`).

### Q11 - Analyse d'une réponse fausse
**À REMPLIR** avec votre cas. Démarche : regarder si le document attendu figure dans les k chunks. S'il est absent, l'erreur vient de la **recherche** (améliorations : taille des chunks, k plus grand, nettoyage, reformulation) ; s'il est présent, elle vient de la **génération** (améliorations : consigne plus stricte, moins d'extraits parasites, modèle plus grand). Testez une amélioration à la fois (ex. k = 3 → 5, ou chunks 500 → 1000) et indiquez avant/après : « taux de recherche 7/10 → 9/10 ».

### Q14 - Quatre points avant le déploiement général
1. **Droits d'accès** : chaque salarié ne doit voir que les documents qu'il a le droit de lire (RH confidentiels, direction...). Il faut authentifier les utilisateurs et filtrer la recherche côté serveur selon leurs droits, pas via un simple choix dans l'interface.
2. **Données personnelles (RGPD)** : les documents et les questions peuvent contenir des données personnelles. Il faut les minimiser ou les anonymiser, limiter la conservation des logs et informer les utilisateurs.
3. **Mise à jour des documents** : les procédures changent ; une réponse basée sur une version périodée est dangereuse. Prévoir une réindexation automatique, des versions/dates de document affichées et la suppression des anciens chunks.
4. **Coût, hébergement et fiabilité du LLM** : un LLM local demande des serveurs (GPU) dimensionnés pour de nombreux utilisateurs simultanés ; un LLM cloud pose des questions de confidentialité et de coût par requête. Il faut aussi surveiller la qualité (jeu d'évaluation élargi, retour utilisateur) et prévoir une sécurité, de la supervision et un support.
