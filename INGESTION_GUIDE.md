# Data Ingestion Guide

## Problem: SQLite is Empty

If you see "Total verses in SQLite: 0", you need to first ingest the EPUB file to populate the database.

## Solution: Use the API Endpoint (Easiest)

The easiest way is to use the ingestion API endpoint which handles everything:

### Step 1: Make sure backend is running on Railway

### Step 2: Call the ingestion endpoint

```bash
# Using curl
curl -X POST https://your-backend-url.railway.app/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"epub_path": null}'

# Or use the frontend UI
# 1. Go to https://your-frontend-url.railway.app
# 2. Navigate to "Ingestion" tab
# 3. Click "Start Ingestion"
```

This will:
1. Read the EPUB file
2. Populate SQLite database
3. Create embeddings
4. Add to Qdrant vector store

## Alternative: Two-Step Process

If you need to use `ingest_sqlite_to_qdrant.py`:

### Step 1: First populate SQLite (if empty)

You need to run the EPUB ingestion first. The `ingest_sqlite_to_qdrant.py` script only moves data FROM SQLite TO Qdrant - it doesn't read the EPUB.

### Step 2: Then run the SQLite to Qdrant script

```bash
railway run --service backend python ingest_sqlite_to_qdrant.py
```

## Troubleshooting Connection Issues

If you get `getaddrinfo failed` error:

### Check 1: Are you running on Railway?

Make sure `railway run` is actually executing on Railway, not locally. Check:
```bash
railway status
```

### Check 2: Environment Variables on Railway

Verify these are set in Railway backend service:
- `QDRANT_URL` - Full URL like `https://qdrant-production.up.railway.app`
- `QDRANT_HOST` - Hostname like `qdrant-production.up.railway.app`
- `OPENAI_API_KEY` - Your OpenAI key

### Check 3: Qdrant Service is Running

Make sure your Qdrant service is deployed and running on Railway.

## Recommended Workflow

1. **Deploy all services** (Qdrant, Backend, Frontend)
2. **Use the API endpoint** to ingest:
   - Via frontend UI (easiest)
   - Or via curl/Postman
3. **Verify** by testing a search query

The API endpoint (`/api/ingest`) is the recommended method as it handles the complete workflow automatically.

