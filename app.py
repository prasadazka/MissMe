import os
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

# Initialize clients
openai_client = OpenAI(api_key=openai_api_key)
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

# Emotion → Voice Settings mapping
emotion_voice_map = {
    "happy": {"stability": 0.3, "similarity_boost": 0.8},
    "sad": {"stability": 0.5, "similarity_boost": 0.85},
    "angry": {"stability": 0.2, "similarity_boost": 0.75},
    "calm": {"stability": 0.7, "similarity_boost": 0.9},
    "excited": {"stability": 0.25, "similarity_boost": 0.8},
    "fearful": {"stability": 0.6, "similarity_boost": 0.85}
}

# Step 1: Detect emotion from text
def detect_emotion(text):
    prompt = f"""Classify the dominant emotion of the following text. Respond with only one word (e.g., happy, sad, angry, calm, excited, fearful, etc.):\n\n{text}"""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an emotion classification expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip().lower()

# Step 2: Generate voice
def generate_voice_from_text(text, voice_id):
    emotion = detect_emotion(text)
    print(f"[INFO] Detected emotion: {emotion}")

    settings = emotion_voice_map.get(emotion, {"stability": 0.5, "similarity_boost": 0.85})

    audio = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings=settings
    )

    filename = f"emotion_{emotion}.mp3"
    with open(filename, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

    print(f"[✓] Generated: {filename}")

# Step 3: Clone voice from jp_1.mp3 if not already cloned
def clone_voice():
    voice = elevenlabs_client.clone(
        name="JP_Voice",
        description="Cloned from jp_1.mp3 for emotion-based synthesis",
        files=["jp_1.mp3"]
    )
    print(f"[✓] Cloned voice ID: {voice.voice_id}")
    return voice.voice_id

# Main
if __name__ == "__main__":
    sample_text = """
    I can't believe you forgot my birthday again. I'm really hurt and disappointed.
    """

    voice_id = clone_voice()  # ⬅ Clone and get actual voice_id
    generate_voice_from_text(sample_text, voice_id)
