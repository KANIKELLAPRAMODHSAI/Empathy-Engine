
=======
# 🎙️ Empathy Engine

> **Emotionally expressive Text-to-Speech — because how something is said matters as much as what is said.**

The Empathy Engine analyzes the emotional content of text and dynamically modulates vocal parameters — rate, pitch, and volume — to generate expressive, human-like audio. It supports **8 distinct emotional states** with **intensity scaling**, a **web UI**, and **SSML generation**.

---

## ✨ Features

| Feature | Status |
|---|---|
| Multi-emotion detection (8 categories) | ✅ |
| Intensity scaling (mild → extreme) | ✅ |
| 3 vocal parameters modulated | ✅ |
| SSML with `<prosody>` + `<emphasis>` | ✅ |
| Web UI with live audio player | ✅ |
| REST API (`/api/synthesize`) | ✅ |
| CLI mode | ✅ |
| Zero required API keys | ✅ |
| Pure-Python audio fallback | ✅ |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <your-repo-url>
cd empathy-engine
pip install -r requirements.txt
```

### 2. Install a TTS engine (optional but recommended)

**Best quality (offline):**
```bash
# Ubuntu/Debian
sudo apt-get install espeak-ng

# macOS
brew install espeak-ng
```

> Without a TTS engine, the app falls back to a pure-Python synthesizer that encodes emotion through audio characteristics. Great for demos!

### 3. Run the web server

```bash
python app.py
```

Open **http://localhost:5000** in your browser. Type any text, hit **Synthesize**, and hear the emotion.

### 4. CLI mode

```bash
# Interactive
python app.py --cli

# Direct input
python app.py "This is absolutely the best news I've heard all year!"
```

---

## 🌐 REST API

### `POST /api/synthesize`

**Request:**
```json
{ "text": "This is absolutely the best news I've heard all year!" }
```

**Response:**
```json
{
  "emotion": "joy",
  "intensity": 0.85,
  "emotion_scores": {
    "joy": 0.78,
    "surprise": 0.14,
    "neutral": 0.08
  },
  "voice_params": {
    "rate": 1.12,
    "pitch": 1.17,
    "volume": 1.08,
    "description": "Upbeat and energetic"
  },
  "ssml": "<speak><prosody rate=\"112%\" pitch=\"+0.9st\" volume=\"+0.5dB\"><emphasis level=\"strong\">...</emphasis></prosody></speak>",
  "audio_url": "/static/audio/abc123.wav"
}
```

### `GET /api/emotions`

Returns the full emotion → voice parameter mapping table.

---

## 🧠 Design: Emotion Detection

The engine uses a **lexicon-based approach with contextual modifiers** — no external API or model download required.

### How it works

1. **Tokenization** — Text is split into words (lowercased).
2. **Lexicon lookup** — Each word is checked against ~120 emotion-tagged entries. Each entry has an emotion label and a base confidence score (0.0–1.0).
3. **Intensifier scaling** — Words like _very_, _extremely_, _incredibly_ multiply the following word's score (up to 1.5×).
4. **Negation handling** — Words like _not_, _never_, _don't_ within 2 tokens flip the emotion to its opposite with reduced confidence.
5. **Punctuation signals** — `!` boosts joy/anger/surprise; `?` boosts inquisitive; `...` boosts sadness; `ALL CAPS` words amplify the dominant emotion.
6. **Score normalization** — All emotion scores are normalized to sum to 1.0 (probability distribution).
7. **Intensity extraction** — Raw accumulated score is mapped to a 0–1 intensity scale.

### Supported Emotions

| Emotion | Voice Delivery | Example trigger words |
|---|---|---|
| 😄 Joy | Upbeat, faster, louder | happy, amazing, thrilled, best |
| 😢 Sadness | Slower, softer, lower pitch | sad, disappointed, grief, terrible |
| 😤 Anger | Forceful, clipped, louder | furious, unacceptable, demand, hate |
| 😰 Fear | Tense, hushed, slightly higher | worried, afraid, anxious, nervous |
| 😲 Surprise | Quick, high pitch, breathy | unbelievable, wow, shocking, whoa |
| 🤔 Inquisitive | Thoughtful, rising inflection | wondering, curious, why, perhaps |
| 😌 Calm | Smooth, measured, quieter | relax, peaceful, breathe, gentle |
| 😐 Neutral | Standard delivery | (no strong emotion detected) |

---

## 🎛️ Design: Emotion → Voice Mapping

### Base Parameters (at intensity = 1.0)

| Emotion | Rate | Pitch | Volume |
|---|---|---|---|
| Joy | 1.15× | 1.20× | 1.10× |
| Sadness | 0.85× | 0.85× | 0.85× |
| Anger | 1.10× | 0.90× | 1.25× |
| Fear | 1.05× | 1.10× | 0.90× |
| Surprise | 1.20× | 1.25× | 1.05× |
| Inquisitive | 0.95× | 1.10× | 0.95× |
| Calm | 0.90× | 0.95× | 0.90× |
| Neutral | 1.00× | 1.00× | 1.00× |

### Intensity Scaling

Each parameter is interpolated between neutral (1.0×) and its base value using the detected intensity:

```
final_param = 1.0 + (base_param - 1.0) × intensity
```

**Example: Joy at intensity 0.4 vs 0.95**

| Intensity | Rate | Pitch | Volume |
|---|---|---|---|
| 0.4 (mild) | 1.06× | 1.08× | 1.04× |
| 0.95 (strong) | 1.14× | 1.19× | 1.09× |

This means "That's good" gets a gentle upward inflection, while "THIS IS THE BEST DAY EVER!!!" gets dramatically higher pitch and faster delivery.

---

## 📝 SSML Generation

For each synthesis, the engine generates SSML using `<prosody>` for rate/pitch/volume and `<emphasis>` for high-intensity emotions:

```xml
<!-- High intensity joy -->
<speak>
  <prosody rate="115%" pitch="+1.0st" volume="+0.5dB">
    <emphasis level="strong">This is the best news ever!</emphasis>
  </prosody>
</speak>
```

The SSML is displayed in the web UI and returned in the API response for use with cloud TTS providers (Google Cloud TTS, AWS Polly, etc.) that support SSML input.

---

## 🔧 TTS Backend Priority

The engine tries backends in order:

1. **espeak-ng** — Best quality offline TTS. Accepts rate (words/min), pitch (0–99), amplitude (0–200) parameters directly.
2. **festival** — Alternative offline fallback.
3. **Pure Python WAV synthesizer** — Always available. Uses harmonic synthesis + vibrato + syllabic envelope to encode emotion in the audio waveform itself. No external dependencies.

---

## 📁 Project Structure

```
empathy-engine/
├── app.py              # Main Flask app + emotion detection + TTS
├── requirements.txt    # Python dependencies (just Flask!)
├── README.md           # This file
├── templates/
│   └── index.html      # Web UI
└── static/
    └── audio/          # Generated WAV files (auto-created)
```

---

## 🎯 Bonus Objectives Completed

- ✅ **Granular Emotions** — 8 states including inquisitive, fear, surprise
- ✅ **Intensity Scaling** — Linear interpolation from neutral to max modulation
- ✅ **Web Interface** — Full-featured UI with audio player, parameter dials, score breakdown
- ✅ **SSML Integration** — `<prosody>` + `<emphasis>` generated for every synthesis
- ✅ **Negation Handling** — "not happy" correctly shifts away from joy
- ✅ **Intensifier Detection** — "very happy" vs "extremely ecstatic" produce different intensities
- ✅ **Zero API keys** — Fully offline capable

---

