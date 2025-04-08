import json
from pathlib import Path

DB_FILE = Path("data.json")

if not DB_FILE.exists():
    DB_FILE.write_text("{}", encoding="utf-8")

def load_data():
    with DB_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    return load_data().get(str(user_id))

def save_user(user_id, info):
    data = load_data()
    data[str(user_id)] = info
    save_data(data)

def get_all_users():
    return load_data()

def delete_user_by_name(name):
    data = load_data()
    name = name.lower()
    to_delete = [uid for uid, info in data.items() if info.get("name", "").lower() == name]
    for uid in to_delete:
        del data[uid]
    save_data(data)
    return len(to_delete)

def delete_all_users():
    save_data({})

def find_user_by_name(query):
    query = query.lower()
    return {
        uid: user for uid, user in load_data().items()
        if query in user.get("name", "").lower() or query in user.get("surname", "").lower()
    }

def get_top_users():
    users = load_data()
    return sorted(
        users.items(),
        key=lambda item: sum(1 for v in item[1].get("likes", {}).values() if v == 1),
        reverse=True
    )

def like_profile(viewer_id, target_id, value):
    data = load_data()
    target = data.get(str(target_id))
    if not target:
        return
    likes = target.get("likes", {})
    likes[str(viewer_id)] = value
    target["likes"] = likes
    data[str(target_id)] = target
    save_data(data)

def get_likes_info(user_id):
    user = get_user(user_id)
    likes = user.get("likes", {}) if user else {}
    like_count = sum(1 for v in likes.values() if v == 1)
    dislike_count = sum(1 for v in likes.values() if v == -1)
    return like_count, dislike_count