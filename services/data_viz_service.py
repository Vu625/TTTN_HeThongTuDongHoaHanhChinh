def get_dashboard_data():
    #lấy data để dashboard
    pass

import json
from pathlib import Path

APP_PATH = Path("data/db/applications.json")
FORM_PATH = Path("data/db/form_templates.json")

def load_forms():
    with open(FORM_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_applications():
    try:
        with open(APP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_applications(data):
    with open(APP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
