# Navigator — AI Web Browser Agent

Voice-driven web navigation agent powered by **Gemini Live API** multimodal (audio + vision) on **Google Cloud**.

Speak naturally to browse the web — the agent sees the screen, clicks, types, scrolls, and navigates for you.

## Architecture

```
Browser (Mic/Speaker/View) <--WebSocket--> Cloud Run (FastAPI + Playwright) <--Live API--> Gemini 2.5 Flash
                                                    |
                                            Headless Chromium
                                          (screenshots + actions)
```

See [docs/architecture.md](docs/architecture.md) for the full architecture diagram.

## Features

- **Voice control**: Speak naturally to navigate any website
- **Visual understanding**: Gemini sees browser screenshots, not DOM — works on any site
- **Live browser view**: Watch the agent navigate in real-time
- **Click indicators**: Purple dots show where the agent clicks
- **8 browser tools**: click, type, scroll, navigate, go back, key press, read text, page info
- **Interruption handling**: Cut the agent off anytime
- **Transcript panel**: See all voice + tool interactions

## Google Cloud Services

| Service | Usage |
|---------|-------|
| **Vertex AI** | Gemini Live API — multimodal audio + vision streaming |
| **Cloud Run** | Hosts FastAPI + Playwright headless Chromium |
| **Cloud Build** | Builds Docker image with browser dependencies |
| **Container Registry** | Stores the container image |

## Prerequisites

- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- [Python 3.11+](https://www.python.org/downloads/)
- A Google Cloud project with billing enabled
- Vertex AI API enabled

## Quick Start (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/gemini-ui-navigator-agent.git
cd gemini-ui-navigator-agent
```

### 2. Set up Google Cloud credentials

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 5. Set environment variables

```bash
export PROJECT_ID="your-gcp-project-id"
export LOCATION="us-central1"
```

### 6. Run the server

```bash
python -m src.main
```

Open [http://localhost:8080](http://localhost:8080), click the microphone, and say "Go to Wikipedia".

## Deploy to Google Cloud Run

### Automated deployment

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh YOUR_PROJECT_ID us-central1
```

### Manual deployment

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gemini-ui-navigator-agent --timeout=900

gcloud run deploy gemini-ui-navigator-agent \
    --image gcr.io/YOUR_PROJECT_ID/gemini-ui-navigator-agent \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=YOUR_PROJECT_ID,LOCATION=us-central1" \
    --memory 1Gi \
    --cpu 2 \
    --session-affinity
```

## Project Structure

```
2-ui-navigator/
  public/
    index.html              # Frontend (browser view + mic + transcript)
  src/
    main.py                 # FastAPI server + WebSocket endpoint
    config.py               # Configuration
    agents/
      navigator.py          # Gemini Live session (audio + screenshots)
    tools/
      browser_tools.py      # 8 Playwright browser tools + BrowserManager
  deploy/
    deploy.sh               # Automated Cloud Run deployment
    cleanup.sh              # Cleanup script
  docs/
    architecture.md         # Architecture diagram
  Dockerfile                # Cloud Run container (includes Chromium)
  requirements.txt          # Python dependencies
```

## How It Works

1. **User speaks** — "Go to Wikipedia and search machine learning"
2. **Audio streams** to Cloud Run via WebSocket
3. **Playwright takes screenshots** of headless Chromium (1 FPS)
4. **Screenshots sent to Gemini** via Live API as media input
5. **Gemini sees the page + hears the user** — decides on actions
6. **Tool calls executed** — navigate, click, type via Playwright
7. **New screenshot captured** — sent to Gemini and frontend
8. **Gemini responds vocally** — "I found the page, here's what it says..."
9. **Frontend shows** live browser view + transcripts + action indicators

## Example Voice Commands

- "Go to Wikipedia"
- "Search for artificial intelligence"
- "Click on the first result"
- "Scroll down"
- "Go back to the previous page"
- "What does this page say?"
- "Navigate to news.ycombinator.com"
- "Type my email address in the login field"

## Tech Stack

- **AI**: Gemini 2.5 Flash (Native Audio + Vision) via Vertex AI
- **SDK**: Google GenAI SDK (`google-genai>=1.44.0`)
- **Backend**: Python 3.12, FastAPI, uvicorn
- **Browser**: Playwright (headless Chromium)
- **Frontend**: Vanilla HTML/JS, Web Audio API, WebSocket
- **Hosting**: Google Cloud Run (Docker with Chromium)

## Built for

[Gemini Live Agent Challenge](https://devpost.com/) — Category: UI Navigator

## License

MIT
