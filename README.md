# 🎙️ Empathy Engine: Neural Expressive TTS

> **Emotionally intelligent Text-to-Speech — because how something is said matters as much as what is said.**

The **Empathy Engine** is a full-stack AI application that bridge the gap between text and human feeling. It analyzes the emotional subtext of input and dynamically modulates a Neural TTS voice to match the mood of the message.

---

## ✨ Features

| Feature | Status |
| :--- | :--- |
| **Multi-emotion detection** | ✅ Joy, Sad, Anger, Fear, Surprise, Inquisitive, Calm |
| **Contextual Logic** | ✅ Handles negators ("not happy") and intensifiers ("very") |
| **Neural Human Voice** | ✅ Powered by Microsoft Azure Neural TTS (Aria) |
| **Intensity Scaling** | ✅ Mild to extreme vocal modulation (0.0 to 1.0) |
| **Modern Web UI** | ✅ Dark-themed dashboard with live audio and score charts |
| **SSML Generation** | ✅ Dynamic `<prosody>` and `<emphasis>` tagging |

---

## 🚀 Quick Start

### 1. Environment Setup
Clone the repository and move into the project directory:
```bash
git clone <your-repository-url>
cd myflaskapp
Create and activate a virtual environment:Bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
2. Install DependenciesBashpip install flask edge-tts asyncio
3. Folder ArrangementEnsure your files are organized exactly like this for Flask to function:Plaintextmyflaskapp/
├── app.py              # Backend Logic & Emotion Engine
├── templates/
│   └── index.html      # Frontend Dashboard
├── static/
│   └── audio/          # Output directory for voice files
├── requirements.txt    # List of dependencies
└── README.md           # This file
4. Run the ApplicationBashpython app.py
Open your browser to http://localhost:5000.🧠 Design: The Emotion-to-Voice LogicThe core "intelligence" of the engine lies in the Vocal Parameter Mapping. We translate emotional intensity ($I$) into physical voice attributes using a linear scaling formula:$$Parameter_{final} = 1.0 + (Base_{emotion} - 1.0) \times I$$Voice Profiles (Intensity = 1.0)EmotionRatePitchVolumeCharacteristicJoy1.15x1.20x1.10xUpbeat, fast, energeticSadness0.85x0.85x0.85xSlow, low, and mutedAnger1.10x0.90x1.25xForceful, low-pitch, high-volumeFear1.05x1.10x0.90xTense, rapid, and hushedContextual AnalysisNegation Handling: The engine scans for tokens like "not" or "never." If detected within two words of an emotion, it flips the target (e.g., "not happy" $\rightarrow$ Sadness).Intensifier Detection: Words like "extremely" or "really" act as multipliers, pushing the intensity closer to 1.0.🔧 Technical Stack ValidationSentiment Analysis: Custom weighted-lexicon scoring engine.Neural TTS: edge-tts (Microsoft Neural Engine) for high-fidelity human prosody.Backend: Flask (Python) with asyncio for non-blocking audio generation.Frontend: HTML5/CSS3 with modern CSS variables and Vanilla JS.📂 Submission DetailsAuthor: Kanikella Pramodh SaiInstitution: IIT PalakkadProject Goal: Demonstrate expressive human-computer interaction through neural voice modulation.
