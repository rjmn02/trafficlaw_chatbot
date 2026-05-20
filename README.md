# Traffic Law Chatbot

An AI-powered RAG (Retrieval-Augmented Generation) chatbot designed to answer questions related to traffic laws. It uses a modern React frontend and a FastAPI backend connected to a PostgreSQL database with pgvector for semantic search.
![alt text](<Screenshot 2026-05-18 180933.png>)

## 🌟 Features

- **Conversational Interface**: Modern chat UI with typing indicators, markdown support, and session management.
- **RAG Architecture**: Accurately fetches relevant traffic laws and regulations to ground the LLM's responses using pgvector.
- **Session Memory**: Remembers past conversations and maintains chat history for context.
- **Vercel Ready**: Easily deploy both frontend and backend on Vercel as a monorepo.

## 🏗 Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS (via components)
- **Backend**: Python, FastAPI, Groq API (LLM)
- **Database**: PostgreSQL with pgvector (via Docker/Supabase)

---

## 🚀 Getting Started

### 1. Prerequisites

- **Node.js**: v16+
- **Python**: 3.9+
- **Supabase Account**: For the hosted PostgreSQL database, OR **Docker** if running locally.

### 2. Environment Setup

Copy the example environment file or create new ones for backend and frontend:

#### Backend (`backend/.env`)
```env
user=root
password=rootpass
host=localhost
port=5432
dbname=trafficlawdb
SUPABASE_DB_URL=postgresql+psycopg2://$user:$password@$host:$port/$dbname

GROQ_API_KEY="your_groq_api_key"
HF_TOKEN="your_huggingface_token"
ALLOWED_ORIGINS="" # Leave empty for local, set to Vercel URL in production

DATA_RAW_PATH="../data/raw"
DATA_PROCESSED_PATH="../data/processed"
EVAL_TESTSET_PATH="../data/evaluation_testset.csv"
```

#### Frontend (`frontend/.env`)
```env
# URL for the backend API.
# Leave unset for local development (Vite proxies /api/* to http://127.0.0.1:8000)
# VITE_API_URL=/_/backend
```

### 3. Local Development

#### Start the Database

**Primary Option: Supabase**
This project primarily uses [Supabase](https://supabase.com/) for its PostgreSQL database.
1. Create a project on Supabase and enable the `pgvector` extension.
2. Copy your connection string into the `SUPABASE_DB_URL` variable in your `backend/.env` file.

**Alternative Option: Local Docker**
If you prefer running the database locally, spin up the `pgvector` Postgres container:
 ```bash
docker-compose up -d
 ```

#### Start the Backend (FastAPI)
 ```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Start the Frontend (Vite)
 ```bash
cd frontend
npm install
npm run dev
```
The application will be available at `http://localhost:5173`.


---

## ☁️ Deployment (Vercel)

This project is configured as a monorepo for Vercel deployment via `vercel.json`.

1. Import the repository into Vercel.
2. In the Vercel project settings, set the **Framework Preset** to `Vite`.
3. Add the required Environment Variables in Vercel settings (e.g., `GROQ_API_KEY`, `HF_TOKEN`, `SUPABASE_DB_URL`, `VITE_API_URL=/_/backend`, and `ALLOWED_ORIGINS="https://your-vercel-app-url.vercel.app"`).
4. Deploy! Requests to `/_/backend` will be routed securely to your FastAPI service.

## 🧠 System Architecture

The project consists of three main components working together to provide an AI-powered conversational experience:

1. **Frontend (Vite + React)**: 
   - A single-page application that provides a chat interface to the user.
   - It proxies API calls to the backend during local development, and routes them appropriately in production via Vercel.

2. **Backend (Python + FastAPI)**:
   - Exposes REST API endpoints (`/chat`, `/sessions`).
   - Implements the RAG (Retrieval-Augmented Generation) pipeline: it takes user queries, builds an embedding, retrieves similar documents from the database, and queries the Groq LLM API.

3. **Database (PostgreSQL + pgvector)**:
   - Stores pre-processed traffic law document embeddings.
   - Uses `pgvector` extension for fast semantic similarity search.

**Core Workflow**:
User Input → Frontend Chat UI → FastAPI `/chat` endpoint → pgvector retrieval → LLM Generation (Groq) → Response parsed & sent back to User.
