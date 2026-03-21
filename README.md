<div align="center">
  <img src="assets/logo.svg" alt="GEMINI·UI·NAVIGATOR" width="520"/>
  <br/><br/>

  [![License: MIT](https://img.shields.io/badge/License-MIT-38BDF8?style=flat-square)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.11+-38BDF8?style=flat-square&logo=python&logoColor=black)](#)
  [![Gemini](https://img.shields.io/badge/Gemini_Live_API-Vision-4285F4?style=flat-square&logo=google)](#)
  [![Playwright](https://img.shields.io/badge/Playwright-web_automation-34D399?style=flat-square)](#)
  [![Voice](https://img.shields.io/badge/Voice-driven_navigation-38BDF8?style=flat-square)](#)

  <br/>
  <p><strong>Agent navigateur web vocal · Gemini Live API Vision · Playwright · Google Cloud</strong></p>
  <p><em>Naviguez sur le web par la voix — Gemini voit l'écran et execute les actions à votre place</em></p>
</div>

---

## Présentation

**GEMINI·UI·NAVIGATOR** est un agent navigateur web vocal propulsé par la **Gemini Live API** avec vision. Il "voit" l'interface web via la capture d'écran, comprend vos commandes vocales, et exécute les actions (clics, saisie, navigation) via Playwright — sans aucune intervention manuelle.

---

## Fonctionnalités

| Feature | Description |
|---------|-------------|
| **Vision web** | Gemini analyse l'écran en temps réel |
| **Commandes vocales** | "Clique sur connexion" → action exécutée |
| **Navigation** | "Va sur google.com" → Playwright navigue |
| **Formulaires** | "Remplis le champ email" → saisie auto |
| **Screenshot** | Capture + analyse à chaque étape |

---

## Architecture

```
Microphone → Gemini Live API (STT + Vision + LLM)
                    │
              Analyse screenshot        Playwright captures screen
              "Je vois un bouton…"      Gemini identifie les éléments
                    │
              Intent → Action
              ├── NAVIGATE → page.goto(url)
              ├── CLICK    → page.click(selector)
              ├── TYPE     → page.fill(selector, text)
              └── SCROLL   → page.scroll(direction)
                    │
              Confirmation vocale TTS
```

---

## Installation

```bash
git clone https://github.com/Turbo31150/gemini-ui-navigator-agent.git
cd gemini-ui-navigator-agent
pip install -r requirements.txt
playwright install chromium
export GOOGLE_API_KEY=AIza...
python main.py
```

---

<div align="center">

**Franc Delmas (Turbo31150)** · Google Cloud · Gemini Live API Vision · MIT License

</div>
