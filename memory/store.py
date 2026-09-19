"""SQLite-backed patient-scoped personal memory store."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class MemoryStore:
    def __init__(self, database_path: str | Path = ":memory:") -> None:
        self.database_path = str(database_path)
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL, title TEXT NOT NULL,
                people TEXT NOT NULL, relationships TEXT NOT NULL, place TEXT, time TEXT,
                activity TEXT, objects TEXT NOT NULL, emotion TEXT, story TEXT NOT NULL,
                source TEXT NOT NULL, confidence REAL NOT NULL, sensitive INTEGER NOT NULL,
                language TEXT NOT NULL, sequence INTEGER, tags TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS memory_chunks (
                chunk_id TEXT PRIMARY KEY, memory_id TEXT NOT NULL, patient_id TEXT NOT NULL,
                section TEXT NOT NULL, text TEXT NOT NULL, language TEXT NOT NULL, sequence INTEGER NOT NULL
            )"""
        )
        self._connection.commit()

    def save_memory(self, memory: dict[str, Any]) -> dict[str, Any]:
        required = {"patient_id", "title", "story", "source", "confidence", "sensitive", "language"}
        missing = required - memory.keys()
        if missing:
            raise ValueError(f"Missing memory fields: {sorted(missing)}")
        now = datetime.now(timezone.utc).isoformat()
        memory_id = memory.get("memory_id") or f"mem_{uuid4().hex}"
        record = {"memory_id": memory_id, "people": [], "relationships": [], "place": None, "time": None, "activity": None, "objects": [], "emotion": None, "sequence": None, "tags": [], **memory}
        self._connection.execute(
            """INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (record["memory_id"], record["patient_id"], record["title"], json.dumps(record["people"], ensure_ascii=False), json.dumps(record["relationships"], ensure_ascii=False), record["place"], record["time"], record["activity"], json.dumps(record["objects"], ensure_ascii=False), record["emotion"], record["story"], record["source"], float(record["confidence"]), int(bool(record["sensitive"])), record["language"], record["sequence"], json.dumps(record["tags"], ensure_ascii=False), record.get("created_at", now), record.get("updated_at", now)))
        self._connection.commit()
        return self.get_memory(memory_id) or {}

    def get_memory(self, memory_id: str, patient_id: str | None = None) -> dict[str, Any] | None:
        query = "SELECT * FROM memories WHERE memory_id = ?"
        params: list[Any] = [memory_id]
        if patient_id is not None:
            query += " AND patient_id = ?"
            params.append(patient_id)
        row = self._connection.execute(query, params).fetchone()
        return self._decode(row) if row else None

    def find_memory_by_story(self, patient_id: str, title: str, story: str, source: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            "SELECT * FROM memories WHERE patient_id = ? AND title = ? AND story = ? AND source = ?",
            (patient_id, title, story, source),
        ).fetchone()
        return self._decode(row) if row else None

    def list_memories(self, patient_id: str) -> list[dict[str, Any]]:
        rows = self._connection.execute("SELECT * FROM memories WHERE patient_id = ? ORDER BY COALESCE(sequence, 2147483647), created_at", (patient_id,)).fetchall()
        return [self._decode(row) for row in rows]

    def update_memory(self, memory_id: str, patient_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        current = self.get_memory(memory_id, patient_id)
        if current is None:
            return None
        allowed = {"title", "people", "relationships", "place", "time", "activity", "objects", "emotion", "story", "source", "confidence", "sensitive", "language", "sequence", "tags"}
        updates = {key: value for key, value in updates.items() if key in allowed}
        if not updates:
            return current
        columns = []
        values: list[Any] = []
        json_fields = {"people", "relationships", "objects", "tags"}
        for key, value in updates.items():
            columns.append(f"{key} = ?")
            values.append(json.dumps(value, ensure_ascii=False) if key in json_fields else int(bool(value)) if key == "sensitive" else value)
        columns.append("updated_at = ?")
        values.extend([datetime.now(timezone.utc).isoformat(), memory_id, patient_id])
        self._connection.execute(f"UPDATE memories SET {', '.join(columns)} WHERE memory_id = ? AND patient_id = ?", values)
        self._connection.commit()
        return self.get_memory(memory_id, patient_id)

    def delete_memory(self, memory_id: str, patient_id: str) -> bool:
        cursor = self._connection.execute("DELETE FROM memories WHERE memory_id = ? AND patient_id = ?", (memory_id, patient_id))
        self._connection.execute("DELETE FROM memory_chunks WHERE memory_id = ? AND patient_id = ?", (memory_id, patient_id))
        self._connection.commit()
        return cursor.rowcount == 1

    def save_chunk(self, chunk: dict[str, Any]) -> dict[str, Any]:
        chunk_id = chunk.get("chunk_id") or f"chunk_{uuid4().hex}"
        self._connection.execute("INSERT INTO memory_chunks VALUES (?, ?, ?, ?, ?, ?, ?)", (chunk_id, chunk["memory_id"], chunk["patient_id"], chunk["section"], chunk["text"], chunk.get("language", "en"), chunk["sequence"]))
        self._connection.commit()
        return {**chunk, "chunk_id": chunk_id}

    def list_chunks(self, patient_id: str, memory_id: str | None = None) -> list[dict[str, Any]]:
        if memory_id:
            rows = self._connection.execute("SELECT * FROM memory_chunks WHERE patient_id = ? AND memory_id = ? ORDER BY sequence", (patient_id, memory_id)).fetchall()
        else:
            rows = self._connection.execute("SELECT * FROM memory_chunks WHERE patient_id = ? ORDER BY sequence", (patient_id,)).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self._connection.close()

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        for field in ("people", "relationships", "objects", "tags"):
            result[field] = json.loads(result[field])
        result["sensitive"] = bool(result["sensitive"])
        return result
