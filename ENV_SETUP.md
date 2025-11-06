# Environment Files Setup

You need to create **3 separate environment files**. Here's exactly what goes where:

---

## File 1: `.env` (Project Root)

**Location**: `/Users/jem/Documents/trafficlaw_chatbot/.env`

**Used by**: Python Backend (`backend/main.py`)

**Contents**:
```bash
# Database
DATABASE_URL="postgresql+asyncpg://root:rootpass@localhost:5432/trafficlawdb"
POSTGRES_USER=root
POSTGRES_PASSWORD=rootpass
POSTGRES_DB=trafficlawdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# External APIs
GROQ_API_KEY="your_groq_api_key_here"

# Data paths
DATA_RAW_PATH="/Users/jem/Documents/trafficlaw_chatbot/data/raw"
DATA_PROCESSED_PATH="/Users/jem/Documents/trafficlaw_chatbot/data/processed"
EVAL_TESTSET_PATH="/Users/jem/Documents/trafficlaw_chatbot/data/evaluation_testset.csv"

# CORS (for production - optional for development)
# ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

**For Production**: Uncomment and set `ALLOWED_ORIGINS` to your actual domain(s)

---

## File 2: `frontend/web/.env.local`

**Location**: `/Users/jem/Documents/trafficlaw_chatbot/frontend/web/.env.local`

**Used by**: Next.js Frontend (`frontend/web`)

**Contents**:
```bash
NEXT_PUBLIC_API_URL="http://localhost:3001"
```

**For Production**: Change to your API Gateway URL:
```bash
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
```

---

## File 3: `frontend/api/.env.local`

**Location**: `/Users/jem/Documents/trafficlaw_chatbot/frontend/api/.env.local`

**Used by**: Next.js API Gateway (`frontend/api`)

**Contents**:
```bash
PYTHON_API_URL="http://localhost:8000"
```

**For Production**: Change to your Python backend URL and add CORS:
```bash
PYTHON_API_URL="https://backend.yourdomain.com"
ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

---

## Quick Summary

| File | Location | What It Does |
|------|----------|--------------|
| `.env` | Project root | Python backend config (database, API keys, CORS) |
| `frontend/web/.env.local` | `frontend/web/` | Frontend knows where API Gateway is |
| `frontend/api/.env.local` | `frontend/api/` | API Gateway knows where Python backend is + CORS |

---

## For Development (Right Now)

You can create these files with these commands:

```bash
# 1. Create root .env (copy from example.env and fill in your values)
cp example.env .env
# Then edit .env and fill in your actual GROQ_API_KEY and paths

# 2. Create frontend/web/.env.local
echo 'NEXT_PUBLIC_API_URL="http://localhost:3001"' > frontend/web/.env.local

# 3. Create frontend/api/.env.local
echo 'PYTHON_API_URL="http://localhost:8000"' > frontend/api/.env.local
```

---

## For Production

When deploying, set these as **environment variables** in your hosting platform:

- **Vercel/Netlify (Frontend)**: Set `NEXT_PUBLIC_API_URL`
- **Vercel/Netlify (API Gateway)**: Set `PYTHON_API_URL` and `ALLOWED_ORIGINS`
- **Railway/Render/Fly.io (Python Backend)**: Set all variables from root `.env` + `ALLOWED_ORIGINS`

**Important**: In production, you don't create `.env` files - you set environment variables in your platform's dashboard.

