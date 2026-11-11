"""Separate, local audit trail for dashboard calculations (no broker orders)."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'logs' / 'dashboard.sqlite3'


def save_run(mode, capital, targets, current, drift, trades, db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS dashboard_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL,
            mode TEXT NOT NULL, capital REAL NOT NULL, targets TEXT NOT NULL,
            current_weights TEXT NOT NULL, drift TEXT NOT NULL,
            trades TEXT NOT NULL)''')
        db.execute('''INSERT INTO dashboard_runs
            (ts,mode,capital,targets,current_weights,drift,trades)
            VALUES (?,?,?,?,?,?,?)''', (
                datetime.now(timezone.utc).isoformat(), mode, capital,
                json.dumps(targets), json.dumps(current), json.dumps(drift),
                json.dumps(trades)))


def get_runs(limit=50, db_path=DB_PATH):
    if not Path(db_path).exists():
        return []
    with sqlite3.connect(db_path) as db:
        return db.execute('''SELECT id,ts,mode,capital,targets,current_weights,drift,trades
            FROM dashboard_runs ORDER BY id DESC LIMIT ?''', (int(limit),)).fetchall()
