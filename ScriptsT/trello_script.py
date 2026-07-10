import requests
import json

# ==========================================
# 1. ضع المفاتيح الخاصة بك هنا
# ==========================================
API_KEY = "18482e7216f9b3ba3c2072364327d4b1"
TOKEN = "ATTA97644a56e63500222cab7b8966e3b86988b6a7d8563743d24e3b5e5afc7b653aB205A98B"
# ==========================================
# 2. إنشاء البورد (Board)
# ==========================================
print("جاري إنشاء البورد...")
url_board = "https://api.trello.com/1/boards/"
querystring_board = {
    "name": "HireSphere: Smart AI Recruitment",
    "desc": "لوحة إدارة مهام مشروع التخرج - فريق التطوير",
    "defaultLabels": "true",
    "defaultLists": "false", # هنلغي القوائم الافتراضية عشان نعمل قوائمنا
    "key": API_KEY,
    "token": TOKEN
}
response_board = requests.post(url_board, params=querystring_board)
board_id = response_board.json()["id"]
print("تم إنشاء البورد بنجاح!")

# ==========================================
# 3. إنشاء القوائم (Lists) بالترتيب
# ==========================================
# لاحظ: السبت القادم هو 4 أبريل، فالأسبرنت من 4 لـ 11 أبريل 2026
lists = [
    "1. المصادر والمستندات (Docs & Resources)",
    "2. قائمة الأفكار (Backlog)",
    "3. مهام الأسبوع (Sprint 1: Apr 4 - Apr 11)",
    "4. قيد التنفيذ (In Progress)",
    "5. المراجعة والاختبار (Review/Testing)",
    "6. تم الإنجاز (Done)"
]

url_lists = f"https://api.trello.com/1/boards/{board_id}/lists"
# بنعكس الترتيب في الكود عشان يظهروا من الشمال لليمين صح في واجهة تريلو
for list_name in reversed(lists):
    querystring_list = {
        "name": list_name,
        "key": API_KEY,
        "token": TOKEN
    }
    requests.post(url_lists, params=querystring_list)

print("تم إنشاء القوائم بنجاح!")

# ==========================================
# 4. تخصيص الألوان (Labels) لكل تخصص
# ==========================================
labels = [
    {"name": "AI (Team Leader)", "color": "purple"},
    {"name": "Backend", "color": "green"},
    {"name": "Frontend", "color": "blue"},
    {"name": "UI/UX", "color": "pink"},
    {"name": "Network/DevOps", "color": "orange"}
]

url_labels = f"https://api.trello.com/1/boards/{board_id}/labels"
for label in labels:
    querystring_label = {
        "name": label["name"],
        "color": label["color"],
        "key": API_KEY,
        "token": TOKEN
    }
    requests.post(url_labels, params=querystring_label)

print("تم تخصيص الألوان (Labels) بنجاح!")
print(f"رابط البورد الخاص بك: https://trello.com/b/{board_id}")