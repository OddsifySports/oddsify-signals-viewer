"""
Oddsify Signals Viewer - Backend API
FastAPI server for uploading and parsing sports betting signals from markdown files
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import re
import json
from pathlib import Path
from datetime import datetime
import os

app = FastAPI(title="Oddsify Signals Viewer")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Models
class Signal(BaseModel):
    bucket: str
    market: str
    player: str
    team: str
    side: str
    line: Optional[str]
    price: str
    model_pct: float
    mkt_pct: float
    edge: float
    ev: float
    fair: str
    book: str
    sport: Optional[str] = None
    fetch_id: Optional[int] = None

class SignalFile(BaseModel):
    id: str
    filename: str
    sport: str
    n_signals: int
    model: str
    fetch_id: int
    generated: str
    signals: List[Signal]

class GroupedSignals(BaseModel):
    market: str
    league: str
    signals: List[Signal]
    count: int
    avg_edge: float
    max_edge: float

# Parser
def parse_markdown_signals(content: str) -> dict:
    """Parse markdown signals file and extract metadata + signals table"""
    
    # Extract metadata from front matter
    metadata = {}
    meta_match = re.search(r'\*\*sport\*\*:\s*(\w+)', content)
    if meta_match:
        metadata['sport'] = meta_match.group(1)
    
    n_signals_match = re.search(r'\*\*n_signals\*\*:\s*(\d+)', content)
    if n_signals_match:
        metadata['n_signals'] = int(n_signals_match.group(1))
    
    model_match = re.search(r'\*\*model\*\*:\s*(\S+)', content)
    if model_match:
        metadata['model'] = model_match.group(1)
    
    fetch_id_match = re.search(r'\*\*fetch_id\*\*:\s*(\d+)', content)
    if fetch_id_match:
        metadata['fetch_id'] = int(fetch_id_match.group(1))
    
    generated_match = re.search(r'\*\*generated\*\*:\s*([\d\-T:]+)', content)
    if generated_match:
        metadata['generated'] = generated_match.group(1)
    
    # Extract table
    table_match = re.search(r'\| Bucket \|.*?\n((?:\|.*?\n)+)', content, re.DOTALL)
    if not table_match:
        raise ValueError("No signals table found in markdown")
    
    table_content = table_match.group(1)
    lines = table_content.strip().split('\n')
    
    signals = []
    for line in lines:
        # Skip separator line
        if '|---' in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 14:
            continue
        
        # Parse row
        try:
            bucket = parts[1]
            market = parts[2]
            player = parts[3]
            team = parts[4]
            side = parts[5]
            line = parts[6] if parts[6] != '—' else None
            price = parts[7]
            
            # Parse percentages
            model_pct_str = parts[8].replace('pp', '').replace('+', '')
            mkt_pct_str = parts[9].replace('pp', '').replace('+', '')
            edge_str = parts[10].replace('pp', '').replace('+', '')
            ev_str = parts[11].replace('¢', '').replace('+', '')
            
            model_pct = float(model_pct_str) / 100
            mkt_pct = float(mkt_pct_str) / 100
            edge = float(edge_str)
            ev = float(ev_str)
            
            fair = parts[12]
            book = parts[13]
            
            signal = Signal(
                bucket=bucket,
                market=market,
                player=player,
                team=team,
                side=side,
                line=line,
                price=price,
                model_pct=model_pct,
                mkt_pct=mkt_pct,
                edge=edge,
                ev=ev,
                fair=fair,
                book=book,
                sport=metadata.get('sport'),
                fetch_id=metadata.get('fetch_id')
            )
            signals.append(signal)
        except (ValueError, IndexError) as e:
            # Skip malformed rows
            continue
    
    return {
        'metadata': metadata,
        'signals': signals
    }

# API Endpoints
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a markdown signals file"""
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only .md files are supported")
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse the file
        parsed = parse_markdown_signals(content_str)
        
        if not parsed['signals']:
            raise HTTPException(status_code=400, detail="No signals found in file")
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        file_path.write_text(content_str)
        
        # Create response
        file_id = file_path.stem
        result = SignalFile(
            id=file_id,
            filename=file.filename,
            sport=parsed['metadata'].get('sport', 'UNKNOWN'),
            n_signals=len(parsed['signals']),
            model=parsed['metadata'].get('model', 'UNKNOWN'),
            fetch_id=parsed['metadata'].get('fetch_id', 0),
            generated=parsed['metadata'].get('generated', ''),
            signals=parsed['signals']
        )
        
        return {
            'success': True,
            'file_id': file_id,
            'filename': file.filename,
            'sport': result.sport,
            'n_signals': result.n_signals,
            'model': result.model,
            'fetch_id': result.fetch_id,
            'generated': result.generated,
            'signals': [s.dict() for s in result.signals]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/files")
async def list_files():
    """List all uploaded files"""
    files = []
    for f in UPLOAD_DIR.glob("*.md"):
        try:
            content = f.read_text()
            parsed = parse_markdown_signals(content)
            files.append({
                'id': f.stem,
                'filename': f.name,
                'sport': parsed['metadata'].get('sport', 'UNKNOWN'),
                'n_signals': len(parsed['signals']),
                'generated': parsed['metadata'].get('generated', ''),
            })
        except:
            continue
    
    # Sort by generated date (newest first)
    files.sort(key=lambda x: x.get('generated', ''), reverse=True)
    return {'files': files}

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Get signals from a specific file"""
    file_path = UPLOAD_DIR / f"{file_id}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    content = file_path.read_text()
    parsed = parse_markdown_signals(content)
    
    return {
        'file_id': file_id,
        'metadata': parsed['metadata'],
        'signals': [s.dict() for s in parsed['signals']]
    }

@app.get("/api/signals/grouped")
async def get_grouped_signals(file_id: Optional[str] = None):
    """Get signals grouped by market and league"""
    
    # Get all signals (from one file or all files)
    all_signals = []
    
    if file_id:
        file_path = UPLOAD_DIR / f"{file_id}.md"
        if file_path.exists():
            content = file_path.read_text()
            parsed = parse_markdown_signals(content)
            all_signals = parsed['signals']
    else:
        # Load from all files
        for f in UPLOAD_DIR.glob("*.md"):
            try:
                content = f.read_text()
                parsed = parse_markdown_signals(content)
                all_signals.extend(parsed['signals'])
            except:
                continue
    
    # Group by market and sport (league)
    grouped = {}
    for signal in all_signals:
        key = f"{signal.market}__{signal.sport or 'UNKNOWN'}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(signal)
    
    # Calculate stats and format
    result = []
    for key, signals in grouped.items():
        market, league = key.split('__')
        edges = [s.edge for s in signals]
        
        result.append({
            'market': market,
            'league': league,
            'signals': [s.dict() for s in signals],
            'count': len(signals),
            'avg_edge': sum(edges) / len(edges) if edges else 0,
            'max_edge': max(edges) if edges else 0,
        })
    
    # Sort by count (descending)
    result.sort(key=lambda x: x['count'], reverse=True)
    
    return {'groups': result}

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    file_path = UPLOAD_DIR / f"{file_id}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path.unlink()
    return {'success': True, 'message': f"Deleted {file_id}.md"}

# Serve frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
