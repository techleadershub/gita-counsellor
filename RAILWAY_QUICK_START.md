# Railway Production Deployment - Quick Start Guide

This guide will help you deploy the Bhagavad Gita Research Agent to Railway production in under 15 minutes.

## Prerequisites

- ✅ Railway account ([railway.app](https://railway.app))
- ✅ GitHub repository with your code
- ✅ OpenAI API Key
- ✅ All code committed and pushed to GitHub

## Step-by-Step Deployment

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your repository
5. Railway will create a new project

### Step 2: Deploy Qdrant Service

1. In your Railway project, click **"+ New"** → **"Empty Service"**
2. Name it: `qdrant`
3. Click on the service → **"Settings"** → **"Generate Domain"** (note the domain)
4. Go to **"Deploy"** tab → Click **"Configure"**
5. Select **"Docker Hub Image"**
6. Enter image: `qdrant/qdrant:latest`
7. Add environment variables:
   ```
   QDRANT__SERVICE__HTTP_PORT=6333
   QDRANT__SERVICE__GRPC_PORT=6334
   ```
8. Click **"Deploy"**
9. Wait for deployment (~2-3 minutes)
10. **Copy the service URL** (e.g., `qdrant-production.up.railway.app`)

### Step 3: Deploy Backend Service

1. In your Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select your repository
3. Name it: `backend`
4. Go to **"Settings"**:
   - **Root Directory**: Leave empty (project root) ⚠️ **IMPORTANT**
   - **Dockerfile Path**: `backend/Dockerfile`
5. Go to **"Variables"** tab and add:

   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here
   QDRANT_URL=https://qdrant-production.up.railway.app
   QDRANT_HOST=qdrant-production.up.railway.app
   QDRANT_PORT=6333
   DB_PATH=/app/data/gita_verses.db
   PORT=8000
   ```

   **Important**: 
   - Replace `qdrant-production.up.railway.app` with your actual Qdrant service domain
   - Replace `sk-your-openai-api-key-here` with your actual OpenAI API key

6. Go to **"Deploy"** tab → Click **"Deploy"**
7. Wait for deployment (~5-7 minutes for first build)
8. **Copy the backend URL** (e.g., `backend-production.up.railway.app`)

### Step 4: Deploy Frontend Service

1. In your Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select your repository
3. Name it: `frontend`
4. Go to **"Settings"**:
   - **Root Directory**: `frontend`
   - **Dockerfile Path**: `frontend/Dockerfile`
5. Go to **"Variables"** tab and add:

   ```
   VITE_API_URL=https://backend-production.up.railway.app
   ```

   **Important**: Replace `backend-production.up.railway.app` with your actual backend service domain.

6. Go to **"Deploy"** tab → Click **"Deploy"**
7. Wait for deployment (~3-5 minutes for first build)
8. **Copy the frontend URL** (e.g., `frontend-production.up.railway.app`)

### Step 5: Ingest Data (First Time Setup)

After all services are deployed, you need to ingest the Bhagavad Gita data:

#### Option A: Using Railway CLI (Recommended)

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Connect to your project**:
   ```bash
   railway link
   ```

3. **Run ingestion script**:
   ```bash
   railway run --service backend python ingest_sqlite_to_qdrant.py
   ```

#### Option B: Using Railway Web Interface

1. Go to backend service → **"Deployments"** tab
2. Click on the latest deployment
3. Click **"View Logs"** or use **"Shell"** (if available)
4. Run: `python ingest_sqlite_to_qdrant.py`

#### Option C: Using Frontend UI

1. Visit your frontend URL
2. Navigate to **"Ingestion"** tab
3. Click **"Start Ingestion"**
4. Wait for completion (~2-3 minutes)

### Step 6: Verify Deployment

1. **Check Backend Health**:
   - Visit: `https://your-backend-url.railway.app/health`
   - Should return: `{"status": "healthy"}`

2. **Check Frontend**:
   - Visit: `https://your-frontend-url.railway.app`
   - Should show the research interface

3. **Test Research Query**:
   - Enter a test question (e.g., "How to deal with stress?")
   - Verify it returns results

## Environment Variables Summary

### Qdrant Service
```
QDRANT__SERVICE__HTTP_PORT=6333
QDRANT__SERVICE__GRPC_PORT=6334
```

### Backend Service
```
OPENAI_API_KEY=sk-...                    # Required
QDRANT_URL=https://qdrant-service-url    # Required (from Qdrant service)
QDRANT_HOST=qdrant-service-hostname       # Required (from Qdrant service)
QDRANT_PORT=6333                         # Optional (default: 6333)
DB_PATH=/app/data/gita_verses.db         # Optional
PORT=8000                                # Railway sets this automatically
```

### Frontend Service
```
VITE_API_URL=https://backend-service-url  # Required (from Backend service)
```

## Important Notes

1. **Root Directory for Backend**: Must be project root (empty), not `backend/`
   - This allows the Dockerfile to copy the EPUB file from `epubs/` directory

2. **Service URLs**: After deployment, update environment variables:
   - Frontend's `VITE_API_URL` should point to backend URL
   - Backend's `QDRANT_URL` should point to Qdrant URL

3. **Data Persistence**: Railway provides ephemeral storage. For production:
   - Consider using Railway's persistent volumes
   - Or migrate to managed databases (PostgreSQL for SQLite, Qdrant Cloud for vector DB)

4. **CORS**: Backend allows all origins. For production, restrict to your frontend domain.

## Troubleshooting

### Backend won't start
- Check logs in Railway dashboard
- Verify `OPENAI_API_KEY` is set correctly
- Verify `QDRANT_URL` points to correct Qdrant service
- Check that EPUB file exists (should be in `epubs/BhagavadGitaAsItIs.epub`)

### Frontend can't connect to backend
- Verify `VITE_API_URL` is set correctly (must be https://)
- Check backend CORS settings
- Verify backend is running and accessible

### Qdrant connection fails
- Verify Qdrant service is running
- Check `QDRANT_URL` format (should be `https://...` not `http://...`)
- Verify Qdrant service domain is correct

### No verses found in search
- Data may not be ingested
- Check Qdrant collection exists
- Run ingestion script manually

### EPUB file not found
- Ensure EPUB file is in `epubs/BhagavadGitaAsItIs.epub` in your repository
- Verify backend Root Directory is set to project root (not `backend/`)

## Next Steps

1. **Set up custom domains** (optional)
2. **Configure monitoring** (Railway provides basic metrics)
3. **Set up CI/CD** for automatic deployments
4. **Add persistent storage** for production data
5. **Configure backups** for SQLite database

## Support

For Railway-specific issues:
- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)

