# Oddsify Signals Viewer - Railway Deployment

## 🚀 Deploy to Railway

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub:**
```bash
cd /home/markusbot/oddsify-signals-viewer
git init
git add .
git commit -m "Initial commit - Oddsify Signals Viewer"
git remote add origin https://github.com/YOUR_USERNAME/oddsify-signals-viewer.git
git push -u origin main
```

2. **Deploy on Railway:**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select `oddsify-signals-viewer` repository
   - Railway auto-detects `railway.json` and `requirements.txt`
   - Click "Deploy"

3. **Get Your URL:**
   - Railway provides: `https://oddsify-signals-viewer-production.up.railway.app`
   - Share this URL with your team!

---

### Option 2: Deploy via Railway CLI

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login to Railway:**
```bash
railway login
```

3. **Initialize Project:**
```bash
cd /home/markusbot/oddsify-signals-viewer
railway init
```

4. **Deploy:**
```bash
railway up
```

5. **Open in Browser:**
```bash
railway open
```

---

## 📋 Configuration

### Environment Variables (Optional)
Railway auto-sets these, but you can override:

```bash
# In Railway Dashboard → Variables
PORT=8000
UPLOAD_DIR=/app/uploads
```

### Persistent Storage (Important!)

By default, Railway ephemeral filesystem resets on deploy. For persistent file storage:

1. **Add Persistent Disk:**
   - Railway Dashboard → Project → Storage
   - Click "New Disk"
   - Mount path: `/app/uploads`
   - Size: 1GB (free tier)

2. **Update railway.json:**
```json
{
  "build": "pip install -r requirements.txt",
  "start": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
  "watch": ["backend", "frontend", "requirements.txt"]
}
```

---

## 🔒 Security for Production

### Add Basic Auth (Optional)

Update `backend/main.py`:

```python
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/api/upload", dependencies=[Depends(verify_token)])
async def upload_file(...):
    ...
```

Set `API_KEY` in Railway Dashboard → Variables.

---

## 📊 Post-Deployment Checklist

- [ ] Deploy successful
- [ ] Upload test file works
- [ ] Signals display correctly
- [ ] Filters work
- [ ] Search works
- [ ] Add persistent disk (if needed)
- [ ] Set custom domain (optional)
- [ ] Add API key authentication (optional)

---

## 🌐 Custom Domain (Optional)

1. Railway Dashboard → Project → Settings
2. Click "Add Custom Domain"
3. Enter: `signals.oddsifylabs.com`
4. Update DNS with provided CNAME
5. SSL auto-provisioned by Railway

---

## 💰 Cost Estimate

**Railway Free Tier:**
- 500 hours/month runtime
- 1GB persistent storage
- Sufficient for small team use

**Paid Plan ($5/month):**
- Unlimited runtime
- More storage
- Priority support

---

## 📱 Share with Team

Once deployed, share the Railway URL:
```
https://oddsify-signals-viewer-production.up.railway.app
```

Team members can:
- Upload signals files
- View grouped signals
- Filter and search
- No login required (add auth if needed)

---

## 🔄 Auto-Deploy

With GitHub deployment:
- Every push to `main` triggers auto-deploy
- Changes live in ~2 minutes
- Railway shows deploy logs in dashboard

---

**Need help?** Check Railway docs: https://docs.railway.app
