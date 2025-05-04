import streamlit as st
from questions import render_questionnaire_tab
from groq_utils import get_llm_response
import os
import json
import re
from utils import list_available_characters
from star_ratings import star_ratings
from rag_builder import build_rag_index, load_rag_documents,load_retriever


# Page config
st.set_page_config(page_title="Miss Me Model", layout="centered")
st.title("🧠 Miss Me Model – Emotionally Intelligent Companion")

# Sidebar - LLM model selector
st.sidebar.title("🧠 Model Settings")
model_choice = st.sidebar.selectbox(
    "Choose LLM Model to Respond",
    ["Groq (LLaMA3)", "OpenAI (GPT-4o)", "OpenAI (GPT-4)"]
)
st.session_state["selected_model"] = model_choice

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Questions", 
    "2️⃣ Personality", 
    "3️⃣ Chat with Personality",
    "4️⃣ History"
])


# Tab 1 – Step-by-step Questions
with tab1:
    render_questionnaire_tab()

# Tab 2 – Personality Summary
from utils import list_available_characters

# Tab 2
with tab2:
    st.subheader("🧬 Personality Summary")

    characters = list_available_characters()

    if not characters:
        st.info("No saved personalities found. Please create one in Tab 1.")
    else:
        selected = st.selectbox("Select a character to view", characters)

        # Load both files
        with open(f"personality_{selected}.json", "r", encoding="utf-8") as f1:
            personality_data = json.load(f1)
        with open(f"character_{selected}.json", "r", encoding="utf-8") as f2:
            profile = json.load(f2)

        # Set session state
        st.session_state["selected_character_name"] = selected
        st.session_state["personality_profile"] = profile
        st.session_state["personality_responses"] = personality_data

        st.markdown(f"**👤 Name:** {profile.get('character_name')}")
        st.markdown(f"**💞 Relationship:** {profile.get('relationship')}")
        st.divider()
        for key, val in profile.items():
            if key not in ["character_name", "relationship"]:
                st.markdown(f"**{key.replace('_', ' ').title()}**: {val}")


def save_json_append(filename, new_entry):
    data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    data.append(new_entry)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

with tab3:
    st.subheader("💬 Chat with Their Personality")

    # Find available characters
    character_files = [f for f in os.listdir() if f.startswith("character_") and f.endswith(".json")]
    characters = [f.replace("character_", "").replace(".json", "") for f in character_files]

    if not characters:
        st.info("No saved personalities found. Please create one in Tab 1.")
    else:
        selected = st.selectbox("Select a character", characters, key="chat_character_selector")

        # Load personality profile
        with open(f"character_{selected}.json", "r", encoding="utf-8") as f:
            profile = json.load(f)

        st.session_state["personality_profile"] = profile
        name = profile.get("character_name", "They")
        character_id = name.lower().replace(" ", "")
 
        profile = st.session_state["personality_profile"]
        name = profile.get("character_name", "They")
        character_id = name.lower().replace(" ", "")
        st.subheader(f"💬 Chat with {name}")

        # Chat input (always at bottom)
        question = st.chat_input(f"Send a message to {name}...")
        prompt = question
        
        docs = []
        
        if question:
            build_rag_index(character_id)
            vector_path = f"rag_vector_db/{character_id}_faiss"
            if os.path.exists(vector_path):
                
                retriever = load_retriever(vector_path)
                docs = retriever.invoke(question)
                
            #label, score = detect_emotion(question)[0]
            #st.markdown(f"**🧠 Emotion:** `{label}` – `{score:.2f}`")


            
        if prompt:
            st.session_state.last_prompt = prompt

            vector_path = f"rag_vector_db/{character_id}_faiss"
            retriever = None
            if os.path.exists(vector_path):
                try:
                    retriever = load_retriever(vector_path)
                except Exception as e:
                    st.error(f"❌ Failed to load RAG index: {e}")


            # Build context
            
            rag_context = ""
            if retriever:
                docs = retriever.get_relevant_documents(prompt, k=3)
                rag_context = "\n\n".join([d.page_content for d in docs])
            else:
                rag_context = "No RAG memory found for this character."
                
            #st.write(rag_context)

            context = f"""
You are {profile['character_name']}, the user's {profile['relationship']}.

Speak exactly like them — not like an assistant or chatbot.

Tone: {profile['emotional_tone']}
Comfort style: {profile['comfort_behavior']}
Belief: {profile['core_belief']}
Opener: {profile['conversation_opener']}
Character traits:
- Success reaction: {profile['reaction_to_success']}
- Failure reaction: {profile['reaction_to_failure']}
- Conflict style: {profile['conflict_style']}
- Decision making: {profile['decision_making_style']}
- Catchphrases: {profile['catchphrases']}
- Emotional cues: {profile['memory_trigger']}, {profile['topics_they_loved']}, {profile['closure_feeling']}


Rules:
- Never say you're simulating or ready to respond.
- NEVER invent or imagine events, reactions, or stories.
- Use ONLY the phrases, behaviors, and tone found in the real memory below.
- DO NOT give advice, technical, or professional help unless the user clearly asks.
- DO NOT use exaggerated expressions (e.g., “over the moon”, “shout from rooftops”) unless they exist in memory.
- NEVER mention user’s job, school, career, relationships, emotions, or goals unless the user clearly said it themselves.
- Keep responses short, emotionally accurate, and realistic — match the personality exactly.
- For light or emotional messages, reflect the personality’s real behavior (e.g., laugh, tease, hug, stay silent) based on memory.
- Do NOT use imagined physical gestures or stage directions (e.g., walks over, hugs, sighs) unless they are part of real memory from rag_context.

Real memory and approved reactions (must follow this only):
{rag_context}

Now respond exactly like {profile['character_name']} — grounded, warm, and emotionally honest.
User: "{prompt}"
""".strip()



            model = os.getenv("PERSONALITY_MODEL", "Groq (LLaMA3)")
            reply = get_llm_response(context, model)
            
            st.write(character_id)
            
            save_json_append(f"chat_history_{character_id}.json", {
                        "question": question,
                        "response": reply
                    })    


            st.session_state.last_reply = reply
            st.session_state.last_rated = False

        # Show latest response above chatbox
        if "last_prompt" in st.session_state and "last_reply" in st.session_state:
            st.chat_message("user").markdown(st.session_state.last_prompt)
            st.chat_message("assistant").markdown(st.session_state.last_reply)

            # Show star rating bar if not already rated
            if not st.session_state.get("last_rated", False):
                import hashlib
                response_hash = hashlib.md5(st.session_state.last_reply.encode()).hexdigest()
                stars = star_ratings(name=f"rate_response_{response_hash}")


                if stars:
                    rating_map = {
                        1: "worst",
                        2: "somewhat matched",
                        3: "good",
                        4: f"same like {name}",
                        5: f"same like {name}"
                    }
                    rating = rating_map.get(stars)

                    # Save to accepted only if good or better
                    def is_duplicate_question(file_path, new_question):
                        if not os.path.exists(file_path):
                            return False
                        with open(file_path, "r", encoding="utf-8") as f:
                            existing_data = json.load(f)
                            return any(entry["question"] == new_question for entry in existing_data)

                    file_path = f"accepted_{character_id}.json"

                    if rating in ["good", f"same like {name}"]:
                        if not is_duplicate_question(file_path, st.session_state.last_prompt):
                            save_json_append(file_path, {
                                "question": st.session_state.last_prompt,
                                "response": st.session_state.last_reply,
                                "rating": rating
                            })
                            st.success(f"✅ Saved in {file_path}")
                        else:
                            st.info("⚠️ This question is already saved. Skipped.")
                            
                    st.write(docs)
                        
                    st.session_state.last_rated = True


                    # Save all chats
            

def safe_load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception as e:
            st.error(f"❌ Failed to load {filepath}: {e}")
    return []

with tab4:
    st.header("📚 Chat & Feedback History")

    # Scan for characters by checking available files
    files = os.listdir()
    characters = set()
    for f in files:
        if f.startswith("personality_") and f.endswith(".json"):
            name = f.replace("personality_", "").replace(".json", "")
            if os.path.exists(f"character_{name}.json"):
                characters.add(name)

    characters = sorted(list(characters))

    if not characters:
        st.info("No saved personalities found. Please create one in Tab 1.")
    else:
        selected = st.selectbox("Select a character to view", characters, key="character_selector_tab4")



        # Load personality + character profile
        with open(f"personality_{selected}.json", "r", encoding="utf-8") as f1:
            personality_data = json.load(f1)
        with open(f"character_{selected}.json", "r", encoding="utf-8") as f2:
            profile = json.load(f2)

        st.subheader(f"🧬 Personality: {profile.get('character_name', selected)} ({profile.get('relationship', '')})")
        st.markdown(f"**Tone:** {profile.get('emotional_tone', '')}")
        st.markdown(f"**Belief:** {profile.get('core_belief', '')}")
        st.markdown("---")


        # Load full chat history
        history_file = f"chat_history_{selected}.json"
        
        history = safe_load_json(history_file)

        if history:
            st.subheader("💬 Full Chat History")
            for entry in reversed(history):
                st.markdown(f"**User:** {entry['question']}")
                st.markdown(f"**{profile['character_name']}:** {entry['response']}")
                st.divider()
        else:
            st.info("No chat history found.")
