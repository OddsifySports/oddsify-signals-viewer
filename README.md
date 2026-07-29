# Oddsify Signals Viewer

Web application for uploading, viewing, and analyzing sports betting signals from markdown files.

## Features

✅ **Upload & Parse** - Drag & drop markdown signals files  
✅ **Group by Market & League** - Automatically organizes signals  
✅ **Filter & Search** - Filter by sport, market, bucket, or search text  
✅ **Stats Dashboard** - Total signals, average/max edge, STRONG count  
✅ **Real-time Filtering** - Instant results as you type  

## Quick Start

### 1. Install Dependencies

```bash
cd /home/markusbot/oddsify-signals-viewer
pip install fastapi uvicorn python-multipart
```

### 2. Start Server

```bash
cd backend
python3 main.py
```

Server runs at: **http://localhost:8000**

### 3. Upload Signals

1. Open http://localhost:8000 in your browser
2. Drag & drop your `.md` signals file
3. View grouped signals with filters

## API Endpoints

### Upload File
```bash
POST /api/upload
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "file_id": "20260729_090650_oddsify-signals",
  "n_signals": 59,
  "sport": "MLB"
}
```

### List Files
```bash
GET /api/files

Response:
{
  "files": [
    {
      "id": "20260729_090650_oddsify-signals",
      "filename": "oddsify-signals-20260729-090650.md",
      "n_signals": 59,
      "sport": "MLB"
    }
  ]
}
```

### Get Grouped Signals
```bash
GET /api/signals/grouped?file_id={file_id}

Response:
{
  "groups": [
    {
      "market": "game_run_totals",
      "league": "MLB",
      "count": 15,
      "avg_edge": 14.2,
      "max_edge": 16.9,
      "signals": [...]
    }
  ]
}
```

### Delete File
```bash
DELETE /api/files/{file_id}
```

## File Format

Supports markdown files with this structure:

```markdown
# Oddsify signals

**sport**: MLB
**n_signals**: 59
**model**: mlb_batter_hits_v1_1p5
**fetch_id**: 63
**generated**: 2026-07-29T09:06:52

| Bucket | Market | Player | Team | Side | Line | Price | Model% | Mkt% | Edge | EV/¢ | Fair | Book |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| STRONG | game_run_totals | (Boston Red Sox) | Boston Red Sox | under | 10.5 | -108 | 0.689 | 0.519 | +16.9pp | +32.6 | −221 | fanduel |
```

## Project Structure

```
oddsify-signals-viewer/
├── backend/
│   └── main.py          # FastAPI server + parser
├── frontend/
│   └── index.html       # Single-page app
├── uploads/             # Uploaded files storage
├── test_parser.py       # Parser test script
└── README.md            # This file
```

## Testing

```bash
# Test parser with sample file
python3 test_parser.py

# Expected output:
# ✅ ALL 59 SIGNALS PARSED CORRECTLY
```

## Features Detail

### Grouping
Signals are automatically grouped by:
- **Market** (e.g., `game_run_totals`, `batter_hits`, `game_moneyline`)
- **League/Sport** (e.g., `MLB`, `NBA`)

### Filtering
- **Sport**: Filter by league (MLB, NBA, etc.)
- **Market**: Filter by bet type
- **Bucket**: STRONG / MEDIUM / SMALL
- **Search**: Player name, team, or sportsbook

### Statistics
- **Total Signals**: Count of all signals
- **Average Edge**: Mean edge across all signals
- **Max Edge**: Highest edge signal
- **STRONG Count**: Number of STRONG bucket signals

## Production Deployment

### With Uvicorn (Production ASGI Server)
```bash
pip install uvicorn[standard]
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Gunicorn + Uvicorn Workers
```bash
pip install gunicorn uvicorn[standard]
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables
```bash
export UPLOAD_DIR="/path/to/uploads"
export PORT=8000
```

## Security Notes

- Files are stored in `/uploads` directory
- Only `.md` files are accepted
- No authentication (add if needed for production)
- CORS enabled for all origins (restrict in production)

## Future Enhancements

- [ ] User authentication
- [ ] Multiple file comparison
- [ ] Historical tracking
- [ ] Export to CSV/Excel
- [ ] Email alerts for STRONG signals
- [ ] API key authentication
- [ ] Rate limiting

---

**Built by:** Ruth, Oddsify Labs  
**Date:** July 29, 2026  
**Version:** 1.0.0
