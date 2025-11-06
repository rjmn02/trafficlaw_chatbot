# Deployment Guide

## Overview

This application has **3 services** that need to be deployed:
1. **Next.js Frontend** (`frontend/web`) - User interface
2. **Next.js API Gateway** (`frontend/api`) - Proxy/API layer
3. **Python Backend** (`backend`) - RAG pipeline with ML models

---

## Environment Variables

### 1. Next.js Frontend (`frontend/web`)

Set in your hosting platform (Vercel, Netlify, etc.) or `.env.production`:

```bash
# Required: URL of your Next.js API Gateway
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
```

### 2. Next.js API Gateway (`frontend/api`)

Set in your hosting platform or `.env.production`:

```bash
# Required: URL of your Python backend
PYTHON_API_URL="https://backend.yourdomain.com"

# CRITICAL: Set your production domains for CORS
# This restricts which origins can call your API
ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

**Note**: Security is already implemented with input validation, security headers, and error sanitization. Consider adding rate limiting and authentication for production (see [REMAINING_SECURITY.md](./REMAINING_SECURITY.md)).

**Important**: Replace `yourdomain.com` with your actual domain(s). If you have multiple domains, separate them with commas:
```bash
ALLOWED_ORIGINS="https://trafficlaw.com,https://www.trafficlaw.com,https://app.trafficlaw.com"
```

### 3. Python Backend (`backend`)

Set in your hosting platform (Railway, Render, Fly.io, etc.) or `.env`:

```bash
# Database
DATABASE_URL="postgresql+asyncpg://user:pass@host:port/dbname"
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=trafficlawdb
POSTGRES_HOST=your_db_host
POSTGRES_PORT=5432

# External APIs
GROQ_API_KEY="your_groq_api_key"

# Data paths (adjust for your server filesystem)
DATA_RAW_PATH="/path/to/data/raw"
DATA_PROCESSED_PATH="/path/to/data/processed"
EVAL_TESTSET_PATH="/path/to/evaluation_testset.csv"

# CRITICAL: Set your production domains for CORS (must match Next.js API Gateway)
ALLOWED_ORIGINS="https://api.yourdomain.com,https://yourdomain.com,https://www.yourdomain.com"
```

**Note**: The `ALLOWED_ORIGINS` in the Python backend should include:
- Your Next.js API Gateway URL (where requests come from)
- Your frontend domain (if accessing Python backend directly, though unlikely)

---

## Deployment Steps by Platform

### Option A: Vercel (Frontend + API Gateway) + Railway (Python Backend)

#### Frontend (`frontend/web`):
1. Deploy to Vercel
2. Set environment variable: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`

#### API Gateway (`frontend/api`):
1. Deploy to Vercel as a separate project
2. Set environment variables:
   - `PYTHON_API_URL=https://backend.yourdomain.com`
   - `ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`

#### Python Backend (`backend`):
1. Deploy to Railway/Render/Fly.io
2. Set all environment variables from the "Python Backend" section above
3. Make sure `ALLOWED_ORIGINS` includes your API Gateway URL

---

### Option B: Docker Compose (Single Server)

1. Create a `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    depends_on:
      - postgres

  api:
    build: ./frontend/api
    environment:
      - PYTHON_API_URL=http://backend:8000
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    depends_on:
      - backend

  web:
    build: ./frontend/web
    environment:
      - NEXT_PUBLIC_API_URL=http://api:3001
    depends_on:
      - api

volumes:
  postgres_data:
```

2. Set all environment variables in `.env` file
3. Run: `docker compose -f docker-compose.prod.yml up -d`

---

## Pre-Deployment Checklist

- [ ] Set `ALLOWED_ORIGINS` in **both** Next.js API Gateway and Python Backend
- [ ] Update `NEXT_PUBLIC_API_URL` in frontend to point to your API Gateway URL
- [ ] Update `PYTHON_API_URL` in API Gateway to point to your Python backend URL
- [ ] Set all database credentials (`DATABASE_URL`, etc.)
- [ ] Set `GROQ_API_KEY` in Python backend
- [ ] Ensure data paths (`DATA_RAW_PATH`, etc.) exist on the server
- [ ] Test CORS by making a request from your frontend domain
- [ ] Ensure PostgreSQL has `vector` extension enabled: `CREATE EXTENSION IF NOT EXISTS vector;`

---

## Testing After Deployment

### 1. Test Frontend → API Gateway
```bash
curl https://api.yourdomain.com/api/health
```

### 2. Test API Gateway → Python Backend
```bash
curl -X POST https://api.yourdomain.com/api/chat \
  -H "Content-Type: application/json" \
  -H "Origin: https://yourdomain.com" \
  -d '{"session_id":"test","query":"What is the speed limit?"}'
```

### 3. Test CORS
Open browser console on your frontend and check for CORS errors. If you see:
- ✅ No CORS errors = Good!
- ❌ `Access-Control-Allow-Origin` error = Check `ALLOWED_ORIGINS` includes your frontend domain

---

## Common Issues

### CORS Errors After Deployment
**Problem**: Frontend can't call API Gateway

**Solution**: 
1. Check `ALLOWED_ORIGINS` includes your frontend domain (exactly as it appears in the browser)
2. Check `ALLOWED_ORIGINS` includes both `http://` and `https://` if needed
3. Check `ALLOWED_ORIGINS` has no trailing slashes (use `https://domain.com` not `https://domain.com/`)

### 404 Errors
**Problem**: API Gateway can't reach Python backend

**Solution**: 
1. Check `PYTHON_API_URL` in API Gateway is correct
2. Check Python backend is running and accessible
3. Check firewall/network settings allow connections

### Database Connection Errors
**Problem**: Python backend can't connect to PostgreSQL

**Solution**:
1. Check `DATABASE_URL` is correct
2. Check PostgreSQL container/service is running
3. Check network connectivity between services
4. Verify `vector` extension is installed: `CREATE EXTENSION IF NOT EXISTS vector;`

---

## Security Notes

1. **Never commit `.env` files** - Use platform environment variable settings
2. **Use HTTPS in production** - All services should use HTTPS
3. **Restrict `ALLOWED_ORIGINS`** - Only include your actual domains
4. **Keep `GROQ_API_KEY` secret** - Don't expose it in client-side code
5. **Use strong database passwords** - Especially in production

