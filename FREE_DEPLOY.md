# Free Tier Deployment Guide

## Platform Setup (100% Free)

- ✅ **Frontend**: Vercel (Free)
- ✅ **API Gateway**: Vercel (Free)
- ✅ **Python Backend**: Render (Free - sleeps after 15 min inactivity)
- ✅ **Database**: Supabase (Free - 500MB, includes pgvector)

---

## Step 1: Set Up Supabase Database (Free)

### 1.1 Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub (free)
3. Click "New Project"
4. Choose an organization (create one if needed)

### 1.2 Create Project
- **Name**: `trafficlaw-chatbot` (or your choice)
- **Database Password**: Create a strong password (save it!)
- **Region**: Choose closest to you
- **Pricing Plan**: Free
- Click "Create new project" (takes ~2 minutes)

### 1.3 Get Database Connection String
1. Go to **Settings** → **Database**
2. Under **Connection string**, select **URI**
3. Copy the connection string (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`)
4. **Save this** - you'll need it for the Python backend

### 1.4 Enable pgvector (Already Enabled!)
- Supabase has pgvector enabled by default ✅
- No action needed!

---

## Step 2: Set Up Render Python Backend (Free)

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (free)
3. Connect your GitHub account

### 2.2 Deploy Python Backend
1. Click **"New +"** → **"Web Service"**
2. **Connect Repository**: Select your `trafficlaw_chatbot` repository
3. **Configure**:
   - **Name**: `trafficlaw-backend` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main` or `feature/security-performance-optimizations` (your branch)
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `PYTHONPATH=/opt/render/project/src python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (sleeps after 15 min)

### 2.3 Set Environment Variables
Click **"Environment"** tab and add:

```
DATABASE_URL=your_supabase_connection_string_from_step_1.3
GROQ_API_KEY=your_groq_api_key_here
DATA_RAW_PATH=/opt/render/project/src/data/raw
DATA_PROCESSED_PATH=/opt/render/project/src/data/processed
EVAL_TESTSET_PATH=/opt/render/project/src/data/evaluation_testset.csv
ALLOWED_ORIGINS=https://your-api-gateway-url.vercel.app,https://your-frontend-url.vercel.app
```

**Note**: Replace:
- `your_supabase_connection_string` with the string from Step 1.3
- `your_groq_api_key_here` with your actual Groq API key
- `your-api-gateway-url.vercel.app` and `your-frontend-url.vercel.app` - we'll get these in next steps (you can update later)

### 2.4 Upload PDF Files
**Option A: Via Git** (Recommended)
1. Commit your PDFs to the repository (if not already there)
2. Render will automatically deploy them

**Option B: Via Render Dashboard**
1. Go to your service
2. Use Render's file system or persistent disk (may require paid plan)

**Option C: Use Cloud Storage**
- Upload PDFs to Google Drive, Dropbox, or S3
- Update `DATA_RAW_PATH` to point to the storage URL
- Modify backend code to fetch from storage (advanced)

**For now**: If your PDFs are in `data/raw/` in your repo, they'll be available at `/opt/render/project/src/data/raw`

### 2.5 Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (~5-10 minutes)
3. Once deployed, you'll get a URL like: `https://trafficlaw-backend.onrender.com`
4. **Save this URL** - this is your `PYTHON_API_URL`

### 2.6 Test Backend
- Visit: `https://your-backend-url.onrender.com/docs`
- Should show FastAPI docs
- **Note**: First request may be slow (waking up from sleep)

---

## Step 3: Deploy API Gateway on Vercel (Free)

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub (free)
3. Import your GitHub account

### 3.2 Deploy API Gateway
1. Click **"Add New..."** → **"Project"**
2. **Import Git Repository**: Select `trafficlaw_chatbot`
3. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click "Edit" → Set to `frontend/api`
   - **Build Command**: Leave default (auto-detected)
   - **Output Directory**: Leave default
4. **Environment Variables** (click "Environment Variables"):
   Add:
   ```
   PYTHON_API_URL=https://your-backend-url.onrender.com
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   ```
   (We'll update `ALLOWED_ORIGINS` after getting frontend URL)

5. Click **"Deploy"**

### 3.3 Get API Gateway URL
- After deployment, Vercel gives you a URL like: `https://trafficlaw-api.vercel.app`
- **Save this URL** - this is your API Gateway URL

### 3.4 Update Environment Variables
1. Go to **Settings** → **Environment Variables**
2. Update `ALLOWED_ORIGINS` with your actual frontend URL (get it from Step 4)
3. **Redeploy** (go to Deployments → click "..." → Redeploy)

---

## Step 4: Deploy Frontend on Vercel (Free)

### 4.1 Deploy Frontend
1. Click **"Add New..."** → **"Project"** (in Vercel)
2. **Import Git Repository**: Select `trafficlaw_chatbot` (same repo)
3. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click "Edit" → Set to `frontend/web`
   - **Build Command**: Leave default
   - **Output Directory**: Leave default
4. **Environment Variables**:
   Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-gateway-url.vercel.app
   ```
   (Use the API Gateway URL from Step 3.3)

5. Click **"Deploy"**

### 4.2 Get Frontend URL
- After deployment: `https://trafficlaw-web.vercel.app`
- **Save this URL**

### 4.3 Update CORS Origins
Now that you have all URLs:

1. **Update API Gateway** environment variables:
   - Go to API Gateway project in Vercel
   - Settings → Environment Variables
   - Update `ALLOWED_ORIGINS`: `https://your-frontend-url.vercel.app`
   - Redeploy

2. **Update Python Backend** environment variables:
   - Go to Render dashboard
   - Your backend service → Environment
   - Update `ALLOWED_ORIGINS`: `https://your-api-gateway.vercel.app,https://your-frontend.vercel.app`
   - Save (will auto-redeploy)

---

## Step 5: Final Configuration

### 5.1 Verify All Services
- ✅ Frontend: `https://your-frontend.vercel.app`
- ✅ API Gateway: `https://your-api.vercel.app`
- ✅ Python Backend: `https://your-backend.onrender.com`
- ✅ Database: Supabase (connected)

### 5.2 Test Everything
1. **Visit Frontend**: Open your frontend URL
2. **Send Test Message**: Try asking a question
3. **Check Browser Console**: No CORS errors
4. **Check API Health**: Visit `https://your-api.vercel.app/api/health`
5. **Check Backend Docs**: Visit `https://your-backend.onrender.com/docs`

### 5.3 First Request May Be Slow
- Render free tier sleeps after 15 minutes
- First request after sleep takes ~30-60 seconds (cold start)
- Subsequent requests are fast

---

## Troubleshooting

### Backend Returns 503
- **Cause**: Render service is sleeping
- **Fix**: Wait 30-60 seconds, try again (it's waking up)
- **Permanent Fix**: Upgrade to paid plan for always-on

### CORS Errors
- Check `ALLOWED_ORIGINS` includes exact URLs (with `https://`, no trailing slash)
- Verify both API Gateway and Python Backend have correct origins
- Redeploy after changing environment variables

### Database Connection Errors
- Verify `DATABASE_URL` from Supabase is correct
- Check Supabase project is active
- Ensure password is correct

### PDF Files Not Found
- Verify PDFs are in `data/raw/` directory in your repo
- Check `DATA_RAW_PATH` matches the actual path on Render
- For Render free tier, files are in `/opt/render/project/src/`

### 404 Errors
- Check `PYTHON_API_URL` in API Gateway is correct
- Verify backend URL is accessible
- Check root directory settings in Vercel (should be `frontend/api` and `frontend/web`)

---

## Quick Reference: Your URLs

After deployment, you'll have:

```
Frontend:     https://your-frontend.vercel.app
API Gateway:  https://your-api.vercel.app
Python Backend: https://your-backend.onrender.com
Database:     Supabase (internal)
```

---

## Cost Summary

- **Vercel**: $0/month (Free tier)
- **Render**: $0/month (Free tier - sleeps when inactive)
- **Supabase**: $0/month (Free tier - 500MB database)
- **Total**: **$0/month** 🎉

---

## Next Steps After Deployment

1. ✅ Test all functionality
2. ✅ Monitor Render logs for any errors
3. ✅ Set up custom domain (optional, Vercel supports this for free)
4. ✅ Consider upgrading Render if you need always-on (starts at $7/month)

---

**Ready to start?** Follow the steps above in order!

