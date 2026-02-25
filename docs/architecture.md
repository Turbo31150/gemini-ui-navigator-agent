# Architecture Diagram — UI Navigator Agent

## System Overview

```
+--------------------------------------------------+
|                   USER (Browser)                  |
|                                                   |
|  +-------------+  +------------+  +------------+  |
|  | Microphone  |  |  Speaker   |  | Browser    |  |
|  | (16kHz PCM) |  |  (24kHz)   |  | View       |  |
|  +------+------+  +-----^------+  | (live      |  |
|         |               |         | screenshots|  |
|         v               |         +-----^------+  |
|  +------+---------------+--------------+-------+  |
|  |            WebSocket (wss://)                |  |
|  |   Binary = PCM audio                        |  |
|  |   JSON   = events, screenshots, tool calls  |  |
|  +------+--------------------^------------------+  |
+---------+--------------------+---------------------+
          |                    |
          v                    |
+---------+--------------------+---------------------+
|              Google Cloud Run                       |
|                                                     |
|  +-----------------------------------------------+ |
|  |          FastAPI Server (Python)               | |
|  |                                                | |
|  |  /ws          WebSocket proxy                  | |
|  |  /api/health  Health check                     | |
|  |  /            Static frontend                  | |
|  +------+--------------------------^--------------+ |
|         |                          |                |
|  +------v--------------------------+--------------+ |
|  |          NavigatorSession                      | |
|  |                                                | |
|  |  audio_input --> Gemini Live API               | |
|  |  screenshots --> Gemini Live API (media)       | |
|  |  Gemini responses --> audio + tool calls       | |
|  +------+--------------------------^--------------+ |
|         |                          |                |
|  +------v---------+    +----------+--------------+  |
|  | Playwright      |    | Gemini Live API        |  |
|  | Headless Browser|    | (Vertex AI)            |  |
|  |                 |    |                        |  |
|  | - Screenshots   |    | Model: gemini-live-    |  |
|  | - Click(x,y)    |    |   2.5-flash-native-   |  |
|  | - Type(text)    |    |   audio                |  |
|  | - Scroll        |    |                        |  |
|  | - Navigate(url) |    | Features:              |  |
|  | - Go back       |    | - Audio bidirectional  |  |
|  | - Key press     |    | - Vision (screenshots) |  |
|  | - Read text     |    | - Function calling     |  |
|  +-----------------+    | - Transcription        |  |
|                         +------------------------+  |
+---------+-------------------------------------------+
          |
          v
+---------+-------------------------------------------+
|                   Internet                          |
|   Any website the user asks to navigate to          |
+-----------------------------------------------------+
```

## Data Flow

```
1. User speaks: "Go to Wikipedia and search machine learning"
   Browser captures audio at 16kHz PCM16
   Sends as binary WebSocket frame to Cloud Run

2. Server takes periodic screenshots of Playwright browser (1 FPS)
   Sends JPEG to Gemini Live API as media input
   Also sends screenshots to frontend for display

3. Gemini receives audio + screenshot simultaneously
   Understands the voice command AND sees the current page
   Decides to call navigate_to("https://www.wikipedia.org")

4. Server executes action on Playwright
   Playwright navigates to Wikipedia
   New screenshot captured and sent to Gemini + frontend

5. Gemini sees the Wikipedia homepage
   Calls click_element(x=500, y=250) on the search bar
   Then type_text("machine learning", press_enter=true)

6. Gemini confirms via voice
   "I found the Machine Learning page on Wikipedia"
   Audio streamed back to browser speaker

7. Frontend displays
   - Live browser screenshots (updated each second)
   - Voice transcriptions
   - Tool call log (click, type, navigate actions)
   - Click indicators (purple dots on click positions)
```

## Google Cloud Services Used

| Service | Purpose |
|---------|---------|
| **Cloud Run** | Hosts FastAPI + Playwright headless browser |
| **Vertex AI** | Gemini Live API (audio + vision multimodal) |
| **Cloud Build** | Builds Docker image with Chromium |
| **Container Registry** | Stores the container image |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vanilla HTML/JS, WebSocket, Web Audio API |
| Backend | Python 3.12, FastAPI, uvicorn |
| Browser Engine | Playwright (headless Chromium) |
| AI Model | Gemini 2.5 Flash (Native Audio + Vision) |
| SDK | Google GenAI SDK (`google-genai`) |
| Hosting | Google Cloud Run (Docker) |
| Coordinates | 1000x1000 normalized grid |
