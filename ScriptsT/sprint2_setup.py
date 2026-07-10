import requests

# ==========================================
# 1. Place your API Key, Token, and Board ID here
# ==========================================
API_KEY = "18482e7216f9b3ba3c2072364327d4b1"
TOKEN = "ATTA97644a56e63500222cab7b8966e3b86988b6a7d8563743d24e3b5e5afc7b653aB205A98B"
BOARD_ID = "AKyrqFZM" 

# ==========================================
# 2. Create Sprint 2 List & Fetch Label IDs
# ==========================================
print("Setting up Sprint 2 environment...")

# Create new list for Sprint 2
lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
sprint2_list_data = {
    "name": "Sprint 2: Apr 11 - Apr 18",
    "pos": 3, # عشان تظهر بعد الـ Backlog مباشرة
    "key": API_KEY,
    "token": TOKEN
}
sprint2_response = requests.post(lists_url, params=sprint2_list_data).json()
sprint2_list_id = sprint2_response.get("id")

# Fetch Labels
labels_url = f"https://api.trello.com/1/boards/{BOARD_ID}/labels"
labels_response = requests.get(labels_url, params={"key": API_KEY, "token": TOKEN}).json()
label_map = {lbl['name']: lbl['id'] for lbl in labels_response}

if not sprint2_list_id:
    print("Error: Could not create Sprint 2 list.")
    exit()

# ==========================================
# 3. Sprint 2 Cards Data
# ==========================================
cards_data = [
    {
        "name": "UI/UX: Dashboard UX Architecture",
        "label": "UI/UX",
        "desc": "**Required Tasks:**\n- Design detailed wireframes for Employee and Employer dashboards.\n- Finalize the Theme & Component Library (Colors, Buttons, Typography)."
    },
    {
        "name": "Backend: Identity & Job Posting API",
        "label": "Backend",
        "desc": "**Required Tasks:**\n- Implement Role-Based Authentication (RBAC) to separate Employers from Employees.\n- Develop Job CRUD API (Phase 1) for companies to post and view jobs.\n- Generate API Documentation (Swagger) for the Frontend team."
    },
    {
        "name": "Frontend: User Entry & Dynamic Data",
        "label": "Frontend",
        "desc": "**Required Tasks:**\n- Build functional Authentication UI (Login/Signup) with validation.\n- Connect the Job Feed page to the Backend API to fetch real jobs.\n- Implement Global State Management (e.g., Context API) for user sessions."
    },
    {
        "name": "Network/DevOps: Database & Cloud Infrastructure",
        "label": "Network/DevOps",
        "desc": "**Required Tasks:**\n- Provision a Cloud Database (e.g., Supabase, MongoDB Atlas Free Tier).\n- Configure Automated Deployment (CI/CD) using GitHub Actions for the dev branch."
    },
    {
        "name": "AI (Team Leader): Structuring the Brain",
        "label": "AI (Team Leader)",
        "desc": "**Required Tasks:**\n- Implement AI JSON Schema Design for structured CV analysis output (Scores, Skills, Reasons).\n- Refine the text extraction engine to handle complex multi-column PDFs.\n- Run a local environment stress test to monitor processing time."
    }
]

# ==========================================
# 4. Create Cards in Sprint 2
# ==========================================
print("Distributing Sprint 2 tasks...")
cards_url = "https://api.trello.com/1/cards"

for card in cards_data:
    label_id = label_map.get(card["label"])
    
    querystring = {
        "idList": sprint2_list_id,
        "name": card["name"],
        "desc": card["desc"],
        "idLabels": [label_id] if label_id else [],
        "key": API_KEY,
        "token": TOKEN
    }
    
    requests.post(cards_url, params=querystring)
    print(f"Successfully created: {card['name']}")

print("\nSprint 2 is ready! You can now notify the team.")