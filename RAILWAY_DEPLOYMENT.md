# Railway Deployment Guide - Oddsify Signals Viewer

## 🚀 Deployment Status

**Repository:** https://github.com/OddsifySports/oddsify-signals-viewer  
**Build Triggered:** 2026-07-29T18:14:25Z  
**Builder:** Metal (builder-fstdwd)

---

## 📊 Monitor Deployment

### Railway Dashboard
1. Go to https://railway.app/dashboard
2. Find your project: `oddsify-signals-viewer`
3. Click "Deployments" tab
4. Watch the build logs in real-time

### Expected Build Steps
```
✅ Cloning repository
✅ Installing dependencies (pip install -r requirements.txt)
✅ Building application
✅ Starting server (uvicorn main:app)
✅ Health check
🟢 Deployment complete!
```

**Build Time:** ~2-3 minutes

---

## 🎯 Post-Deployment Checklist

### 1. Verify App is Running
```bash
# Replace with your Railway URL
curl https://oddsify-signals-viewer-production.up.railway.app/api/files
```

Expected response:
```json
{"files": []}
```

### 2. Test File Upload
- Open your Railway URL in browser
- Upload the sample signals file
- Verify signals display correctly

### 3. Add Persistent Storage (CRITICAL)
**Without this, uploaded files will be lost on redeploy!**

In Railway Dashboard:
1. Go to your project → "Storage" tab
2. Click "New Disk"
3. Configuration:
   - **Mount Path:** `/app/uploads`
   - **Size:** 1GB (sufficient for thousands of files)
4. Click "Create"

### 4. Set Environment Variables (Optional)
In Railway Dashboard → "Variables":
```
PORT=8000
UPLOAD_DIR=/app/uploads
```

---

## 🔧 Troubleshooting

### Build Fails
**Check logs for:**
- Missing dependencies → Update `requirements.txt`
- Python syntax errors → Check `backend/main.py`
- Port binding issues → Ensure `$PORT` is used

### App Won't Start
**Common issues:**
- Wrong working directory → `railway.json` has `cd backend`
- Port not configured → Use `$PORT` environment variable
- Missing static files → Verify `frontend/index.html` exists

### Files Disappear After Redeploy
**Solution:** Add persistent storage (see above)

### API Returns 404
**Check:**
- Routes are defined in `backend/main.py`
- CORS is enabled
- Frontend is calling correct API base URL

---

## 🌐 Custom Domain (Optional)

1. Railway Dashboard → Project → Settings
2. Click "Add Custom Domain"
3. Enter: `signals.oddsifylabs.com` (or your domain)
4. Update DNS records:
   ```
   Type: CNAME
   Name: signals
   Value: production.up.railway.app
   ```
5. SSL auto-provisioned by Let's Encrypt (~5 minutes)

---

## 💰 Cost Estimate

**Railway Free Tier:**
- 500 execution hours/month
- 1GB storage (with persistent disk)
- Sufficient for: ~10-20 users, moderate usage

**Paid Plan ($5/month):**
- Unlimited execution hours
- Additional storage
- Priority support

---

## 📈 Scaling Options

### If Traffic Increases:
1. **Upgrade Railway plan** → More resources
2. **Add CDN** → Cloudflare in front of Railway
3. **Database** → Migrate from file storage to PostgreSQL
4. **Caching** → Redis for frequently accessed signals

---

## 🔐 Security Recommendations

### For Production:
1. **Add API Key Authentication**
   ```python
   # backend/main.py
   API_KEY = os.getenv("API_KEY")
   
   async def verify_auth(x_api_key: str = Header(None)):
       if x_api_key != API_KEY:
           raise HTTPException(status_code=401)
   ```

2. **Set API_KEY in Railway Variables**

3. **Enable Rate Limiting**
   ```python
   from slowapi import SlowAPI
   limiter = SlowAPI()
   app.state.limiter = limiter
   ```

4. **HTTPS Only** → Railway handles this automatically

---

## 📱 Share with Team

**Deployment URL:** (will be shown in Railway Dashboard)
```
https://oddsify-signals-viewer-production.up.railway.app
```

**Usage Instructions for Team:**
1. Open URL in browser
2. Drag & drop signals `.md` file
3. View grouped signals
4. Filter by sport/market/bucket
5. Search for players, teams, or books

---

## 🔄 Auto-Deploy

With GitHub integration:
- Every push to `main` triggers auto-deploy
- Build starts within 30 seconds
- Downtime: ~30-60 seconds during deploy
- Rollback: Click previous deployment in dashboard

---

## 📞 Support

**Railway Docs:** https://docs.railway.app  
**Railway Discord:** https://discord.gg/railway  
**Status Page:** https://status.railway.app

---

**Last Updated:** 2026-07-29  
**Version:** 1.0.0
