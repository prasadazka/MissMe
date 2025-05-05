import os
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import streamlit as st
from pathlib import Path

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os
from groq_utils import get_llm_response

#OPENAI_API_KEY ="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"

elevenlabs_api_key = "sk_5e396eb82dfcf51ef26a365ced74f8a1f5e198f20e0fa01a"


def render_voice_upload_tab():
    st.header("🎙️ Upload a Voice Sample")

    st.markdown("""
    Upload a short audio clip of your loved one (e.g., `.wav`, `.mp3`)  
    This voice will be used to clone their tone and style.
    """)

    # Create upload folder
    upload_dir = "uploaded_voices"
    Path(upload_dir).mkdir(parents=True, exist_ok=True)

    uploaded_file = st.file_uploader("📁 Upload voice file", type=["wav", "mp3"])

    if uploaded_file:
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    else:
        return None  # ✅ avoids UnboundLocalError


    

    #     with open(file_path, "wb") as f:
    #         f.write(uploaded_file.getbuffer())

    #     st.success(f"✅ File saved as `{uploaded_file.name}`")
    #     st.audio(file_path)

    #     st.session_state["uploaded_voice_path"] = file_path  # Store path for later cloning


elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

# Emotion to voice settings mapping
emotion_voice_map = {
    "happy": {"stability": 0.3, "similarity_boost": 0.8},
    "sad": {"stability": 0.5, "similarity_boost": 0.85},
    "angry": {"stability": 0.2, "similarity_boost": 0.75},
    "calm": {"stability": 0.7, "similarity_boost": 0.9},
    "excited": {"stability": 0.25, "similarity_boost": 0.8},
    "fearful": {"stability": 0.6, "similarity_boost": 0.85}
}

# Detect emotion from text



def detect_emotion(text):
    groq_api_key = "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"

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-8b-8192",  # or "llama3-8b-8192" if you prefer
        temperature=0.2,
    )

    messages = [
        SystemMessage(content="You are an emotion classification expert."),
        HumanMessage(content=f"Classify the dominant emotion of the following text. Respond with only one word (e.g., happy, sad, angry, calm, excited, fearful, etc.):\n\n{text}")
    ]

    response = llm(messages)
    return response.content.strip().lower()


# Clone and generate emotional voice
def synthesize_emotional_voice(input_voice_path, input_text,character_id):
    """
    Clones the voice from the input file and synthesizes the input text with emotion.

    Args:
        input_voice_path (str): Path to the uploaded voice file.
        input_text (str): The input text to synthesize.

    Returns:
        str: Path to the generated MP3 file.
    """

    # Clone voice
    voice = elevenlabs_client.clone(
        name="JP_Cloned_Voice",
        description=f"Cloned from {os.path.basename(input_voice_path)}",
        files=[input_voice_path]
    )
    voice_id = voice.voice_id
    print(f"[✓] Cloned voice ID: {voice_id}")

    # Detect emotion
    emotion = detect_emotion(input_text)
    print(f"[INFO] Detected emotion: {emotion}")

    # Get emotion settings
    settings = emotion_voice_map.get(emotion, {"stability": 0.5, "similarity_boost": 0.85})

    # Generate speech
    audio = elevenlabs_client.text_to_speech.convert(
        text=input_text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings=settings
    )

    # Save to file
    output_path = f"{character_id}_{emotion}.mp3"
    with open(output_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

    print(f"[✓] Audio generated: {output_path}")
    return output_path
