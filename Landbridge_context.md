# LangBridge — Contexte projet pour Claude Code

## Vue d'ensemble

Tu vas m'aider à construire **LangBridge**, un projet soumis au **Gemma 4 Good Hackathon** organisé par Kaggle et Google DeepMind (deadline : 18 mai 2026, prize pool : 200 000 $).

LangBridge est une **application web progressive (PWA) multilingue** qui aide les réfugiés et nouveaux arrivants à apprendre la langue locale via des simulations de situations du quotidien (mairie, médecin, école, travail). Le tout fonctionne **hors-ligne, sans envoyer aucune donnée à l'extérieur**, grâce à Gemma 4 qui tourne en local via Ollama.

---

## Le hackathon — contraintes et critères de jugement

### Organisateurs
- **Kaggle** + **Google DeepMind**
- Compétition officielle : https://www.kaggle.com/competitions/gemma-4-good-hackathon

### Dates
- Début : 2 avril 2026
- **Deadline soumission : 18 mai 2026 à 23h59 UTC**
- Temps restant effectif : ~4 semaines de développement

### Prize pool
- **200 000 $ total**, réparti en catégories (général, impact, technique)
- **Prix Unsloth spécial : 10 000 $** pour le meilleur fine-tune réalisé avec la stack Unsloth

### Ce que les jurés évaluent
1. **Impact réel** — le projet résout-il un vrai problème pour de vraies personnes ?
2. **Exécution technique** — le prototype tourne-t-il vraiment ? Le code est-il propre ?
3. **Utilisation de Gemma 4** — le modèle est-il utilisé de façon significative (pas juste un wrapper ChatGPT-like) ?
4. **Fonctionnement en environnements contraints** — offline, faible bande passante, hardware limité
5. **Documentation** — repo public clair, README, write-up technique

### Livrables obligatoires
- Prototype fonctionnel (pas une démo mockée)
- Dépôt GitHub public avec code + README
- Vidéo de démonstration (2-3 min max)
- Write-up technique expliquant l'usage de Gemma 4 et les choix d'implémentation

### Catégorie visée
**Éducation** (Future of Education) + éligibilité au **prix Unsloth** via le fine-tuning QLoRA documenté.

---

## Le problème résolu par LangBridge

Des millions de réfugiés et migrants arrivent dans un nouveau pays sans maîtriser la langue locale. Les outils d'apprentissage linguistique existants (Duolingo, etc.) sont :
- Gamifiés mais superficiels — ils n'apprennent pas à naviguer les situations administratives réelles
- Dépendants du cloud — inutilisables sans connexion stable
- Pas adaptés aux urgences du quotidien (rendez-vous préfecture, urgences médicales, inscription scolaire)

LangBridge répond à ce besoin avec des **simulations de dialogues réels**, une **correction pédagogique inline**, et un fonctionnement **entièrement hors-ligne**.

---

## Architecture technique

### Modèles Gemma 4 utilisés

| Rôle | Modèle | Pourquoi |
|------|--------|----------|
| Conversations hors-ligne légères | `gemma4:e4b` via Ollama | Tourne sur CPU, ~4 Go RAM |
| Simulations riches + corrections | `gemma4:26b` via Ollama | Meilleure qualité multilingue |
| Fine-tuné (prize Unsloth) | `gemma4:26b` + QLoRA | Spécialisé dialogues administratifs |

Le fine-tune QLoRA cible les dialogues administratifs dans 4 langues : **français, anglais, arabe, espagnol**. Les données d'entraînement proviennent de :
- OPUS-100 (corpus de traductions multilingues, licence libre)
- FLORES-200 (benchmark multilingue Meta, licence CC-BY)
- Dialogues administratifs synthétiques générés et vérifiés manuellement

### Stack complète

```
Frontend         React 18 + Vite + TypeScript
                 PWA (Workbox service worker, cache offline complet)
                 TailwindCSS

Backend          FastAPI (Python 3.11)
                 Uvicorn (ASGI)
                 Pydantic v2 pour la validation

Inference        Ollama (API REST locale, port 11434)
                 Compatible Windows 10/11 et Ubuntu 22.04+

Voix — entrée   Whisper.cpp (binaire local, pas de cloud)
                 Modèle whisper-small ou medium selon hardware

Voix — sortie   Piper TTS (synthèse vocale locale, voix naturelle)
                 Fallback : Web Speech Synthesis API (natif navigateur)

Fine-tuning      Unsloth + QLoRA (4-bit quantization)
                 Datasets : OPUS-100, FLORES-200, synthétiques
                 Environnement : Ubuntu natif ou WSL2 + CUDA

Base de données  SQLite (via SQLAlchemy async) — aucune dépendance externe
                 Stocke : sessions, progression utilisateur, historique

Packaging        Electron (optionnel) pour Windows .exe installable
                 Sinon : localhost simple, instructions dans README
```

### Structure de fichiers cible

```
langbridge/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── chat.py              # POST /chat — conversation avec Gemma 4
│   │   ├── scenarios.py         # GET /scenarios — liste des scénarios disponibles
│   │   ├── progress.py          # GET/POST /progress — suivi utilisateur
│   │   └── tts.py               # POST /tts — synthèse vocale Piper
│   ├── services/
│   │   ├── ollama_client.py     # Client Ollama (streaming + non-streaming)
│   │   ├── whisper_service.py   # Transcription audio locale
│   │   ├── piper_service.py     # Synthèse vocale locale
│   │   └── pedagogy.py          # Logique de correction et feedback pédagogique
│   ├── models/
│   │   ├── database.py          # SQLAlchemy async setup
│   │   └── schemas.py           # Pydantic schemas
│   ├── data/
│   │   └── scenarios/           # Fichiers JSON des scénarios par langue
│   │       ├── fr/
│   │       ├── en/
│   │       ├── ar/
│   │       └── es/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx   # Fenêtre de conversation principale
│   │   │   ├── ScenarioCard.tsx # Carte de sélection de scénario
│   │   │   ├── VoiceButton.tsx  # Bouton micro (Whisper.cpp)
│   │   │   ├── FeedbackPanel.tsx# Corrections grammaticales inline
│   │   │   └── ProgressBar.tsx  # Progression par scénario
│   │   ├── pages/
│   │   │   ├── Home.tsx         # Sélection langue cible + scénario
│   │   │   ├── Chat.tsx         # Interface de simulation
│   │   │   └── Progress.tsx     # Tableau de bord progression
│   │   ├── hooks/
│   │   │   ├── useOllama.ts     # Hook streaming Gemma 4
│   │   │   └── useVoice.ts      # Hook Web Speech + Whisper
│   │   └── App.tsx
│   ├── public/
│   │   └── manifest.json        # PWA manifest
│   ├── vite.config.ts
│   └── package.json
├── finetune/
│   ├── prepare_dataset.py       # Nettoyage et formatage OPUS-100 / FLORES
│   ├── train.py                 # Script Unsloth QLoRA
│   ├── evaluate.py              # Métriques avant/après fine-tune
│   └── README_finetune.md       # Instructions reproductibles
├── docker-compose.yml           # Optionnel pour démo reproductible
├── README.md
└── HACKATHON_WRITEUP.md         # Write-up technique pour la soumission
```

---

## Scénarios de simulation prévus (MVP)

Chaque scénario est un fichier JSON avec : contexte, rôle de l'IA, objectifs pédagogiques, vocabulaire clé, phrases types.

| # | Scénario | Langue cible | Difficulté |
|---|----------|-------------|------------|
| 1 | Rendez-vous à la préfecture | Français | Intermédiaire |
| 2 | Consultation médicale généraliste | Français / Anglais | Intermédiaire |
| 3 | Inscription scolaire d'un enfant | Français | Débutant |
| 4 | Entretien d'embauche (poste non qualifié) | Français / Anglais | Avancé |
| 5 | Achat en supermarché / pharmacie | Français | Débutant |
| 6 | Appel à un propriétaire (logement) | Français | Intermédiaire |

Chaque scénario supporte 3 niveaux : **débutant** (phrases simples, Gemma 4 parle lentement et clairement), **intermédiaire**, **avancé** (vitesse normale, argot administratif).

---

## Comportement de Gemma 4 dans l'application

### System prompt de base (à adapter par scénario)

```
Tu es un agent de formation linguistique pour réfugiés et nouveaux arrivants.
Tu joues le rôle de [ROLE_DU_SCENARIO] en [LANGUE_CIBLE].

Règles impératives :
1. Tu parles UNIQUEMENT en [LANGUE_CIBLE] sauf pour les corrections pédagogiques
2. Tu adaptes ta complexité au niveau [NIVEAU] de l'utilisateur
3. Après chaque réponse de l'utilisateur, tu fournis un bloc JSON structuré séparé :
   {"corrections": [...], "vocabulary": [...], "encouragement": "..."}
4. Tu ne dévoiles pas que tu es une IA sauf si l'utilisateur le demande explicitement
5. Tu fais avancer le scénario naturellement, comme un vrai interlocuteur

Contexte du scénario : [CONTEXTE_DETAILLE]
Objectif de la session : [OBJECTIF]
```

### Function calling Gemma 4 (natif)

Gemma 4 supporte nativement le function calling via JSON schema. On l'utilise pour :
- `get_vocabulary_hint(word)` — définition contextuelle sans quitter la conversation
- `evaluate_grammar(sentence, language)` — retourne les erreurs avec explications
- `advance_scenario(current_step)` — fait progresser le scénario vers l'étape suivante

---

## Contraintes techniques spécifiques au développeur

### Environnement de développement
- **OS** : Windows 10/11 + Ubuntu 22.04 (dual boot ou WSL2)
- **Pas d'appareil iOS** — aucune app iOS à développer. La PWA couvre Android et navigateurs desktop.
- **GPU** : à préciser — si disponible, utilisé pour le fine-tuning Unsloth. Sinon : Kaggle GPU (30h/semaine gratuit) ou Colab Pro.

### Ollama sur Windows
```bash
# Installation Windows (PowerShell)
winget install Ollama.Ollama

# Pull des modèles
ollama pull gemma4:e4b       # ~3 Go — pour tests rapides
ollama pull gemma4:26b       # ~16 Go — pour prod

# Vérification
ollama list
curl http://localhost:11434/api/tags
```

### Ollama sur Ubuntu
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull gemma4:e4b
ollama pull gemma4:26b
```

### Whisper.cpp sur Windows/Ubuntu
```bash
# Ubuntu
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp && make
bash ./models/download-ggml-model.sh small

# Windows — utiliser les binaires pré-compilés depuis les releases GitHub
# ou via WSL2
```

### Piper TTS
```bash
# pip install piper-tts
# Voix disponibles : fr_FR-upmc-medium, en_US-lessac-medium, ar_JO-kareem-medium
pip install piper-tts
```

### Unsloth (fine-tuning) — Ubuntu natif recommandé
```bash
pip install unsloth
# Nécessite CUDA 11.8+ et une carte NVIDIA
# Sur Windows : passer par WSL2 avec CUDA configuré
# Alternativement : notebook Kaggle (GPU T4 gratuit 30h/semaine)
```

---

## Fine-tuning QLoRA — objectif prix Unsloth

### Pourquoi fine-tuner ?
Le baseline Gemma 4 26B est déjà multilingue et capable. Le fine-tune apporte :
- Meilleure cohérence dans les rôles administratifs (agent préfecture, médecin, etc.)
- Ton plus réaliste pour les dialogues bureaucratiques français
- Réduction des hallucinations sur les procédures administratives réelles
- Métriques documentées = argument solide pour le write-up

### Pipeline prévu
```python
# Pseudo-code du pipeline Unsloth
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="google/gemma-4-26b-it",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,                    # rang LoRA
    target_modules=["q_proj", "v_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
)

# Dataset : dialogues administratifs formatés en ShareGPT format
# Train : 80% | Eval : 20%
# Métriques : BLEU score, perplexité, human eval sur 50 échantillons
```

### Métriques à documenter pour le jury Unsloth
- Perplexité avant/après fine-tune sur le dataset de validation
- BLEU score sur les traductions administratives
- Exemples qualitatifs : même prompt → réponse baseline vs fine-tuné
- Temps d'entraînement, hardware utilisé, coût estimé

---

## Plan de développement sur 4 semaines

### Semaine 1 — Foundation (priorité : faire tourner le pipeline de bout en bout)
- [ ] Setup Ollama + Gemma 4 E4B (Windows ET Ubuntu, les deux doivent marcher)
- [ ] Backend FastAPI minimal : endpoint `/chat` qui appelle Ollama en streaming
- [ ] Frontend React basique : zone de texte → affichage réponse streamée
- [ ] Premier scénario JSON (préfecture) + system prompt testé
- [ ] Collecte et nettoyage partiel du dataset fine-tune (OPUS-100)

### Semaine 2 — Core features
- [ ] Intégration Whisper.cpp (input vocal → transcription)
- [ ] Intégration Piper TTS (réponse Gemma 4 → audio)
- [ ] 3 scénarios JSON complets (préfecture, médecin, inscription scolaire)
- [ ] Feedback pédagogique inline (parsing JSON des corrections)
- [ ] Interface React propre avec sélecteur de scénario et niveau
- [ ] Lancement du fine-tuning QLoRA (peut tourner en arrière-plan)

### Semaine 3 — PWA + Polish
- [ ] Service worker Workbox — fonctionnement offline complet
- [ ] 3 scénarios supplémentaires (emploi, pharmacie, logement)
- [ ] Système de progression utilisateur (SQLite)
- [ ] Intégration du modèle fine-tuné si prêt
- [ ] Tests sur Android (PWA dans Chrome mobile)
- [ ] README complet + instructions d'installation Windows/Ubuntu

### Semaine 4 — Soumission
- [ ] Évaluation formelle du fine-tune (métriques BLEU, exemples qualitatifs)
- [ ] Rédaction HACKATHON_WRITEUP.md (write-up technique pour Kaggle)
- [ ] Tournage vidéo démo (scénario préfecture de bout en bout, 2-3 min)
- [ ] Repo GitHub public : nettoyage code, docstrings, LICENSE Apache 2.0
- [ ] Soumission Kaggle avant le 18 mai 23h59 UTC

---

## Ce que j'attends de toi, Claude Code

Tu vas m'aider à construire ce projet fichier par fichier, en respectant ces règles :

### Règles de développement
1. **Toujours vérifier la compatibilité Windows ET Ubuntu** avant de proposer une commande ou une dépendance
2. **Streaming obligatoire** pour les réponses Ollama — l'UX doit être fluide, pas de loading spinner de 10 secondes
3. **Offline-first** — chaque feature doit fonctionner sans internet une fois les modèles téléchargés
4. **Pas d'app iOS** — toutes les fonctionnalités mobiles passent par la PWA Android/navigateur
5. **Code propre et commenté** — le repo sera public et évalué par des jurés techniques
6. **Gestion d'erreurs explicite** — Ollama peut être down, Whisper peut planter, tout doit avoir un fallback

### Ordre de priorité si le temps manque
1. Le pipeline conversationnel texte (sans voix) doit absolument fonctionner
2. La voix (Whisper + Piper) est une feature nice-to-have importante pour la démo
3. Le fine-tuning est optionnel pour le fonctionnement de base, mais fortement souhaité pour le prix Unsloth
4. La PWA offline peut être simplifiée à un simple `localhost` si le temps manque

### Points de vigilance
- **Ollama API** : utiliser `http://localhost:11434/v1` (compatible OpenAI SDK) ou l'API native Ollama selon ce qui est plus simple dans le contexte
- **Streaming React** : utiliser `ReadableStream` + `TextDecoder` pour afficher les tokens au fil de l'eau
- **Whisper.cpp sur Windows** : le binaire natif existe, pas besoin de WSL pour cette partie
- **SQLite async** : utiliser `aiosqlite` + `SQLAlchemy async` pour éviter les blocages dans FastAPI
- **CORS** : FastAPI doit autoriser `localhost:5173` (Vite dev server) en développement

---

## Commande de démarrage suggérée

Commence par me générer :

1. `backend/requirements.txt` — toutes les dépendances Python avec versions pinées
2. `backend/main.py` — FastAPI app avec CORS, lifespan, et les 4 routers importés
3. `backend/services/ollama_client.py` — client Ollama avec support streaming et fallback
4. `backend/routers/chat.py` — endpoint POST /chat avec streaming SSE vers le frontend
5. `frontend/package.json` — dépendances React + Vite + TailwindCSS + PWA plugin
6. `frontend/src/hooks/useOllama.ts` — hook React pour consommer le stream SSE
7. `frontend/src/components/ChatWindow.tsx` — composant principal de conversation

Ensuite on avancera module par module selon le plan semaine par semaine.

---

## Ressources utiles

- Ollama API docs : https://github.com/ollama/ollama/blob/main/docs/api.md
- Gemma 4 sur Kaggle : https://www.kaggle.com/models/google/gemma-4
- Unsloth docs : https://docs.unsloth.ai
- Whisper.cpp : https://github.com/ggerganov/whisper.cpp
- Piper TTS : https://github.com/rhasspy/piper
- OPUS-100 dataset : https://huggingface.co/datasets/Helsinki-NLP/opus-100
- FLORES-200 : https://huggingface.co/datasets/facebook/flores
- Workbox PWA : https://developer.chrome.com/docs/workbox
- Kaggle competition : https://www.kaggle.com/competitions/gemma-4-good-hackathon

---

*Fichier généré le 20 avril 2026 — à utiliser comme contexte de démarrage pour Claude Code.*