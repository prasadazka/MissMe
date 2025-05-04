import streamlit as st
import json
import os
import re
from personality_builder import generate_personality_template

def load_questions(json_path="personality_questions.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)["personality_questions"]

def render_questionnaire_tab():
    st.header("💬 Create Your Loved One's Memory")

    questions = load_questions()

    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "personality_created" not in st.session_state:
        st.session_state.personality_created = False

    step = st.session_state.current_step

    # Step 0: Name
    if step == 0:
        with st.form("name_form"):
            st.subheader("👤 What is your loved one’s name?")
            name = st.text_input("Their name", value=st.session_state.responses.get("Loved One's Name", ""))
            submitted = st.form_submit_button("Next")
            if submitted:
                if len(name.strip()) >= 3:
                    st.session_state.responses["Loved One's Name"] = name.strip()
                    st.session_state.current_step += 1
                    st.rerun()
                else:
                    st.warning("Please enter at least 3 characters for the name.")

    # Step 1: Relationship
    elif step == 1:
        with st.form("relationship_form"):
            st.subheader("💞 What is your relationship with them?")
            relationship = st.selectbox(
                "Choose one", 
                ["Father", "Mother", "Sibling", "Spouse", "Friend", "Mentor", "Other"],
                index=["Father", "Mother", "Sibling", "Spouse", "Friend", "Mentor", "Other"].index(
                    st.session_state.responses.get("Relationship", "Father"))
            )
            col1, col2 = st.columns(2)
            back = col1.form_submit_button("⬅️ Back")
            next_ = col2.form_submit_button("➡️ Next")
            if back:
                st.session_state.current_step -= 1
                st.rerun()
            if next_:
                st.session_state.current_step += 1
                st.rerun()  # ✅ use st.rerun() instead of rerun


    # Steps 2 → N (questions)
    elif 2 <= step <= len(questions) + 1:
        q_index = step - 2
        question_obj = questions[q_index]
        question = question_obj["question"]
        example = question_obj["answer"]

        with st.form(f"form_q{q_index}"):
            st.subheader(f"{q_index+1}. {question}")
            response = st.text_area(
                "Your answer", 
                value=st.session_state.responses.get(question, ""), 
                placeholder=example, 
                height=150
            )
            col1, col2 = st.columns(2)
            back = col1.form_submit_button("⬅️ Back")
            next_ = col2.form_submit_button("➡️ Next" if q_index + 1 < len(questions) else "✅ Finish")

            if back:
                st.session_state.responses[question] = response
                st.session_state.current_step -= 1
                st.rerun()
            elif next_:
                if len(response.strip()) >= 25:
                    st.session_state.responses[question] = response
                    if q_index + 1 < len(questions):
                        st.session_state.current_step += 1
                        st.rerun()
                    else:
                        st.success("✅ All responses saved.")
                else:
                    st.warning("Please enter at least 25 characters to describe them well.")

    # Final Step: Create Personality
    if step >= len(questions) + 1 and not st.session_state.personality_created:
        st.markdown("---")
        st.subheader("🧬 Ready to Build Personality?")

        if st.button("🧠 Create Personality"):
            raw_name = st.session_state.responses.get("Loved One's Name", "default")
            safe_name = re.sub(r'\W+', '', raw_name.strip().lower())

            user_filename = f"personality_{safe_name}.json"
            character_filename = f"character_{safe_name}.json"

            personality_answers = [
                {"question": k, "answer": v}
                for k, v in st.session_state.responses.items()
                if k not in ["Loved One's Name", "Relationship"]
            ]

            personality_data = {
                "Loved One's Name": raw_name,
                "Relationship": st.session_state.responses.get("Relationship", ""),
                "personality_answers": personality_answers
            }

            with open(user_filename, "w", encoding="utf-8") as f:
                json.dump(personality_data, f, indent=2, ensure_ascii=False)

            st.info(f"📁 User responses saved to `{user_filename}`")

            model = os.getenv("PERSONALITY_MODEL", "Groq (LLaMA3)")
            print("🔧 Using model:", model)

            profile = generate_personality_template(
                user_data_path=user_filename,
                output_path=character_filename
            )

            if profile:
                st.session_state["personality_responses"] = st.session_state.responses
                st.session_state["personality_profile"] = profile
                st.session_state.personality_created = True
                st.success(f"🧠 Personality generated and saved to `{character_filename}`")
                st.json(profile)
            else:
                st.error("❌ Failed to generate personality. Check logs or LLM output.")
