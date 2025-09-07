from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

DB_PATH = os.environ.get("OIC_DB", "oic_runs.sqlite3")

DDL = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    input TEXT,
    output TEXT,
    meta TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


@dataclass
class RunRecord:
    id: str
    kind: str
    input: str
    output: str
    meta: dict


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    return conn


def save_run(record: RunRecord) -> None:
    conn = _connect()
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO runs (id, kind, input, output, meta) VALUES (?, ?, ?, ?, ?)",
            (
                record.id,
                record.kind,
                record.input,
                record.output,
                json.dumps(record.meta, ensure_ascii=False),
            ),
        )
    conn.close()


def load_run(run_id: str) -> Optional[RunRecord]:
    conn = _connect()
    cur = conn.execute("SELECT id, kind, input, output, meta FROM runs WHERE id = ?", (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return RunRecord(id=row[0], kind=row[1], input=row[2], output=row[3], meta=json.loads(row[4]))


def list_runs(kind: Optional[str] = None, limit: int = 10) -> List[RunRecord]:
    conn = _connect()
    if kind:
        cur = conn.execute(
            "SELECT id, kind, input, output, meta FROM runs WHERE kind = ? ORDER BY created_at DESC LIMIT ?",
            (kind, limit),
        )
    else:
        cur = conn.execute("SELECT id, kind, input, output, meta FROM runs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [RunRecord(id=r[0], kind=r[1], input=r[2], output=r[3], meta=json.loads(r[4])) for r in rows]


