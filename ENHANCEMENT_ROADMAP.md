# 🚀 Oddsify Signals Viewer - Enhancement Roadmap

## ✅ COMPLETED (Phase 1 - Core Features)
- [x] File upload (drag & drop)
- [x] Markdown parsing
- [x] Grouping by market/league
- [x] Filtering & search
- [x] Stats dashboard
- [x] Railway deployment
- [x] Persistent storage

---

## 🎯 PHASE 2: Quick Wins (1-2 days)

### 1. CSV Export ✅ IN PROGRESS
**Status:** Ready to implement  
**Priority:** HIGH  
**Effort:** 2 hours

**Features:**
- Export filtered signals to CSV
- Download button in UI
- Include all columns (player, team, edge, EV, book, etc.)

**Implementation:**
```python
# Backend: /api/signals/export?file_id=xxx&format=csv
# Frontend: "Export CSV" button next to filters
```

---

### 2. Historical Tracking Database ✅ IN PROGRESS
**Status:** Database schema created  
**Priority:** HIGH  
**Effort:** 4 hours

**Features:**
- SQLite database for signal history
- Track signals across uploads
- Query by date range, sport, market
- Compare edges over time

**Schema:**
- `signal_history` - All uploaded signals
- `users` - User accounts (for Phase 3)
- `email_subscriptions` - Alert preferences

**Implementation:**
```python
# backend/database.py - Created ✅
# Add to main.py: Save signals on upload
```

---

### 3. History Comparison UI
**Status:** Pending  
**Priority:** MEDIUM  
**Effort:** 6 hours

**Features:**
- Timeline view of signal edges
- Compare same market across dates
- Graph: Edge distribution over time
- Filter by date range

**UI Components:**
- New "History" tab
- Chart.js for visualizations
- Date range picker

---

## 🎯 PHASE 3: Advanced Features (3-5 days)

### 4. Email Alerts for STRONG Signals
**Status:** Pending  
**Priority:** MEDIUM  
**Effort:** 8 hours

**Features:**
- Subscribe to alerts (email + preferences)
- Send when STRONG signals uploaded
- Configurable thresholds (min edge, sport, market)
- Daily/weekly digest option

**Implementation:**
```python
# backend/email_service.py
# Use aiosmtplib for async email
# Railway environment variables: SMTP_HOST, SMTP_USER, SMTP_PASS
```

**UI:**
- "Subscribe to Alerts" modal
- Preference form (sport, market, min edge)
- Unsubscribe link in emails

---

### 5. User Authentication
**Status:** Pending  
**Priority:** HIGH (for multi-user)  
**Effort:** 12 hours

**Features:**
- User registration/login
- JWT-based authentication
- Protected routes
- User-specific preferences
- Upload history per user

**Implementation:**
```python
# backend/auth.py
# python-jose for JWT
# passlib for password hashing
# /api/auth/register, /api/auth/login
```

**UI:**
- Login/Register modals
- User profile page
- "My Uploads" section
- Logout button

---

### 6. Custom Domain
**Status:** Pending  
**Priority:** LOW (cosmetic)  
**Effort:** 1 hour (configuration only)

**Steps:**
1. Railway Dashboard → Settings → Domains
2. Add domain: `signals.oddsifylabs.com`
3. Update DNS with CNAME record
4. SSL auto-provisioned by Railway

**No code changes needed!**

---

## 📊 IMPLEMENTATION ORDER

**Recommended Sequence:**

1. **CSV Export** (2h) - Quick win, high value
2. **Historical DB Integration** (4h) - Foundation for analytics
3. **History Comparison UI** (6h) - Visual insights
4. **User Authentication** (12h) - Required for multi-user
5. **Email Alerts** (8h) - Depends on auth
6. **Custom Domain** (1h) - Do last, just config

**Total Effort:** ~33 hours (4-5 work days)

---

## 🔧 TECHNICAL REQUIREMENTS

### Dependencies (Added to requirements.txt)
```txt
python-jose[cryptography]==3.3.0     # JWT auth
passlib[bcrypt]==1.7.4               # Password hashing
python-dotenv==1.0.0                 # Environment variables
aiosmtplib==3.0.1                    # Async email
email-validator==2.1.0               # Email validation
```

### Environment Variables (Railway)
```bash
# Database
DB_PATH=/app/data/signals.db

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=noreply@oddsifylabs.com

# Auth
JWT_SECRET=your-secret-key-here
JWT_EXPIRE_HOURS=24

# Domain (optional)
CUSTOM_DOMAIN=signals.oddsifylabs.com
```

---

## 📈 METRICS & ANALYTICS

Once historical tracking is live:
- **Total signals uploaded** (all time)
- **Average edge by sport**
- **Best performing markets**
- **STRONG signal frequency**
- **User engagement** (if auth enabled)

---

## 🎯 SUCCESS CRITERIA

**Phase 2 Complete When:**
- ✅ CSV export works for all filtered views
- ✅ All uploads saved to database
- ✅ History page shows timeline
- ✅ Can compare edges across dates

**Phase 3 Complete When:**
- ✅ Users can register/login
- ✅ Email alerts sent for STRONG signals
- ✅ Custom domain configured
- ✅ Full user dashboard with preferences

---

## 💡 FUTURE ENHANCEMENTS (Post-Phase 3)

- [ ] WebSocket for real-time updates
- [ ] PostgreSQL migration (scale beyond SQLite)
- [ ] API rate limiting
- [ ] Advanced analytics (ROI tracking, sharp vs square books)
- [ ] Mobile app (React Native)
- [ ] Webhook integrations (Discord, Slack, Telegram)
- [ ] Machine learning insights (edge prediction)

---

**Ready to start implementation! Which phase should we tackle first?**
