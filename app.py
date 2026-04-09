"""
Empathy Engine - Emotionally Expressive TTS Service
Detects emotion in text and modulates voice parameters accordingly.
"""
import os
import re
import uuid
import json
import math
import struct
import wave
import subprocess
import tempfile
import asyncio        
import edge_tts      
from flask import Flask, request, jsonify, render_template, send_from_directory


EMOTION_LEXICON = {
    # Joy / Happiness
    "happy": ("joy", 0.8), "wonderful": ("joy", 0.9), "amazing": ("joy", 0.95),
    "fantastic": ("joy", 0.9), "great": ("joy", 0.7), "love": ("joy", 0.85),
    "excited": ("joy", 0.9), "thrilled": ("joy", 0.95), "delighted": ("joy", 0.85),
    "awesome": ("joy", 0.85), "brilliant": ("joy", 0.8), "excellent": ("joy", 0.8),
    "best": ("joy", 0.75), "perfect": ("joy", 0.85), "celebrate": ("joy", 0.9),
    "congratulations": ("joy", 0.9), "hooray": ("joy", 0.95), "yay": ("joy", 0.9),
    "good": ("joy", 0.5), "nice": ("joy", 0.5), "glad": ("joy", 0.65),

    # Sadness
    "sad": ("sadness", 0.8), "sorry": ("sadness", 0.6), "unfortunate": ("sadness", 0.75),
    "terrible": ("sadness", 0.85), "awful": ("sadness", 0.85), "horrible": ("sadness", 0.9),
    "disappointed": ("sadness", 0.8), "regret": ("sadness", 0.75), "miss": ("sadness", 0.65),
    "lost": ("sadness", 0.6), "broken": ("sadness", 0.7), "cry": ("sadness", 0.85),
    "grief": ("sadness", 0.9), "heartbroken": ("sadness", 0.95), "depressed": ("sadness", 0.9),
    "lonely": ("sadness", 0.75), "pain": ("sadness", 0.7), "hurt": ("sadness", 0.7),

    # Anger / Frustration
    "angry": ("anger", 0.85), "frustrated": ("anger", 0.8), "furious": ("anger", 0.95),
    "annoyed": ("anger", 0.7), "outraged": ("anger", 0.9), "unacceptable": ("anger", 0.85),
    "ridiculous": ("anger", 0.8), "hate": ("anger", 0.85), "worst": ("anger", 0.8),
    "disgusting": ("anger", 0.85), "infuriating": ("anger", 0.9), "demand": ("anger", 0.75),
    "enough": ("anger", 0.65), "stop": ("anger", 0.6), "stupid": ("anger", 0.8),

    # Fear / Concern
    "worried": ("fear", 0.75), "afraid": ("fear", 0.85), "scared": ("fear", 0.85),
    "nervous": ("fear", 0.7), "anxious": ("fear", 0.8), "concerned": ("fear", 0.65),
    "terrified": ("fear", 0.95), "panic": ("fear", 0.9), "danger": ("fear", 0.8),
    "risk": ("fear", 0.6), "warning": ("fear", 0.65), "careful": ("fear", 0.5),
    "uncertain": ("fear", 0.6), "doubt": ("fear", 0.55),

    # Surprise
    "surprised": ("surprise", 0.8), "unbelievable": ("surprise", 0.85), "wow": ("surprise", 0.9),
    "shocking": ("surprise", 0.85), "unexpected": ("surprise", 0.75), "suddenly": ("surprise", 0.65),
    "incredible": ("surprise", 0.8), "astonishing": ("surprise", 0.9), "whoa": ("surprise", 0.85),
    "really": ("surprise", 0.4), "seriously": ("surprise", 0.5),

    # Inquisitive
    "wondering": ("inquisitive", 0.7), "curious": ("inquisitive", 0.75), "how": ("inquisitive", 0.3),
    "why": ("inquisitive", 0.4), "what": ("inquisitive", 0.3), "perhaps": ("inquisitive", 0.6),
    "maybe": ("inquisitive", 0.55), "question": ("inquisitive", 0.65), "explore": ("inquisitive", 0.6),
    "understand": ("inquisitive", 0.5), "explain": ("inquisitive", 0.5),

    # Calm / Reassurance
    "calm": ("calm", 0.8), "relax": ("calm", 0.8), "peaceful": ("calm", 0.85),
    "okay": ("calm", 0.5), "fine": ("calm", 0.45), "alright": ("calm", 0.45),
    "steady": ("calm", 0.7), "gentle": ("calm", 0.75), "easy": ("calm", 0.6),
    "breathe": ("calm", 0.85), "patience": ("calm", 0.75),
}


INTENSIFIERS = {"very": 1.3, "extremely": 1.5, "incredibly": 1.4, "so": 1.2,
                "really": 1.2, "absolutely": 1.4, "totally": 1.3, "utterly": 1.4,
                "deeply": 1.3, "highly": 1.2, "super": 1.3, "quite": 1.1}
NEGATORS = {"not", "no", "never", "don't", "doesn't", "didn't", "isn't", "wasn't",
            "can't", "won't", "wouldn't", "shouldn't", "couldn't", "hardly"}


EXCLAMATION_RE = re.compile(r'!+')
QUESTION_RE = re.compile(r'\?+')
CAPS_RE = re.compile(r'\b[A-Z]{3,}\b')
ELLIPSIS_RE = re.compile(r'\.{2,}')


def detect_emotion(text: str) -> dict:
    """
    Analyze text and return emotion label + intensity (0–1) + debug scores.
    Handles intensifiers, negation, punctuation signals, and ALL-CAPS.
    """
    words = re.findall(r"[a-zA-Z']+", text.lower())
    emotion_scores = {}

    i = 0
    while i < len(words):
        word = words[i]


        negated = any(words[max(0, i-j)] in NEGATORS for j in range(1, 3) if i - j >= 0)


        intensity_mult = 1.0
        if i > 0 and words[i-1] in INTENSIFIERS:
            intensity_mult = INTENSIFIERS[words[i-1]]

        if word in EMOTION_LEXICON:
            emotion, base_score = EMOTION_LEXICON[word]
            score = base_score * intensity_mult

            if negated:

                opposite = {"joy": "sadness", "sadness": "joy",
                            "anger": "calm", "fear": "calm",
                            "surprise": "neutral", "inquisitive": "neutral", "calm": "neutral"}
                emotion = opposite.get(emotion, "neutral")
                score *= 0.6  # reduced confidence

            emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score
        i += 1

    # Punctuation boosts
    excl_count = len(EXCLAMATION_RE.findall(text))
    q_count = len(QUESTION_RE.findall(text))
    caps_count = len(CAPS_RE.findall(text))
    ellipsis_count = len(ELLIPSIS_RE.findall(text))

    if excl_count:
        boost = min(excl_count * 0.15, 0.5)
        for e in ["joy", "anger", "surprise"]:
            if e in emotion_scores:
                emotion_scores[e] += boost
    if q_count:
        emotion_scores["inquisitive"] = emotion_scores.get("inquisitive", 0) + q_count * 0.2
    if caps_count:
        for e in ["anger", "joy", "surprise"]:
            if e in emotion_scores:
                emotion_scores[e] += caps_count * 0.1
    if ellipsis_count:
        emotion_scores["sadness"] = emotion_scores.get("sadness", 0) + ellipsis_count * 0.1
        emotion_scores["inquisitive"] = emotion_scores.get("inquisitive", 0) + ellipsis_count * 0.1

    if not emotion_scores:
        return {"emotion": "neutral", "intensity": 0.0, "scores": {}}

    # Normalize scores
    total = sum(emotion_scores.values())
    normalized = {k: round(v / total, 3) for k, v in emotion_scores.items()}

    top_emotion = max(emotion_scores, key=emotion_scores.get)
    raw_intensity = emotion_scores[top_emotion]
    intensity = round(min(raw_intensity / 2.0, 1.0), 3)  # cap at 1.0

    return {
        "emotion": top_emotion,
        "intensity": intensity,
        "scores": normalized,
    }



EMOTION_VOICE_MAP = {
    # emotion: (rate_base, pitch_base, volume_base, description)
    "joy":        (1.15, 1.20, 1.10, "Upbeat and energetic"),
    "sadness":    (0.85, 0.85, 0.85, "Slow and soft"),
    "anger":      (1.10, 0.90, 1.25, "Forceful and clipped"),
    "fear":       (1.05, 1.10, 0.90, "Tense and hushed"),
    "surprise":   (1.20, 1.25, 1.05, "Quick and high"),
    "inquisitive":(0.95, 1.10, 0.95, "Thoughtful with rising inflection"),
    "calm":       (0.90, 0.95, 0.90, "Smooth and measured"),
    "neutral":    (1.00, 1.00, 1.00, "Standard delivery"),
}


def compute_voice_params(emotion: str, intensity: float) -> dict:
    """
    Compute final rate, pitch, volume based on emotion and intensity.
    Intensity scales how far from neutral (1.0) each param moves.
    """
    base_rate, base_pitch, base_vol, desc = EMOTION_VOICE_MAP.get(
        emotion, EMOTION_VOICE_MAP["neutral"])

    def scale(base, neutral=1.0):
        delta = base - neutral
        return round(neutral + delta * intensity, 3)

    return {
        "rate":        scale(base_rate),
        "pitch":       scale(base_pitch),
        "volume":      scale(base_vol),

        "description": desc,
        "emotion":     emotion,
        "intensity":   intensity,
    }


#     SSML Builder


def build_ssml(text: str, params: dict) -> str:
    """Generate SSML with prosody tags for vocal modulation."""
    rate_pct = f"{int(params['rate'] * 100)}%"
    pitch_st = params['pitch'] - 1.0 
    pitch_str = f"{pitch_st:+.1f}st"
    vol_db = round((params['volume'] - 1.0) * 6, 1)
    vol_str = f"{vol_db:+.1f}dB"

    if params['intensity'] > 0.7:
        ssml = f'<speak><prosody rate="{rate_pct}" pitch="{pitch_str}" volume="{vol_str}"><emphasis level="strong">{text}</emphasis></prosody></speak>'
    elif params['intensity'] > 0.4:
        ssml = f'<speak><prosody rate="{rate_pct}" pitch="{pitch_str}" volume="{vol_str}"><emphasis level="moderate">{text}</emphasis></prosody></speak>'
    else:
        ssml = f'<speak><prosody rate="{rate_pct}" pitch="{pitch_str}" volume="{vol_str}">{text}</prosody></speak>'
    return ssml


#           TTS Engine 

def synthesize_speech(text: str, params: dict, output_path: str) -> bool:
    """
    Uses Microsoft Neural TTS for human-like delivery.
    Maps your rate and pitch math to neural parameters.
    """
    async def _generate():
        
        voice = "en-US-AriaNeural"
        
       
        rate_change = f"{int((params['rate'] - 1) * 100):+d}%"
        
        
        pitch_change = f"{int((params['pitch'] - 1) * 20):+d}Hz"
        
        communicate = edge_tts.Communicate(text, voice, rate=rate_change, pitch=pitch_change)
        await communicate.save(output_path)

    try:
        
        asyncio.run(_generate())
        return True
    except Exception as e:
        print(f"Neural TTS Error: {e}")
        
        return False





#           Flask App 

app = Flask(__name__)
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    if len(text) > 2000:
        return jsonify({"error": "Text too long (max 2000 chars)"}), 400


    emotion_result = detect_emotion(text)


    params = compute_voice_params(emotion_result["emotion"], emotion_result["intensity"])

    ssml = build_ssml(text, params)

    filename = f"{uuid.uuid4().hex}.wav"
    output_path = os.path.join(AUDIO_DIR, filename)
    synthesize_speech(text, params, output_path)

    return jsonify({
        "emotion": emotion_result["emotion"],
        "intensity": emotion_result["intensity"],
        "emotion_scores": emotion_result["scores"],
        "voice_params": {
            "rate": params["rate"],
            "pitch": params["pitch"],
            "volume": params["volume"],
            "description": params["description"],
        },
        "ssml": ssml,
        "audio_url": f"/static/audio/{filename}",
    })


@app.route("/api/emotions", methods=["GET"])
def emotion_map():
    """Return the full emotion → voice parameter mapping."""
    result = {}
    for emotion, (rate, pitch, vol, desc) in EMOTION_VOICE_MAP.items():
        result[emotion] = {
            "rate_base": rate, "pitch_base": pitch,
            "volume_base": vol, "description": desc
        }
    return jsonify(result)


@app.route("/static/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


#       CLI Mode

def cli_mode():
    import sys
    print("\n  Empathy Engine — CLI Mode")
    print("=" * 50)

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter text: ").strip()
        if not text:
            print("No text provided.")
            return

    emotion_result = detect_emotion(text)
    params = compute_voice_params(emotion_result["emotion"], emotion_result["intensity"])

    print(f"\n Emotion Analysis:")
    print(f"   Detected: {emotion_result['emotion'].upper()} (intensity: {emotion_result['intensity']:.2f})")
    if emotion_result['scores']:
        scores_str = ", ".join(f"{k}: {v:.2f}" for k, v in
                               sorted(emotion_result['scores'].items(), key=lambda x: -x[1]))
        print(f"   Scores:   {scores_str}")

    print(f"\n Voice Parameters:")
    print(f"   Rate:     {params['rate']:.3f}x  ({params['description']})")
    print(f"   Pitch:    {params['pitch']:.3f}x")
    print(f"   Volume:   {params['volume']:.3f}x")

    output_path = os.path.join(AUDIO_DIR, "output.wav")
    print(f"\n🔊 Synthesizing to {output_path}...")
    synthesize_speech(text, params, output_path)
    print(f"   Done! File: {output_path}")


if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv or (len(sys.argv) > 1 and not sys.argv[1].startswith("--")):
        cli_mode()
    else:
        print(" Starting Empathy Engine web server at http://localhost:5000")
        app.run(debug=True, port=5000)
