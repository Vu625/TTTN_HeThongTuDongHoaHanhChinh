def get_dashboard_data():
    #lấy data để dashboard
    pass

import pandas as pd
import json
from pathlib import Path

APP_PATH = Path("data/db/applications.json")
FORM_PATH = Path("data/db/form_templates.json")
WORKFLOW_PATH = Path("data/db/workflows.json")

def load_forms():
    with open(FORM_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_name_form(form_id):
    forms = load_forms()
    for f in forms:
        if f["form_template_id"] == form_id:
            return f["name_vn"]
    return "thủ tục không xác định"

def load_applications():
    try:
        with open(APP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_applications(data):
    with open(APP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_statistics():
    apps = load_applications()
    if not apps:
        return None

    df = pd.DataFrame(apps)
    total = len(df)
    by_status = df['status'].value_counts().to_dict()
    by_procedure = df['form_template_id'].value_counts().to_dict()
    return {
        "total": total,
        "by_status": by_status,
        "by_procedure": by_procedure
    }

def load_users():
    path = Path("data/db/users.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def user_full_name(id_name):
    users = load_users()
    for u in users:
        if u["user_id"] == id_name:
            return u["full_name"]
    return "Không xác định"

def save_users(data):
    path = Path("data/db/users.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_workflows():
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_workflow_for_procedure(code):
    #T001
    forms = load_forms()
    workflows = load_workflows()
    for f in forms:
        if f["form_template_id"] == code:
            for wf in workflows:
                if wf["workflow_id"] == f["linked_workflow_id"]:
                    return wf["steps"]
    # for wf in workflows:
    #     if wf["workflow_id"] == code:
    #         return wf["steps"]
    return []
