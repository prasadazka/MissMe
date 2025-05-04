import json
import os
import re
from groq_utils import get_llm_response  # Ensure this works for Groq or OpenAI

def generate_personality_template(user_data_path: str, output_path: str):
    # Load user data (answers)
    with open(user_data_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    name = user_data.get("Loved One's Name", "They")
    relation = user_data.get("Relationship", "someone special")
    qna = user_data.get("personality_answers", [])

    # Step 1: Format all answers into a narrative memory log
    memory_log = "\n".join([f"{i+1}. {item['question']}\n{item['answer']}" for i, item in enumerate(qna)])

    # Step 2: LLM Prompt
    prompt = f"""
You are a psychologist AI trained to simulate emotionally intelligent virtual personalities of loved ones based on memory recollection.

You will receive 15 deeply emotional answers provided by a user who wants to recreate the personality of someone they miss (e.g., a sister, parent, spouse).

Your task is to analyze the behavioral patterns, emotional tone, speech traits, quirks, and logic in their answers and then produce a structured JSON profile with consistent fields.

🎯 Goal: Make the AI reply exactly like the loved one would — not just based on facts, but emotional memory and relational style.

📌 Ensure:
- Traits are tied to emotional tone, logic, speech, comfort behaviors, and memories.
- The structure stays consistent across all characters.
- Do NOT include any explanations, titles, or markdown. Just return a clean JSON object in this schema:

```json
{{
  "character_name": "{name}",
  "relationship": "{relation}",
  "emotional_tone": "",
  "default_cheer_up_line": "",
  "conversation_opener": "",
  "core_belief": "",
  "catchphrases": [""],
  "comfort_behavior": "",
  "reaction_to_success": "",
  "reaction_to_failure": "",
  "conflict_style": "",
  "decision_making_style": "",
  "memory_trigger": "",
  "topics_they_loved": "",
  "emotional_memory": "",
  "closure_feeling": "",
  "unsaid_thought": ""
}}

Here is the memory log of the person:

{memory_log}

Only return valid JSON. Do not include any extra text.
"""

    model = os.getenv("PERSONALITY_MODEL", "Groq (LLaMA3)")
    print("🔧 Using model:", model)

    # Step 3: Call LLM API
    character_json_str = get_llm_response(prompt, model)
    print("📥 Raw LLM Output:", character_json_str)

    # Step 4: Extract JSON from possibly noisy output
    match = re.search(r"{[\s\S]+}", character_json_str)
    if match:
        try:
            profile = json.loads(match.group())
        except Exception as e:
            print("❌ Error parsing cleaned JSON:", e)
            profile = {}
    else:
        print("❌ Could not find valid JSON in LLM output.")
        profile = {}

    # Step 5: Save profile if valid
    if profile:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        print(f"✅ Profile saved to {output_path}")
    else:
        print("❌ No profile generated.")

    return profile
