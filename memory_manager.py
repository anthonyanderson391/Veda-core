import json
import os

# Path to memory file
MEMORY_FILE = "veda_memory.json"

# ========== Initialize Memory File ==========
def init_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({"corrections": {}, "preferred_phrases": {}, "command_logs": []}, f)

# ========== Load Memory ==========
def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# ========== Save Memory ==========
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# ========== Log Command Usage ==========
def log_command(command, success=True):
    memory = load_memory()
    memory["command_logs"].append({
        "command": command,
        "success": success
    })
    save_memory(memory)

# ========== Store Correction ==========
def save_correction(original, correction):
    memory = load_memory()
    memory["corrections"][original] = correction
    save_memory(memory)

# ========== Set Preferred Phrase ==========
def set_preferred_phrase(category, new_phrase):
    memory = load_memory()
    memory["preferred_phrases"][category] = new_phrase
    save_memory(memory)

# ========== Retrieve Preferred Phrase ==========
def get_preferred_phrase(category):
    memory = load_memory()
    return memory["preferred_phrases"].get(category, None)

def should_prompt_for_correction(command):
    memory = load_memory()
    failures = [log for log in memory["command_logs"] if log["command"] == command and not log["success"]]
    return len(failures) >= 3