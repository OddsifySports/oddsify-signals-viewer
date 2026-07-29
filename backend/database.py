"""
Database module for Oddsify Signals Viewer
SQLite-based storage for signals history and user management
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Optional

DB_PATH = Path(os.getenv("DB_PATH", "/app/data/signals.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Signal history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetch_id INTEGER NOT NULL,
            sport TEXT NOT NULL,
            model TEXT NOT NULL,
            market TEXT NOT NULL,
            player TEXT NOT NULL,
            team TEXT NOT NULL,
            side TEXT NOT NULL,
            line TEXT,
            price TEXT NOT NULL,
            model_pct REAL NOT NULL,
            mkt_pct REAL NOT NULL,
            edge REAL NOT NULL,
            ev REAL NOT NULL,
            fair TEXT,
            book TEXT NOT NULL,
            bucket TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_id TEXT
        )
    """)
    
    # Email subscriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            sport TEXT,
            market TEXT,
            min_edge REAL DEFAULT 10.0,
            bucket TEXT DEFAULT 'STRONG',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_fetch ON signal_history(fetch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_sport ON signal_history(sport)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_market ON signal_history(market)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_edge ON signal_history(edge)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_uploaded ON signal_history(uploaded_at)")
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def save_signals(signals: List[Dict], file_id: str, metadata: Dict):
    """Save signals to history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    for signal in signals:
        cursor.execute("""
            INSERT INTO signal_history (
                fetch_id, sport, model, market, player, team, side,
                line, price, model_pct, mkt_pct, edge, ev, fair, book,
                bucket, file_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.get('fetch_id', 0),
            metadata.get('sport', 'UNKNOWN'),
            metadata.get('model', 'UNKNOWN'),
            signal['market'],
            signal['player'],
            signal['team'],
            signal['side'],
            signal.get('line'),
            signal['price'],
            signal['model_pct'],
            signal['mkt_pct'],
            signal['edge'],
            signal['ev'],
            signal['fair'],
            signal['book'],
            signal['bucket'],
            file_id
        ))
    
    conn.commit()
    conn.close()
    return len(signals)

def get_signal_history(
    sport: Optional[str] = None,
    market: Optional[str] = None,
    min_edge: Optional[float] = None,
    days: int = 7
) -> List[Dict]:
    """Get signal history with filters"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM signal_history
        WHERE uploaded_at >= datetime('now', ?)
    """
    params = [f'-{days} days']
    
    if sport:
        query += " AND sport = ?"
        params.append(sport)
    
    if market:
        query += " AND market = ?"
        params.append(market)
    
    if min_edge is not None:
        query += " AND edge >= ?"
        params.append(min_edge)
    
    query += " ORDER BY uploaded_at DESC, edge DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_history_stats(days: int = 7) -> Dict:
    """Get statistics for signal history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_signals,
            COUNT(DISTINCT fetch_id) as total_uploads,
            AVG(edge) as avg_edge,
            MAX(edge) as max_edge,
            COUNT(CASE WHEN bucket = 'STRONG' THEN 1 END) as strong_count
        FROM signal_history
        WHERE uploaded_at >= datetime('now', ?)
    """, (f'-{days} days',))
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        'total_signals': row['total_signals'],
        'total_uploads': row['total_uploads'],
        'avg_edge': row['avg_edge'] or 0,
        'max_edge': row['max_edge'] or 0,
        'strong_count': row['strong_count'] or 0
    }

def add_email_subscription(email: str, sport: Optional[str] = None, market: Optional[str] = None, min_edge: float = 10.0, bucket: str = 'STRONG'):
    """Add email subscription"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO email_subscriptions (email, sport, market, min_edge, bucket)
        VALUES (?, ?, ?, ?, ?)
    """, (email, sport, market, min_edge, bucket))
    
    conn.commit()
    conn.close()

def get_active_subscriptions() -> List[Dict]:
    """Get all active email subscriptions"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM email_subscriptions WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def create_user(username: str, email: str, password_hash: str, membership: str, role: str = "viewer") -> int:
    """
    Create new user account
    
    Args:
        username: User's username
        email: User's email
        password_hash: Hashed password
        membership: Membership type (TERMINAL, ONLINE, INSIDER)
        role: User role (admin or viewer)
    
    Returns:
        User ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (username, password_hash, email, is_active)
        VALUES (?, ?, ?, 1)
    """, (username, password_hash, email))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def update_user_membership(username: str, membership: str) -> bool:
    """Update user's membership type"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET membership = ? WHERE username = ?
    """, (membership, username))
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0

def get_all_users() -> List[Dict]:
    """Get all users (for admin)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, membership, role, created_at, is_active FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def deactivate_user(username: str) -> bool:
    """Deactivate user account"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0

# Initialize DB on import
init_db()
