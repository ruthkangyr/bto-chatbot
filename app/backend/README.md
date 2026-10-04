# HDB BTO Assistant - Backend Service 🐍

The backend service is powered by **FastAPI**, **LangGraph**, and **FAISS**. It orchestrates an Agentic Retrieval-Augmented Generation (RAG) workflow to answer Singapore HDB BTO housing queries using official policy guidelines.

---

## 🏗️ Architecture

```
[ User Query ] ──► [ Orchestrator Agent (Qwen 2.5) ]
                           │
                    Tool Call Needed?
                    ├── No ────────────────────────┐
                    │                              │
                   Yes                             │
                    ▼                              │
         [ FAISS Vector Retriever ]                │
                    │                              │
                    ▼                              │
         [ Relevance Grader (Qwen 2.5) ]           │
                    │                              │
               Is Relevant?                        │
               ├── No (Retry / Re-plan) ───────────┤
              Yes                                  │
               ▼                                   │
         [ Response Generator (Qwen 2.5) ]         │
                    │                              │
                    ▼                              ▼
             [ Formatted Response Returned ]
```

---

## 📋 Prerequisites

1. **Python**: Python 3.11, 3.12, or 3.13.
2. **Local LLM Server (LM Studio)**:
   * Download and install [LM Studio](https://lmstudio.ai/).
   * Download model: **`qwen2.5-7b-instruct`** (choose `Q4_K_M`).
   * Go to the **Local Server (`<->`)** tab, select the model at the top, and click **"Start Server"** on port `1234`.

---

## 🚀 How to Run the Backend (Locally)

### 1. Open Terminal
Navigate to this backend folder:
```powershell
cd "c:\Users\ruth\Documents\Courses\AI in Production\app\backend"
```

### 2. (Recommended) Activate Virtual Environment
```powershell
# Create venv if not already created
python -m venv .venv

# Activate on Windows:
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
# source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Start the FastAPI Server with Uvicorn
```powershell
uvicorn main:app --reload --port 8000
```

* The backend will start on **`http://localhost:8000`** with live auto-reload enabled!
* On startup, it automatically loads official HDB policies, indexes them into FAISS, and connects to LM Studio.

---

## ⚙️ Environment Variables

You can configure the backend via environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LLM_BASE_URL` | `http://localhost:1234/v1` | URL of the local LLM server (LM Studio / vLLM / Ollama) |
| `ORCHESTRATOR_MODEL`| `qwen2.5-7b-instruct` | Model used for agent planning and tool calling |
| `GENERATOR_MODEL` | `qwen2.5-7b-instruct` | Model used for relevance grading and answering |
| `APP_HOST` | `0.0.0.0` | Host IP for FastAPI |
| `APP_PORT` | `8000` | Port for FastAPI |

---

## 🔌 API Endpoints

### 1. Health Check
* **Endpoint:** `GET /api/health` (or `GET /ping`)
* **Response:**
  ```json
  {"status": "ok", "message": "HDB BTO AI Assistant service is healthy!"}
  ```

### 2. Invoke Agent
* **Endpoint:** `POST /api/invoke` (or `POST /invoke`)
* **Request Body:**
  ```json
  {
    "descr": "What is the income ceiling for a 4-room BTO flat for families?"
  }
  ```
* **Response:**
  ```json
  {
    "response": "The monthly household income ceiling for purchasing a new 4-room BTO flat as a family is **$16,000**..."
  }
  ```

