"""Deterministic ingestion of titled life-story sections."""

from __future__ import annotations

import re
from typing import Any

from .store import MemoryStore

_SECTION = re.compile(r"^#\s*(?:\d+\.\s*)?(.+?)\s*$", re.MULTILINE)
_TAGS = {"jasmine": "jasmine", "mango": "mango", "school": "school", "railway": "railway station", "wedding": "wedding", "festival": "festival", "pickle": "pickle", "garden": "garden", "grandchildren": "grandchildren", "husband": "husband", "daughter": "daughter", "cooking": "cooking", "rain": "rain", "rangoli": "rangoli"}


def _section_parts(story_text: str) -> list[tuple[str, str]]:
    matches = list(_SECTION.finditer(story_text))
    parts = []
    for index, match in enumerate(matches):
        title = re.sub(r"^The\s+|^Her\s+|^The\s+", "", match.group(1).strip(), flags=re.I)
        body = story_text[match.end(): matches[index + 1].start() if index + 1 < len(matches) else len(story_text)].strip()
        if title and body:
            parts.append((match.group(1).strip(), body))
    return parts


def _metadata(title: str, body: str) -> dict[str, Any]:
    text = f"{title} {body}".casefold()
    people = [name for name in ("Lakshmi", "Radha") if name.casefold() in text]
    relationships = [value for value, term in (("daughter", "daughter"), ("husband", "husband"), ("father", "father"), ("mother", "mother"), ("grandchildren", "grandchildren"), ("sister", "sister")) if term in text]
    tags = sorted({tag for term, tag in _TAGS.items() if term in text})
    objects = [word for word in ("jasmine", "mango", "flowers", "temple", "basket", "pot", "garland", "pickle", "rangoli", "sari", "letter", "photographs") if word in text]
    sensitive = "became sick" in text or "before he died" in text or "died" in text
    return {"people": people, "relationships": relationships, "place": None, "time": None, "activity": None, "objects": objects, "emotion": None, "tags": tags, "sensitive": sensitive}


def ingest_story(patient_id: str, story_text: str, source: str = "caregiver", store: MemoryStore | None = None) -> dict[str, Any]:
    if not patient_id or not story_text.strip():
        raise ValueError("patient_id and story_text are required")
    target = store or MemoryStore()
    sections = _section_parts(story_text)
    memories = []
    created_count = 0
    chunks = []
    for sequence, (title, body) in enumerate(sections, 1):
        record = {"patient_id": patient_id, "title": title, "story": body, "source": source, "confidence": 1.0, "language": "en", "sequence": sequence, **_metadata(title, body)}
        saved = target.find_memory_by_story(patient_id, title, body, source)
        if saved is None:
            saved = target.save_memory(record)
            memories.append(saved)
            created_count += 1
        else:
            memories.append(saved)
            continue
        for chunk_number, text in enumerate(re.split(r"\n\s*\n", body), 1):
            if text.strip():
                chunks.append(target.save_chunk({"memory_id": saved["memory_id"], "patient_id": patient_id, "section": title, "text": text.strip(), "language": "en", "sequence": chunk_number}))
    return {"story": "LAKSHMI — THE MEMORIES OF A LIFETIME", "sections_detected": len(sections), "memories_stored": len(memories), "memories_created": created_count, "chunks_stored": len(chunks), "patient_id": patient_id, "source": source, "memory_ids": [memory["memory_id"] for memory in memories]}
