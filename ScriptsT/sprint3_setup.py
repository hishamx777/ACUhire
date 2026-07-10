import requests

# ==========================================
# 1. Place your API Key, Token, and Board ID here
# ==========================================
API_KEY = "18482e7216f9b3ba3c2072364327d4b1"
TOKEN = "ATTA97644a56e63500222cab7b8966e3b86988b6a7d8563743d24e3b5e5afc7b653aB205A98B"
BOARD_ID = "AKyrqFZM" 

# ==========================================
# 2. Setup Sprint 3 List
# ==========================================
print("Setting up Sprint 3 (Apr 18 - Apr 25)...")

lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
sprint3_data = {
    "name": "Sprint 3: Apr 18 - Apr 25",
    "pos": 4, 
    "key": API_KEY,
    "token": TOKEN
}
sprint3_list = requests.post(lists_url, params=sprint3_data).json()
sprint3_id = sprint3_list.get("id")

# Fetch Label IDs
labels_url = f"https://api.trello.com/1/boards/{BOARD_ID}/labels"
labels_response = requests.get(labels_url, params={"key": API_KEY, "token": TOKEN}).json()
label_map = {lbl['name']: lbl['id'] for lbl in labels_response}

# ==========================================
# 3. Sprint 3 Data with Checklists
# ==========================================
sprint_tasks = [
    {
        "name": "AI (Team Leader): Interview Bot Core & STT",
        "label": "AI (Team Leader)",
        "tasks": [
            "Integrate OpenAI Whisper (Tiny/Base) for Speech-to-Text.",
            "Build the Prompt Logic for generating 5 unique interview questions.",
            "Handle real-time audio chunking for the STT engine.",
            "Create a mock scoring system for audio responses."
        ]
    },
    {
        "name": "Backend: Application Engine & AI Trigger",
        "label": "Backend",
        "tasks": [
            "Develop the 'Submit Application' API (Link User to Job).",
            "Write the background task trigger to call the AI Ranking script.",
            "Build the Employer-only API to see all applicants for a specific job.",
            "Create a Resume storage bucket (Cloud/Local) with URL generation."
        ]
    },
    {
        "name": "Frontend: Employer Dashboard & Ranking View",
        "label": "Frontend",
        "tasks": [
            "Build the 'Candidate List' page for Employers.",
            "Visualize the AI Score (using Progress Bars/Badges) next to each name.",
            "Implement the 'View Detailed Feedback' modal for recruiters.",
            "Setup Protected Routes (only Employers can see the Dashboard)."
        ]
    },
    {
        "name": "UI/UX: Live Interview Room Design",
        "label": "UI/UX",
        "tasks": [
            "Design the 'Interview Room' High-Fidelity prototype.",
            "Design the 'Listening' vs 'Thinking' animations for the AI Bot.",
            "Design the Post-Interview 'Results & Analytics' screen.",
            "Standardize the iconography for Audio/Video toggles."
        ]
    },
    {
        "name": "Network/DevOps: Error Tracking & Monitoring",
        "label": "Network/DevOps",
        "tasks": [
            "Integrate Sentry (or similar) for real-time error logging.",
            "Setup Database Auto-Backup scripts.",
            "Monitor CPU/RAM usage of the AI CV Parsing API on the server.",
            "Configure the final domain/subdomain for the Staging environment."
        ]
    }
]

# ==========================================
# 4. Create Cards and Checklists
# ==========================================
cards_url = "https://api.trello.com/1/cards"

for item in sprint_tasks:
    # Create Card
    label_id = label_map.get(item["label"])
    card_params = {
        "idList": sprint3_id,
        "name": item["name"],
        "idLabels": [label_id] if label_id else [],
        "key": API_KEY,
        "token": TOKEN
    }
    card = requests.post(cards_url, params=card_params).json()
    card_id = card.get("id")

    # Create Checklist inside the card
    checklist_url = f"https://api.trello.com/1/cards/{card_id}/checklists"
    checklist = requests.post(checklist_url, params={"name": "Sprint Tasks", "key": API_KEY, "token": TOKEN}).json()
    checklist_id = checklist.get("id")

    # Add Check-items to the Checklist
    checkitem_url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
    for task in item["tasks"]:
        requests.post(checkitem_url, params={"name": task, "key": API_KEY, "token": TOKEN})

    print(f"Created Card & Checklist for: {item['name']}")

print("\nSprint 3 is fully operational with Checklists! Good luck, Leader.")