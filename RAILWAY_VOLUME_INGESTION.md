# Railway Volume & Data Ingestion Guide

## 📦 Step 1: Create Persistent Volume in Railway

Railway provides **ephemeral storage by default** (data is lost on redeploy). For production, you need a **persistent volume**.

### Create Volume:

1. **Go to your Railway project**
2. **Select Backend service**
3. **Go to "Volumes" tab** (or "Data" tab in some Railway versions)
4. **Click "Create Volume"** or **"+ New Volume"**
5. **Configure:**
   - **Name**: `gita-data` (or any name)
   - **Mount Path**: `/app/data`
   - **Size**: Start with 1GB (you can increase later)
6. **Click "Create"**

The volume will be mounted at `/app/data` in your backend container.

## 🔧 Step 2: Configure Database Path

Make sure `DB_PATH` environment variable is set in Railway backend service:

1. **Go to Backend service → Variables tab**
2. **Add/Update:**
   ```
   DB_PATH=/app/data/gita_verses.db
   ```
3. **Save**

This ensures SQLite database is stored in the persistent volume.

## 📚 Step 3: Ingest Verses (Two Methods)

### Method A: Using API Endpoint (Recommended - Easiest) ✅

This method does **everything in one step**:
- Reads EPUB file
- Populates SQLite database (`/app/data/gita_verses.db`)
- Creates embeddings
- Adds to Qdrant vector store

#### Option 1: Via Frontend UI

1. **Go to your frontend URL**: `https://your-frontend.railway.app`
2. **Navigate to "Ingestion" tab**
3. **Click "Start Ingestion"**
4. **Wait 2-3 minutes** for completion
5. **Check status** - should show "Successfully ingested X verses"

#### Option 2: Via API Call

```bash
# Using curl
curl -X POST https://your-backend-url.railway.app/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"epub_path": null}'

# Or using Railway CLI
railway run --service backend curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"epub_path": null}'
```

### Method B: Two-Step Process (If SQLite Already Exists)

If you already have data in SQLite and just need to sync to Qdrant:

#### Step 1: Verify SQLite has data

```bash
railway run --service backend python -c "
from models import get_db_session, Verse
session = get_db_session()
count = session.query(Verse).count()
print(f'Verses in SQLite: {count}')
session.close()
"
```

#### Step 2: Ingest SQLite → Qdrant

```bash
railway run --service backend python ingest_sqlite_to_qdrant.py
```

## ✅ Step 4: Verify Ingestion

### Check SQLite Database:

```bash
railway run --service backend python -c "
from models import get_db_session, Verse
session = get_db_session()
count = session.query(Verse).count()
print(f'✅ SQLite has {count} verses')
session.close()
"
```

### Check Qdrant:

```bash
railway run --service backend python -c "
from vector_store import VectorStore
vs = VectorStore()
info = vs.client.get_collection(vs.collection_name)
print(f'✅ Qdrant has {info.points_count} points')
"
```

### Test Search:

Visit your frontend and try a search query like "What does the Gita say about duty?"

## 🔍 Troubleshooting

### Issue: Volume not persisting data

**Solution:**
- Make sure volume is created and mounted at `/app/data`
- Verify `DB_PATH=/app/data/gita_verses.db` is set
- Check volume is attached to backend service

### Issue: "Total verses in SQLite: 0"

**Solution:**
- You need to run EPUB ingestion first (Method A above)
- The `ingest_sqlite_to_qdrant.py` script only moves data FROM SQLite TO Qdrant
- It doesn't read the EPUB file

### Issue: Can't find EPUB file

**Solution:**
- EPUB should be in Docker image (copied during build)
- Check Dockerfile includes: `COPY epubs/BhagavadGitaAsItIs.epub /app/epubs/`
- Verify EPUB exists in repository at `epubs/BhagavadGitaAsItIs.epub`

### Issue: Volume size limits

**Solution:**
- Railway free tier: Limited storage
- Upgrade plan for more storage
- Or use external database (PostgreSQL) instead of SQLite

## 📊 Data Flow

```
EPUB File (in Docker image)
    ↓
/api/ingest endpoint
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
SQLite DB         Qdrant Vector DB
/app/data/        (Remote service)
gita_verses.db
(Persistent)      (Persistent)
```

## 💡 Best Practices

1. **Always use persistent volumes** for production data
2. **Use Method A (API endpoint)** - it's simpler and handles everything
3. **Monitor volume usage** - Railway shows volume size in dashboard
4. **Backup regularly** - Export SQLite database periodically
5. **Set DB_PATH explicitly** - Don't rely on defaults

## 🎯 Quick Checklist

- [ ] Volume created at `/app/data`
- [ ] `DB_PATH=/app/data/gita_verses.db` set in Railway
- [ ] Backend service has volume mounted
- [ ] EPUB file exists in Docker image
- [ ] Called `/api/ingest` endpoint (or used frontend UI)
- [ ] Verified verses in SQLite
- [ ] Verified points in Qdrant
- [ ] Tested search functionality

---

**Note:** Railway volumes persist across deployments, so you only need to ingest data once (unless you reset the volume).

