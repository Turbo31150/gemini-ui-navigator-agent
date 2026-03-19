# Navigator — AI Web Browser Agent

> **EN** | [FR](#version-française)
>
> ![Python](https://img.shields.io/badge/python-3.12-green)
> ![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash_Vision-blue)
> ![Playwright](https://img.shields.io/badge/browser-Playwright_Chromium-purple)
> ![Cloud](https://img.shields.io/badge/Google_Cloud-Run-orange)
> ![License](https://img.shields.io/badge/license-MIT-brightgreen)
>
> Voice-driven web navigation agent powered by **Gemini Live API** multimodal (audio + vision) on Google Cloud. Speak naturally to browse the web — the agent **sees the screen**, clicks, types, scrolls, and navigates for you.
>
> **Built for**: Gemini Live Agent Challenge — Category: UI Navigator
>
> ---
>
> ## Table of Contents
>
> 1. [Overview](#overview)
> 2. 2. [Architecture](#architecture)
>    3. 3. [Features](#features)
>       4. 4. [Google Cloud Services](#google-cloud-services)
>          5. 5. [Quick Start](#quick-start)
>             6. 6. [Deploy to Cloud Run](#deploy-to-cloud-run)
>                7. 7. [Project Structure](#project-structure)
>                   8. 8. [How It Works](#how-it-works)
>                      9. 9. [8 Browser Tools](#8-browser-tools)
>                         10. 10. [Voice Commands](#voice-commands)
>                             11. 11. [Tech Stack](#tech-stack)
>                                 12. 12. [Version Française](#version-française)
>                                    
>                                     13. ---
>                                    
>                                     14. ## Overview
>                                    
>                                     15. Navigator is a multimodal AI agent that **sees your browser screen** (not DOM) and controls it through voice commands. Because Gemini uses visual understanding rather than DOM parsing, it works on **any website** — including complex SPAs, canvas-based apps, and custom UIs.
>
> ---
>
> ## Architecture
>
> ```
> Browser (Mic / Speaker / Live View)
>               |
>          WebSocket
>               |
>   Cloud Run (FastAPI + Playwright)
>               |
>       Gemini Live API
>   (Gemini 2.5 Flash Native Audio + Vision)
>               |
>     Headless Chromium
>   (screenshots + Playwright actions)
> ```
>
> ---
>
> ## Features
>
> - **Voice control**: Speak naturally to navigate any website
> - - **Visual understanding**: Gemini sees browser screenshots, not DOM — works on any site
>   - - **Live browser view**: Watch the agent navigate in real-time
>     - - **Click indicators**: Purple dots show where the agent clicks
>       - - **8 browser tools**: click, type, scroll, navigate, go back, key press, read text, page info
>         - - **Interruption handling**: Cut the agent off anytime
>           - - **Transcript panel**: See all voice + tool interactions
>            
>             - ---
>
> ## Google Cloud Services
>
> | Service | Usage |
> |---------|-------|
> | **Vertex AI** | Gemini Live API — multimodal audio + vision streaming |
> | **Cloud Run** | Hosts FastAPI + Playwright headless Chromium |
> | **Cloud Build** | Builds Docker image with browser dependencies |
> | **Container Registry** | Stores the container image |
>
> ---
>
> ## Quick Start
>
> ```bash
> # 1. Clone
> git clone https://github.com/Turbo31150/gemini-ui-navigator-agent.git
> cd gemini-ui-navigator-agent
>
> # 2. Google Cloud credentials
> gcloud auth application-default login
> gcloud config set project YOUR_PROJECT_ID
> gcloud services enable aiplatform.googleapis.com
>
> # 3. Install dependencies
> pip install -r requirements.txt
> playwright install chromium
>
> # 4. Environment variables
> export PROJECT_ID="your-gcp-project-id"
> export LOCATION="us-central1"
>
> # 5. Run
> python -m src.main
> ```
>
> Open `http://localhost:8080`, click the microphone, and say **"Go to Wikipedia"**.
>
> ---
>
> ## Deploy to Cloud Run
>
> ```bash
> # Automated (includes Chromium build)
> chmod +x deploy/deploy.sh
> ./deploy/deploy.sh YOUR_PROJECT_ID us-central1
>
> # Manual
> gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gemini-ui-navigator-agent --timeout=900
> gcloud run deploy gemini-ui-navigator-agent \
>   --image gcr.io/YOUR_PROJECT_ID/gemini-ui-navigator-agent \
>   --region us-central1 \
>   --memory 1Gi \
>   --cpu 2 \
>   --session-affinity
> ```
>
> ---
>
> ## Project Structure
>
> ```
> gemini-ui-navigator-agent/
> ├── public/
> │   └── index.html          # Frontend (browser view + mic + transcript)
> ├── src/
> │   ├── main.py             # FastAPI server + WebSocket endpoint
> │   ├── config.py           # Configuration
> │   └── agents/
> │       └── navigator.py    # Gemini Live session (audio + screenshots)
> │   └── tools/
> │       └── browser_tools.py # 8 Playwright browser tools + BrowserManager
> ├── deploy/
> │   ├── deploy.sh           # Automated Cloud Run deployment
> │   └── cleanup.sh          # Cleanup script
> ├── docs/
> │   └── architecture.md     # Architecture diagram
> ├── Dockerfile              # Cloud Run container (includes Chromium)
> └── requirements.txt        # Python dependencies
> ```
>
> ---
>
> ## How It Works
>
> 1. User speaks — "Go to Wikipedia and search machine learning"
> 2. 2. Audio streams to Cloud Run via WebSocket
>    3. 3. Playwright takes **screenshots** of headless Chromium (1 FPS)
>       4. 4. Screenshots sent to Gemini via Live API as media input
>          5. 5. Gemini **sees the page** + hears the user — decides on actions
>             6. 6. Tool calls executed — navigate, click, type via Playwright
>                7. 7. New screenshot captured — sent to Gemini and frontend
>                   8. 8. Gemini responds vocally — "I found the page, here's what it says..."
>                      9. 9. Frontend shows **live browser view** + transcripts + action indicators
>                        
>                         10. ---
>                        
>                         11. ## 8 Browser Tools
>                        
>                         12. | Tool | Description |
> |------|-------------|
> | `navigate` | Go to a URL |
> | `click` | Click at specific position (purple dot indicator) |
> | `type` | Type text in focused element |
> | `scroll` | Scroll up/down/left/right |
> | `go_back` | Browser back navigation |
> | `key_press` | Press keyboard keys (Enter, Escape, Tab...) |
> | `read_text` | Extract text from current page |
> | `get_page_info` | Get current URL + page title |
>
> ---
>
> ## Voice Commands
>
> ```
> "Go to Wikipedia"
> "Search for artificial intelligence"
> "Click on the first result"
> "Scroll down"
> "Go back to the previous page"
> "What does this page say?"
> "Navigate to news.ycombinator.com"
> "Type my search term in the login field"
> "Press Enter"
> ```
>
> ---
>
> ## Tech Stack
>
> | Layer | Technology |
> |-------|-----------|
> | **AI** | Gemini 2.5 Flash (Native Audio + Vision) via Vertex AI |
> | **SDK** | Google GenAI SDK (google-genai >= 1.44.0) |
> | **Backend** | Python 3.12, FastAPI, uvicorn |
> | **Browser** | Playwright (headless Chromium) |
> | **Frontend** | Vanilla HTML/JS, Web Audio API, WebSocket |
> | **Hosting** | Google Cloud Run (Docker with Chromium) |
>
> ---
>
> *Author: Turbo31150 | Challenge: Gemini Live Agent Challenge | Category: UI Navigator | License: MIT*
>
> ---
> ---
>
> # Version Française
>
> > [EN](#navigator--ai-web-browser-agent) | **FR**
> >
> > ![Python](https://img.shields.io/badge/python-3.12-green)
> > ![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash_Vision-blue)
> > ![Playwright](https://img.shields.io/badge/navigateur-Playwright_Chromium-purple)
> > ![Cloud](https://img.shields.io/badge/Google_Cloud-Run-orange)
> > ![Licence](https://img.shields.io/badge/licence-MIT-brightgreen)
> >
> > Agent de navigation web piloté par la voix, propulsé par **Gemini Live API** multimodal (audio + vision) sur Google Cloud. Parlez naturellement pour naviguer sur le web — l'agent **voit l'écran**, clique, tape, fait défiler et navigue pour vous.
> >
> > **Conçu pour** : Gemini Live Agent Challenge — Catégorie : UI Navigator
> >
> > ---
> >
> > ## Table des matières FR
> >
> > 1. [Vue d'ensemble](#vue-densemble-fr)
> > 2. 2. [Architecture](#architecture-fr)
> >    3. 3. [Fonctionnalités](#fonctionnalités-fr)
> >       4. 4. [Services Google Cloud](#services-google-cloud-fr)
> >          5. 5. [Démarrage rapide](#démarrage-rapide-fr)
> >             6. 6. [Déploiement Cloud Run](#déploiement-cloud-run-fr)
> >                7. 7. [Structure du projet](#structure-du-projet-fr)
> >                   8. 8. [Fonctionnement](#fonctionnement-fr)
> >                      9. 9. [8 outils navigateur](#8-outils-navigateur)
> >                         10. 10. [Commandes vocales](#commandes-vocales-fr)
> >                             11. 11. [Stack technique](#stack-technique-fr)
> >                                
> >                                 12. ---
> >                                
> >                                 13. ## Vue d'ensemble FR
> >                                
> >                                 14. Navigator est un agent IA multimodal qui **voit votre écran de navigateur** (pas le DOM) et le contrôle via des commandes vocales. Parce que Gemini utilise la compréhension visuelle plutôt que l'analyse du DOM, il fonctionne sur **n'importe quel site** — y compris les SPAs complexes, les apps canvas et les UIs personnalisées.
> >
> > ---
> >
> > ## Architecture FR
> >
> > ```
> > Navigateur (Micro / Haut-parleur / Vue Live)
> >               |
> >          WebSocket
> >               |
> >   Cloud Run (FastAPI + Playwright)
> >               |
> >       Gemini Live API
> >   (Gemini 2.5 Flash Audio Natif + Vision)
> >               |
> >     Chromium Headless
> >   (captures d'écran + actions Playwright)
> > ```
> >
> > ---
> >
> > ## Fonctionnalités FR
> >
> > - **Contrôle vocal** : Parlez naturellement pour naviguer sur n'importe quel site
> > - - **Compréhension visuelle** : Gemini voit les captures d'écran du navigateur, pas le DOM — fonctionne sur tout site
> >   - - **Vue navigateur live** : Regardez l'agent naviguer en temps réel
> >     - - **Indicateurs de clic** : Points violets montrant où l'agent clique
> >       - - **8 outils navigateur** : clic, frappe, défilement, navigation, retour, touche, lecture texte, info page
> >         - - **Interruption** : Coupez l'agent à tout moment
> >           - - **Panneau transcript** : Voir toutes les interactions voix + outils
> >            
> >             - ---
> >
> > ## Services Google Cloud FR
> >
> > | Service | Usage |
> > |---------|-------|
> > | **Vertex AI** | Gemini Live API — streaming multimodal audio + vision |
> > | **Cloud Run** | Héberge FastAPI + Playwright Chromium headless |
> > | **Cloud Build** | Construit l'image Docker avec dépendances navigateur |
> > | **Container Registry** | Stocke l'image du conteneur |
> >
> > ---
> >
> > ## Démarrage rapide FR
> >
> > ```bash
> > # 1. Cloner
> > git clone https://github.com/Turbo31150/gemini-ui-navigator-agent.git
> > cd gemini-ui-navigator-agent
> >
> > # 2. Credentials Google Cloud
> > gcloud auth application-default login
> > gcloud config set project YOUR_PROJECT_ID
> > gcloud services enable aiplatform.googleapis.com
> >
> > # 3. Installer les dépendances
> > pip install -r requirements.txt
> > playwright install chromium
> >
> > # 4. Variables d'environnement
> > export PROJECT_ID="votre-projet-gcp"
> > export LOCATION="us-central1"
> >
> > # 5. Lancer
> > python -m src.main
> > ```
> >
> > Ouvrez `http://localhost:8080`, cliquez sur le micro et dites **"Va sur Wikipedia"**.
> >
> > ---
> >
> > ## Déploiement Cloud Run FR
> >
> > ```bash
> > # Automatisé (inclut le build Chromium)
> > chmod +x deploy/deploy.sh
> > ./deploy/deploy.sh YOUR_PROJECT_ID us-central1
> > ```
> >
> > ---
> >
> > ## Structure du projet FR
> >
> > ```
> > gemini-ui-navigator-agent/
> > ├── public/
> > │   └── index.html          # Frontend (vue navigateur + micro + transcript)
> > ├── src/
> > │   ├── main.py             # Serveur FastAPI + endpoint WebSocket
> > │   ├── config.py           # Configuration
> > │   └── agents/
> > │       └── navigator.py    # Session Gemini Live (audio + captures d'écran)
> > │   └── tools/
> > │       └── browser_tools.py # 8 outils Playwright + BrowserManager
> > ├── deploy/
> > │   ├── deploy.sh           # Déploiement Cloud Run automatisé
> > │   └── cleanup.sh          # Script de nettoyage
> > ├── docs/
> > │   └── architecture.md     # Schéma d'architecture
> > ├── Dockerfile              # Conteneur Cloud Run (inclut Chromium)
> > └── requirements.txt        # Dépendances Python
> > ```
> >
> > ---
> >
> > ## Fonctionnement FR
> >
> > 1. L'utilisateur parle — "Va sur Wikipedia et cherche machine learning"
> > 2. 2. L'audio est streamé vers Cloud Run via WebSocket
> >    3. 3. Playwright prend des **captures d'écran** de Chromium headless (1 FPS)
> >       4. 4. Les captures sont envoyées à Gemini via Live API en tant qu'entrée média
> >          5. 5. Gemini **voit la page** + entend l'utilisateur — décide des actions
> >             6. 6. Appels d'outils exécutés — naviguer, cliquer, taper via Playwright
> >                7. 7. Nouvelle capture prise — envoyée à Gemini et au frontend
> >                   8. 8. Gemini répond vocalement — "J'ai trouvé la page, voici ce qu'elle dit..."
> >                      9. 9. Le frontend affiche la **vue navigateur live** + transcripts + indicateurs d'actions
> >                        
> >                         10. ---
> >                        
> >                         11. ## 8 outils navigateur
> >                        
> >                         12. | Outil | Description |
> > |-------|-------------|
> > | `navigate` | Aller à une URL |
> > | `click` | Cliquer à une position précise (indicateur point violet) |
> > | `type` | Taper du texte dans l'élément actif |
> > | `scroll` | Faire défiler haut/bas/gauche/droite |
> > | `go_back` | Navigation retour du navigateur |
> > | `key_press` | Appuyer sur des touches (Entrée, Echap, Tab...) |
> > | `read_text` | Extraire le texte de la page courante |
> > | `get_page_info` | Obtenir l'URL courante + titre de la page |
> >
> > ---
> >
> > ## Commandes vocales FR
> >
> > ```
> > "Va sur Wikipedia"
> > "Cherche intelligence artificielle"
> > "Clique sur le premier résultat"
> > "Fais défiler vers le bas"
> > "Reviens à la page précédente"
> > "Que dit cette page ?"
> > "Navigue vers news.ycombinator.com"
> > "Tape mon terme de recherche dans le champ"
> > "Appuie sur Entrée"
> > ```
> >
> > ---
> >
> > ## Stack technique FR
> >
> > | Couche | Technologie |
> > |--------|-------------|
> > | **IA** | Gemini 2.5 Flash (Audio Natif + Vision) via Vertex AI |
> > | **SDK** | Google GenAI SDK (google-genai >= 1.44.0) |
> > | **Backend** | Python 3.12, FastAPI, uvicorn |
> > | **Navigateur** | Playwright (Chromium headless) |
> > | **Frontend** | Vanilla HTML/JS, Web Audio API, WebSocket |
> > | **Hébergement** | Google Cloud Run (Docker avec Chromium) |
> >
> > ---
> >
> > *Auteur : Turbo31150 | Challenge : Gemini Live Agent Challenge | Catégorie : UI Navigator | Licence : MIT*
