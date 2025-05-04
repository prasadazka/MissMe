import os

def list_available_characters():
    files = os.listdir()
    characters = []

    for f in files:
        if f.startswith("character_") and f.endswith(".json"):
            name = f.replace("character_", "").replace(".json", "")
            if f"personality_{name}.json" in files:
                characters.append(name)
    return characters
