# 📄 AI CV Analysis (Gemini + FAISS + RAG)

An intelligent **CV analysis assistant** that helps HR teams and recruiters by:

* Uploading and storing CVs (PDFs or ZIP of PDFs).
* Asking natural language questions about candidates.
* Searching across multiple resumes with semantic similarity.
* Getting concise answers with cited sources.

The system is powered by **RAG (Retrieval-Augmented Generation)**:

1. **Retrieval:** CVs are split into chunks, embedded with **GoogleGenerativeAIEmbeddings**, and stored in **FAISS**.
2. **Augmentation:** When a question is asked, the most relevant chunks are retrieved.
3. **Generation:** The context is passed to **Gemini LLM**, which generates a natural language answer with citations.

---

## 🚀 Features

* Upload CVs (PDF or ZIP).
* Reset and manage the CV vector database.
* Adjustable **Top-K** retrieval and **temperature** for LLM responses.
* Interactive **chat interface** for asking recruitment-related questions.
* Shows answer sources (CV file + page number).
* Live status of the backend system.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Backend:** FastAPI
* **LLM:** Google Gemini API (`gemini-pro`)
* **Vector Database:** FAISS
* **Pipeline:** Custom RAG implementation (`rag_pipeline.py`)

---

## 📂 Project Structure

```
├── app.py                   # Streamlit frontend (UI)
├── backend/                 
│   ├── main.py              # FastAPI entrypoint (endpoints)
│   ├── rag_pipeline.py      # Core RAG pipeline (embeddings, retrieval, QA)
└── README.md
```

---

## ⚙️ Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/ai-cv-analysis.git
   cd ai-cv-analysis
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend (FastAPI server):**

   ```bash
   uvicorn backend.main:app --reload
   ```

5. **Run the Streamlit app:**

   ```bash
   streamlit run app.py
   ```

---

## ⚡ Usage

1. Open the app in your browser (`http://localhost:8501`).
2. Set your **Backend URL** in the sidebar (default: `http://127.0.0.1:8000`).
3. Upload candidate CVs (PDF/ZIP).
4. Ask recruitment-related questions and view AI-powered answers with sources.

---

## 💡 Example HR Questions (Use Cases)

* *“Who has experience with machine learning?”*
* *“List candidates with 5+ years of Python experience.”*
* *“Which candidates worked previously at Microsoft or Google?”*
* *“Who has a Master’s degree in Data Science?”*
* *“Find candidates with strong project management skills.”*
* *“Which candidates are fluent in both English and German?”*

---

## 📊 API Endpoints (Backend)

* `POST /upload` → Upload CV PDFs/ZIP and process into vector store.
* `POST /ask` → Query CV database, returns answer + sources.
* `POST /reset` → Reset the CV vector database.
* `GET /stats` → Get backend statistics.

---

## 🔄 RAG Flow (Diagram)

```
flowchart TD
    A[Upload CVs (PDF/ZIP)] --> B[Chunk & Embed using GoogleGenerativeAIEmbeddings]
    B --> C[Store embeddings in FAISS vector DB]
    D[Ask a Question] --> E[Retrieve Top-K relevant chunks]
    E --> F[Pass context to Gemini LLM]
    F --> G[Generate Answer + Cite Sources]
```

---

## 🔮 Future Work

* Candidate ranking and scoring system.
* Automatic extraction of skills, education, and experience.
* Export shortlisted candidates to Excel/CSV.
* Integration with ATS (Applicant Tracking Systems).

---

## 📧 Contact

Created by **\[Hisham Mislhy]**

* GitHub: [hishamx777](https://github.com/hisamx777)
* Email: [h.mislhy.ai@gmail.com](mailto:h.mislhy.ai@gmail.com)

---
