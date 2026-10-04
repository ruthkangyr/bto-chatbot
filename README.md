# Singapore HDB BTO & Housing Grants AI Assistant 🏠🇸🇬

An **Agentic RAG (Retrieval-Augmented Generation)** chatbot designed to help Singapore citizens navigate the **HDB Build-To-Order (BTO)** buying journey, flat classifications (**Standard, Plus, Prime**), CPF housing grants (up to **$120,000**), eligibility criteria, and the **HDB Flat Eligibility (HFE)** application process.

---

## 🌟 Overview & Key Features

* **Authoritative Housing Knowledge**: Covers Singapore's latest public housing framework:
  * **New Classification Framework**: Standard, Plus, and Prime flats (MOP rules, subsidy recovery/clawback, and resale conditions).
  * **Eligibility Schemes**: Public Scheme, Fiancé/Fiancée Scheme, Single Singapore Citizen Scheme (age 35+), Joint Singles Scheme.
  * **Housing Grants**: Enhanced CPF Housing Grant (EHG) up to $120,000 for families and $60,000 for singles, Step-Up CPF Housing Grant, and Staggered Downpayment Scheme.
  * **HFE Letter Process**: Step-by-step guidance, 9-month validity, and Deferred Income Assessment (DIA) for students/young couples.
* **Agentic Self-Corrective RAG**: Built with **LangGraph** to dynamically plan tool usage, retrieve context, grade document relevance, and synthesize responses.
* **Modern Web UI**: Responsive emerald/teal theme with clickable starter topic chips, markdown bubble rendering, and a real-time typing indicator.
* **Containerized & Production-Ready**: Pre-packaged Docker container with environment variable configuration for local and cloud deployment.

---

## 🧠 Architecture & Agentic Workflow

```
       [ User Query ]
             │
             ▼
    ┌─────────────────┐
    │  Orchestrator   │ (Meta Llama 3.1 8B)
    │  Agent Node     │ Decides whether to query the knowledge base
    └────────┬────────┘
             │
      Tool Call Needed?
       ├─── No ───────────────────────┐
       │                              │
      Yes                             │
       ▼                              │
    ┌─────────────────┐               │
    │  Retriever Tool │ (FAISS + HuggingFace Embeddings)
    │  Node           │ Fetches semantic chunks
    └────────┬────────┘               │
             │                        │
             ▼                        │
    ┌─────────────────┐               │
    │ Relevance Grader│ (DeepSeek R1 Distill)
    │ Conditional Edge│ Validates retrieved content
    └────────┬────────┘               │
             │                        │
       Is Relevant?                   │
       ├─── No (Retry / Re-plan) ─────┤
      Yes                             │
       ▼                              │
    ┌─────────────────┐               │
    │  Generate Node  │ (DeepSeek R1 Distill)
    │  Synthesis      │ Rephrases & structures final advice
    └────────┬────────┘               │
             │                        │
             ▼                        ▼
     [ Final Response Streamed to User ]
```


---

### 🌐 Data Sources

The application ingests official housing knowledge directly from the following Singapore **Housing & Development Board (HDB)** pages using LangChain's `WebBaseLoader`:
* `https://www.hdb.gov.sg/buying-a-flat`
* `https://www.hdb.gov.sg/buying-a-flat/bto-sbf-and-open-booking-of-flats/finding-a-new-flat`
* `https://www.hdb.gov.sg/buying-a-flat/bto-sbf-and-open-booking-of-flats/process-for-buying-a-new-flat`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/application-for-an-hdb-flat-eligibility-hfe-letter`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/couples-and-families`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/couples-and-families/enhanced-cpf-housing-grant`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/couples-and-families/stepup-cpf-housing-grant`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/singles`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/singles/enhanced-cpf-housing-grant`
* `https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/housing-loan/housing-loan-from-hdb`

It also loads curated offline guidelines from [`app/data/bto_knowledge.md`]. The combined content is split into semantic chunks, embedded with HuggingFace `sentence-transformers/all-mpnet-base-v2`, and indexed in a FAISS vector store.

---

## 🛠️ Technology Stack

* **Frontend**: [Node.js](https://nodejs.org/), [React 18](https://react.dev/), [Vite](https://vitejs.dev/), [Tailwind CSS](https://tailwindcss.com/), [Lucide Icons](https://lucide.dev/), [React-Markdown](https://github.com/remarkjs/react-markdown)
* **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
* **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain)
* **Vector Store**: [FAISS (Facebook AI Similarity Search)](https://github.com/facebookresearch/faiss)
* **Embeddings**: HuggingFace `sentence-transformers/all-mpnet-base-v2`
* **LLMs Supported (OpenAI Compatible API)**:
  * **Default Unified Model**: `qwen2.5-7b-instruct` (handles both orchestration and answering seamlessly!)
  * **Optional Multi-Model**: `qwen2.5-7b-instruct` (orchestrator) + `deepseek-r1-distill-qwen-14b` (reasoning)
* **Local Inference Server**: LM Studio / vLLM / Ollama (OpenAI-compatible endpoint at `http://localhost:1234/v1`)
* **Containerization**: Docker (Multi-stage Node.js + Python build)

---

## 📋 Prerequisites & Tools

1. **Docker Desktop** (for running via container) or **Python 3.11/3.12/3.13** (for local development).
2. **LM Studio** (free desktop software to run open-weights AI models locally).

---

## 🤖 Setting Up LM Studio (Step-by-Step)

The chatbot connects to a local LLM server at `http://localhost:1234/v1` powered by **LM Studio**. This allows the entire AI pipeline to run 100% locally and free on your computer without paid API keys.

### 1. Download & Install LM Studio
* Download the free installer for Windows/macOS from the official website: [https://lmstudio.ai/](https://lmstudio.ai/)
* Run the installer and open LM Studio.

### 2. Download the Recommended Model
* In the left sidebar or top bar of LM Studio, click the **Search** (magnifying glass) icon.
* Search for: `Qwen2.5-7B-Instruct`
* In the search results, select the model (e.g. from `lmstudio-community` or `bartowski`).
* Choose quantization: **`Q4_K_M`** (recommended balance between speed, memory usage, and quality).
* Click **Download**.
* *(Optional)* If your system has 16GB+ RAM and you want advanced reasoning, you can also search and download `DeepSeek-R1-Distill-Qwen-14B` (`Q4_K_M`). However, `Qwen2.5-7B-Instruct` alone can easily handle both tasks!

### 3. Start the Local Server
* Click the **Developer / Local Server** tab in the left sidebar (looks like `<->` or a terminal screen).
* At the top dropdown (**Select a model to load**), select your downloaded `Qwen2.5-7B-Instruct` model.
* Confirm the port is set to **`1234`** (default).
* Click the green **"Start Server"** button.
* When you see `Status: Server is running on port 1234`, **leave LM Studio running in the background**.

---

## 🚀 Setup & Running with Docker

### Step 1: Open Docker Desktop
Ensure **Docker Desktop** is launched and running on your system (check for the Docker whale icon in your taskbar).

### Step 2: Build the Docker Image

* **If you are inside the `app/` folder:**
  ```bash
  docker build -t hdb-bto-assistant .
  ```
* **If you are in the root directory (`AI in Production`):**
  ```bash
  docker build -t hdb-bto-assistant ./app
  ```

### Step 3: Run the Container

#### On Windows / macOS (Docker Desktop):
Because the container needs to access your local LM Studio server running on the host machine, use `host.docker.internal`:
```bash
docker run -d -p 8000:8000 \
  -e LLM_BASE_URL="http://host.docker.internal:1234/v1" \
  --name hdb-assistant-app \
  hdb-bto-assistant
```

#### On Linux:
```bash
docker run -d --network host \
  --name hdb-assistant-app \
  hdb-bto-assistant
```

### Step 4: Verify & View Logs
Check that the application has scraped HDB pages and initialized the vector store:
```bash
docker logs -f hdb-assistant-app
```
*(Press `Ctrl + C` anytime to exit the log stream).*

### Step 5: Access the Web Interface
Open your web browser (Chrome, Edge, etc.) and navigate to:
👉 **`http://localhost:8000`**

### Handy Docker Management Commands
* **Check running containers:** `docker ps`
* **Stop the container:** `docker stop hdb-assistant-app`
* **Restart the container:** `docker start hdb-assistant-app`
* **Remove the container:** `docker rm -f hdb-assistant-app`

---

## 💻 Running Locally in Development (Without Docker)

You can run both services locally with live hot-reloading. For detailed setup guides, check the dedicated READMEs:
* 🐍 **Backend Documentation:** [`app/backend/README.md`](file:///c:/Users/ruth/Documents/Courses/AI%20in%20Production/app/backend/README.md)
* ⚛️ **Frontend Documentation:** [`app/frontend/README.md`](file:///c:/Users/ruth/Documents/Courses/AI%20in%20Production/app/frontend/README.md)

---

### Step 1: Start the FastAPI Backend
Open your first terminal window:
```powershell
# 1. Navigate to the backend directory
cd "c:\Users\ruth\Documents\Courses\AI in Production\app\backend"

# 2. (Optional) Activate your virtual environment
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

# 3. Install requirements (first time only)
pip install -r requirements.txt

# 4. Start the backend server with Uvicorn
uvicorn main:app --reload --port 8000
```
* The backend will start on **`http://localhost:8000`** with live auto-reload!
* It loads official HDB policies, initializes FAISS, and connects to LM Studio on port 1234.

---

### Step 2: Start the Node.js + Tailwind CSS Frontend
Open a **second** terminal window:
```powershell
# 1. Navigate to the frontend directory
cd "c:\Users\ruth\Documents\Courses\AI in Production\app\frontend"

# 2. Install Node dependencies (first time only)
npm install

# 3. Start the Vite development server
npm run dev
```
* Vite will launch on **`http://localhost:5173`**.
* Open your browser and go to:
  👉 **`http://localhost:5173`**
* All queries are automatically proxied to the FastAPI backend on port `8000`, with instant Hot Module Replacement as you edit React components!

---

## 💬 Sample Questions to Try

* **Singles Eligibility**: *"Can a single 35-year-old Singapore Citizen buy a BTO flat, and which types are allowed?"*
* **Flat Classifications**: *"What is the difference between Standard, Plus, and Prime BTO flats under the new framework?"*
* **Housing Grants**: *"What is the maximum Enhanced CPF Housing Grant (EHG) for first-timer families and what is the income ceiling?"*
* **Application Process**: *"What is the HDB Flat Eligibility (HFE) letter and when should I apply for it?"*
* **Disposal of Private Property**: *"How long must I wait to apply for a BTO after selling my private property?"*

---

## 📁 Project Structure

```
.
├── app/
│   ├── backend/                 # 🐍 Python FastAPI & LangGraph service
│   │   ├── data/
│   │   │   └── bto_knowledge.md # Authoritative Singapore HDB BTO dataset
│   │   ├── models/              # Cached embedding model weights
│   │   ├── main.py              # LangGraph agent workflow & FastAPI endpoints
│   │   └── requirements.txt     # Python dependencies
│   │
│   ├── frontend/                # ⚛️ Node.js + React + Tailwind CSS web application
│   │   ├── src/
│   │   │   ├── components/      # Header, QuickTopics, ChatMessage, ChatInput
│   │   │   ├── App.jsx          # Main state & API communication
│   │   │   ├── index.css        # Tailwind directives & styles
│   │   │   └── main.jsx         # React root
│   │   ├── dist/                # Production compiled frontend bundle
│   │   ├── package.json         # Node dependencies (Tailwind, Lucide, React)
│   │   ├── tailwind.config.js   # Tailwind theme configuration
│   │   └── vite.config.js       # Vite dev server & backend proxy
│   │
│   └── Dockerfile               # Production multi-stage Docker build
└── README.md                    # Project documentation
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive chatbot web UI |
| `GET` | `/ping` | Health check endpoint |
| `POST` | `/invoke` | Sends user query to the LangGraph agent and returns synthesized response |

#### Example `/invoke` Request:
```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"descr": "What is the Enhanced CPF Housing Grant amount for families?"}'
```
