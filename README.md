# 🎙️ Empathy Engine: Neural Expressive TTS

The **Empathy Engine** is an emotionally intelligent Text-to-Speech service. It does not simply convert text into audio; it interprets emotional subtext and modulates voice rate, pitch, and volume to produce speech that sounds genuinely human.

---

## ✨ Features

* **Emotion Detection:** Custom weighted-lexicon engine that understands context, including negators and intensifiers
* **Neural Human Voice:** Uses Microsoft Azure Neural TTS for high-fidelity speech
* **Real-time Modulation:** Dynamically calculates vocal prosody using a 0.0–1.0 intensity scale
* **Modern Web Dashboard:** Dark-mode interface with live audio playback and emotional score visualization
* **SSML Integration:** Automatically generates Speech Synthesis Markup Language tags for every request

---

## 🚀 Installation & Setup

### 1. Prerequisites

* Python 3.10+
* Active internet connection (required for neural voice synthesis)

---

### 2. Environment Setup

Clone the repository and move into the project directory:

```bash id="a4m72k"
git clone <your-repository-url>
cd myflaskapp
```

Create and activate a virtual environment:

```bash id="b8q31v"
python -m venv venv
source venv/bin/activate
```

For Windows:

```bash id="c6w95t"
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash id="d2r48x"
pip install flask edge-tts asyncio
```

---

### 4. Folder Structure

Ensure files are organized exactly like this:

```plaintext id="e7p13n"
myflaskapp/
├── app.py              # Backend logic & Emotion Engine
├── templates/
│   └── index.html      # Frontend Dashboard UI
├── static/
│   └── audio/          # Directory for generated .wav files
├── README.md
└── requirements.txt
```

---

## ▶️ Running the Application

Start the Flask server:

```bash id="f5t84m"
python app.py
```

Open in browser:

```plaintext id="g3x29r"
http://localhost:5000
```

---

## 🧠 Design Choices & Logic

### 1. Emotion-to-Voice Mapping

The core of the empathy engine uses a linear scaling formula.

A neutral baseline of **1.0** is defined for:

* Rate
* Pitch
* Volume

For each detected emotion, parameters shift according to detected intensity (**I**):

[
Parameter_{final} = 1.0 + (Base_{emotion} - 1.0) \times I
]

---

### Emotion Profiles

| Emotion | Rate  | Pitch | Volume | Characteristic                  |
| ------- | ----- | ----- | ------ | ------------------------------- |
| Joy     | 1.15x | 1.20x | 1.10x  | Upbeat and energetic            |
| Sadness | 0.85x | 0.85x | 0.85x  | Slow, low, and muted            |
| Anger   | 1.10x | 0.90x | 1.25x  | Low-pitch, high volume, clipped |
| Fear    | 1.05x | 1.10x | 0.90x  | Tense and hushed                |

---

### 2. Contextual Awareness

* **Negation:**
  `"I am not happy"` shifts interpretation from Joy to Sadness

* **Intensifiers:**
  Words like `"extremely"` increase intensity and push values closer to 1.0, producing stronger vocal changes

---

### 3. Neural Humanization

The engine originally used traditional formant synthesis, which produced robotic output.

It was upgraded to **Neural TTS** using:

* `en-US-AriaNeural`

This deep-learning voice model allows mathematical parameter shifts to sound natural and expressive instead of mechanical.

---

## 🛠️ Built With

* Flask
* edge-tts
* Python
* Jinja2
