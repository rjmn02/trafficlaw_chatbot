# Traffic Law Chatbot

An AI-powered RAG (Retrieval-Augmented Generation) chatbot designed to answer questions related to traffic laws. It uses a modern React frontend and a FastAPI backend connected to a PostgreSQL database with pgvector for semantic search.

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
- **Docker**: For running the local PostgreSQL database

### 2. Environment Setup

Copy the example environment file or create new ones for backend and frontend:

#### Backend (\ackend/.env\)
\\\env
user=root
password=rootpass
host=localhost
port=5432
dbname=trafficlawdb
SUPABASE_DB_URL=postgresql+psycopg2://$user:$password@$host:$port/$dbname

GROQ_API_KEY="your_groq_api_key"
GROQ_PROD_KEY="your_groq_prod_key"

DATA_RAW_PATH="../data/raw"
DATA_PROCESSED_PATH="../data/processed"
EVAL_TESTSET_PATH="../data/evaluation_testset.csv"
\\\

#### Frontend (\rontend/.env\)
\\\env
# URL for the backend API.
# Leave unset for local development (Vite proxies /api/* to http://127.0.0.1:8000)
# VITE_API_URL=/_/backend
\\\

### 3. Local Development

#### Start the Database
Spin up the \pgvector\ Postgres database via Docker:
\\\ash
docker-compose up -d
\\\

#### Start the Backend (FastAPI)
\\\ash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
\\\

#### Start the Frontend (Vite)
\\\ash
cd frontend
npm install
npm run dev
\\\
The application will be available at \http://localhost:5173\.

---

## ☁️ Deployment (Vercel)

This project is configured as a monorepo for Vercel deployment via \ercel.json\.

1. Import the repository into Vercel.
2. In the Vercel project settings, set the **Framework Preset** to \Vite\.
3. Add the required Environment Variables in Vercel settings (e.g., \GROQ_API_KEY\, \SUPABASE_DB_URL\, \VITE_API_URL=/_/backend\).
4. Deploy! Requests to \/_/backend\ will be routed securely to your FastAPI service.

## 🧠 RAG System Architecture
![Architecture](image-1.png)
