# Quick Deployment Guide

## Step 1: Choose Your Platforms

### Recommended Setup:
- **Frontend + API Gateway**: [Vercel](https://vercel.com) (Free tier available)
- **Python Backend**: [Railway](https://railway.app) or [Render](https://render.com) (Free tier available)
- **Database**: Railway/Render PostgreSQL or [Supabase](https://supabase.com) (Free tier available)

---

## Step 2: Deploy Database First

### Option A: Railway PostgreSQL
1. Go to [Railway.app](https://railway.app)
2. Create new project → Add PostgreSQL
3. Copy the `DATABASE_URL` from the Variables tab
4. Enable pgvector extension (Railway does this automatically, or run: `CREATE EXTENSION IF NOT EXISTS vector;`)

### Option B: Render PostgreSQL
1. Go to [Render.com](https://render.com)
2. New → PostgreSQL
3. Copy the `DATABASE_URL` from the dashboard
4. Connect via psql and run: `CREATE EXTENSION IF NOT EXISTS vector;`

### Option C: Supabase
1. Go to [Supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → Database → Connection string
4. pgvector is enabled by default

---

## Step 3: Deploy Python Backend

### Railway (Recommended)
1. **Connect Repository**:
   - Go to Railway dashboard
   - New Project → Deploy from GitHub repo
   - Select your `trafficlaw_chatbot` repository
   - Set root directory to `backend`

2. **Set Environment Variables**:
   ```
   DATABASE_URL=your_postgresql_connection_string
   GROQ_API_KEY=your_groq_api_key
   DATA_RAW_PATH=/app/data/raw
   DATA_PROCESSED_PATH=/app/data/processed
   EVAL_TESTSET_PATH=/app/data/evaluation_testset.csv
   ALLOWED_ORIGINS=https://your-api-gateway-url.vercel.app,https://your-frontend-url.vercel.app
   ```

3. **Upload PDFs**:
   - Railway provides persistent storage
   - Or use a service like S3/Cloud Storage and update `DATA_RAW_PATH`
   - Or mount a volume with your PDFs

4. **Set Start Command** (if needed):
   ```
   PYTHONPATH=/app python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Get Backend URL**: Railway will give you a URL like `https://your-app.railway.app`

### Render
1. New → Web Service
2. Connect GitHub repo
3. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `PYTHONPATH=/app python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Set environment variables (same as Railway above)
5. Get your backend URL

---

## Step 4: Deploy API Gateway (Vercel)

1. **Go to [Vercel](https://vercel.com)** and sign in with GitHub

2. **Deploy API Gateway**:
   - Click "Add New Project"
   - Import your repository
   - **Root Directory**: Set to `frontend/api`
   - Framework Preset: Next.js
   - Click "Deploy"

3. **Set Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     PYTHON_API_URL=https://your-backend-url.railway.app
     ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
     ```

4. **Redeploy** after adding environment variables

5. **Get API Gateway URL**: Vercel gives you a URL like `https://your-api.vercel.app`

---

## Step 5: Deploy Frontend (Vercel)

1. **Deploy Frontend**:
   - Click "Add New Project" in Vercel
   - Import the same repository
   - **Root Directory**: Set to `frontend/web`
   - Framework Preset: Next.js
   - Click "Deploy"

2. **Set Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-api-gateway-url.vercel.app
     ```

3. **Redeploy** after adding environment variables

4. **Get Frontend URL**: Vercel gives you a URL like `https://your-frontend.vercel.app`

---

## Step 6: Update CORS Origins

After getting all URLs:

1. **Update Python Backend** `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-api-gateway.vercel.app,https://your-frontend.vercel.app
   ```

2. **Update API Gateway** `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

3. **Redeploy both services**

---

## Step 7: Test Everything

1. **Frontend**: Visit your frontend URL
2. **Send a test message**: Check if chat works
3. **Check browser console**: No CORS errors
4. **Check API Gateway health**: `https://your-api.vercel.app/api/health`
5. **Check Python backend**: `https://your-backend.railway.app/docs`

---

## Troubleshooting

### CORS Errors
- Make sure `ALLOWED_ORIGINS` includes your exact frontend URL (with `https://`)
- No trailing slashes in URLs
- Redeploy after changing environment variables

### 404 Errors
- Check `PYTHON_API_URL` in API Gateway is correct
- Check backend is running and accessible

### Database Connection
- Verify `DATABASE_URL` is correct
- Check PostgreSQL is running
- Ensure `vector` extension is enabled

### PDF Files Not Found
- Upload PDFs to your backend's `DATA_RAW_PATH`
- For Railway: Use persistent storage or volumes
- For Render: Use persistent disks

---

## Quick Reference: Environment Variables

### Python Backend
```
DATABASE_URL=postgresql+asyncpg://...
GROQ_API_KEY=...
DATA_RAW_PATH=/app/data/raw
DATA_PROCESSED_PATH=/app/data/processed
EVAL_TESTSET_PATH=/app/data/evaluation_testset.csv
ALLOWED_ORIGINS=https://api.vercel.app,https://frontend.vercel.app
```

### API Gateway
```
PYTHON_API_URL=https://backend.railway.app
ALLOWED_ORIGINS=https://frontend.vercel.app
```

### Frontend
```
NEXT_PUBLIC_API_URL=https://api.vercel.app
```

---

**Need help?** Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

