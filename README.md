📑 Lanalyseur legal


Legal Analyzer est une application basée sur FastAPI (backend) et HTML/JavaScript (frontend) permettant d’analyser automatiquement des contrats juridiques.

Elle utilise le NLP (traitement automatique du langage) pour :

Extraire les clauses importantes (Durée, Prix, Confidentialité, Juridiction, etc.)

Identifier les entités nommées (dates, montants, noms d’entreprises, personnes)

Générer un résumé automatique du contrat

Détecter les risques juridiques grâce à un système de règles (ex : clauses déséquilibrées, pénalités excessives, confidentialité perpétuelle, responsabilité illimitée, etc.)

🚀 Fonctionnalités principales

📂 Upload de documents (TXT, PDF avec OCR automatique si besoin)

🔍 Analyse automatique des clauses

🧠 Résumé automatique (via modèle NLP ou fallback TextRank)

🛑 Détection des risques via un fichier de règles rules.yaml

📊 Visualisation claire des clauses, entités et risques détectés via une interface web simple

🛠️ Technologies utilisées

Backend : FastAPI, Uvicorn, SQLAlchemy

NLP : spaCy, Transformers (HuggingFace), regex avancées

Frontend : HTML5, CSS3, JavaScript (fetch API)

Base de données : MySQL (ou SQLite en mode dev)

📂 Structure du projet
legal-analyzer/
│── backend/
│   ├── app.py          # Backend FastAPI
│   ├── pipeline.py     # Analyse NLP et règles
│   ├── crud.py         # Opérations DB
│   ├── models.py       # Modèles SQLAlchemy
│   ├── rules.yaml      # Définition des risques
│   └── uploads/        # Fichiers uploadés
│
│── frontend/
│   └── index.html      # Interface utilisateur
│
└── README.md           # Documentation
▶️ Démarrage rapide
1. Créer un environnement virtuel et installer les dépendances
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
2. Lancer le serveur FastAPI
uvicorn backend.app:app --reload
3. Ouvrir l’interface web
Accédez à :
👉 http://127.0.0.1:8000 pour l’API
👉 Ouvrir frontend/index.html dans le navigateur pour l’interface
📌 Exemple de détection de risques
Pour un contrat contenant :
Confidentialité perpétuelle
Pénalités de retard excessives
Durée indéterminée sans résiliation
L’application affichera :
Risques détectés :
- CONFIDENTIALITÉ_PERPÉTUELLE (High)
- PÉNALITÉS_FORTES (High)
- MISSING_RÉSILIATION (Medium)
⚖️ Legal Analyzer a pour but de simplifier la lecture et la compréhension des contrats.
Il ne remplace pas un avis juridique, mais permet de mettre en évidence rapidement les points sensibles.

<img width="1792" height="1120" alt="Capture d’écran 2025-08-24 à 23 43 23" src="https://github.com/user-attachments/assets/c017021d-a779-4b1e-b48c-e4bc298bb61c" />
<img width="1792" height="1120" alt="Capture d’écran 2025-08-24 à 23 43 37" src="https://github.com/user-attachments/assets/b1609097-f53d-45f0-b9a0-10473eed6a39" />
<img width="1792" height="1120" alt="Capture d’écran 2025-08-24 à 23 43 41" src="https://github.com/user-attachments/assets/666653d9-a940-4457-bf62-cddeb786f2de" />
<img width="1792" height="1120" alt="Capture d’écran 2025-08-24 à 23 43 54" src="https://github.com/user-attachments/assets/b56f86fa-4f02-4146-a96b-8832f3bdb397" />
