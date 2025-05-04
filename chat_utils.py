import json
import os

def load_chat_history(character_id):
    chat_history_file = f"chat_history_{character_id}.json"
    history = []

    if not os.path.exists(chat_history_file):
        return history

    try:
        with open(chat_history_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return history  # Empty file, return clean list
            raw_history = json.loads(content)

            for item in raw_history:
                if isinstance(item, dict):
                    history.append(item)
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    history.append({"question": item[0], "response": item[1]})
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Invalid chat history in {chat_history_file}: {e}")
        # Optional: reset corrupted file to blank
        with open(chat_history_file, "w", encoding="utf-8") as f:
            json.dump([], f)

    return history


def save_chat_history(character_id, chat_history):
    chat_history_file = f"chat_history_{character_id}.json"
    with open(chat_history_file, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)

def save_accepted_response(character_id, question, response, rating):
    accepted_responses_file = f"accepted_{character_id}.json"
    accepted_entry = {
        "question": question,
        "response": response,
        "rating": rating
    }
    if os.path.exists(accepted_responses_file):
        try:
            with open(accepted_responses_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            existing = []
    else:
        existing = []

    existing.append(accepted_entry)
    with open(accepted_responses_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
