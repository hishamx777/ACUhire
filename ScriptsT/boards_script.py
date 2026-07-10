import requests

# ==========================================
# 1. Place your API Key, Token, and Board ID here
# ==========================================
API_KEY = "18482e7216f9b3ba3c2072364327d4b1"
TOKEN = "ATTA97644a56e63500222cab7b8966e3b86988b6a7d8563743d24e3b5e5afc7b653aB205A98B"
BOARD_ID = "AKyrqFZM" 

# ==========================================
# 2. Fetch List and Label IDs
# ==========================================
print("Fetching Board Data...")

# Get the List ID for Sprint 1
lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
lists_response = requests.get(lists_url, params={"key": API_KEY, "token": TOKEN}).json()

# Looking for "Sprint 1" in the list name
sprint_list_id = next((lst['id'] for lst in lists_response if "Sprint 1" in lst['name']), None)

# Get the Label IDs
labels_url = f"https://api.trello.com/1/boards/{BOARD_ID}/labels"
labels_response = requests.get(labels_url, params={"key": API_KEY, "token": TOKEN}).json()
label_map = {lbl['name']: lbl['id'] for lbl in labels_response}

if not sprint_list_id:
    print("Error: Could not find 'Sprint 1' list. Make sure the setup script ran successfully.")
    exit()

# ==========================================
# 3. Cards Data (Tasks and Details)
# ==========================================
cards_data = [
    {
        "name": "UI/UX: Platform Design Foundation",
        "label": "UI/UX",
        "desc": "**Required Tasks:**\n- Map out the complete User Flow for the platform.\n- Design Wireframes for Login/Signup pages.\n- Design Wireframes for the Job Feed page."
    },
    {
        "name": "Backend: Database & API Setup",
        "label": "Backend",
        "desc": "**Required Tasks:**\n- Design the Entity-Relationship Diagram (ERD).\n- Initialize the backend environment (FastAPI / Node.js).\n- Develop the Login API and connect it to the database."
    },
    {
        "name": "Frontend: Web Project Initialization",
        "label": "Frontend",
        "desc": "**Required Tasks:**\n- Initialize the web project (React / Next.js).\n- Build static UI components (Navbar, Sidebar).\n- Develop the Job Feed page using Mock Data."
    },
    {
        "name": "Network/DevOps: Environment & Version Control",
        "label": "Network/DevOps",
        "desc": "**Required Tasks:**\n- Create a GitHub Organization and invite the team.\n- Set up essential branches (main, dev).\n- Research free cloud hosting via GitHub Student Developer Pack."
    },
    {
        "name": "AI (Team Leader): Core Algorithm Preparation",
        "label": "AI (Team Leader)",
        "desc": "**Required Tasks:**\n- Wrap the CV Parsing script (pdfplumber) into an API endpoint.\n- Test YOLOv8 Nano locally for Mobile/Person detection.\n- Monitor team progress and unblock any technical issues."
    }
]

# ==========================================
# 4. Create Cards in Trello
# ==========================================
print("Creating cards and assigning tasks...")
cards_url = "https://api.trello.com/1/cards"

for card in cards_data:
    label_id = label_map.get(card["label"])
    
    querystring = {
        "idList": sprint_list_id,
        "name": card["name"],
        "desc": card["desc"],
        "idLabels": [label_id] if label_id else [],
        "key": API_KEY,
        "token": TOKEN
    }
    
    requests.post(cards_url, params=querystring)
    print(f"Successfully created card: {card['name']}")

print("\nAwesome Leader! Tasks have been distributed successfully. Check your Trello board.")