"""
File handler — centralised JSON read/write and helper utilities.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


def save_json(filename: str, data: Any) -> None:
    """
    Serialise *data* to a JSON file inside the data/ directory.

    Args:
        filename: e.g. "students.json"
        data    : JSON-serialisable object (list, dict, etc.)
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = _path(filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except OSError as e:
        print(f"  [FILE ERROR] Could not save '{filename}': {e}")


def load_json(filename: str, default: Any = None) -> Any:
    """
    Load and return data from a JSON file.
    Returns *default* (empty list by default) if the file doesn't exist.

    Args:
        filename: e.g. "students.json"
        default : value returned when the file is absent.
    """
    filepath = _path(filename)
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [FILE ERROR] Could not load '{filename}': {e}")
        return default if default is not None else []


def append_json(filename: str, new_item: Dict[str, Any]) -> None:
    """
    Load existing list, append *new_item*, then save back.

    Args:
        filename: e.g. "students.json"
        new_item: dict to append.
    """
    records: List[Dict[str, Any]] = load_json(filename, default=[])
    records.append(new_item)
    save_json(filename, records)


def delete_from_json(filename: str, key: str, value: Any) -> bool:
    """
    Remove the first record whose *key* equals *value* from a JSON list file.

    Returns:
        True if a record was found and removed, False otherwise.
    """
    records: List[Dict[str, Any]] = load_json(filename, default=[])
    original_len = len(records)
    records = [r for r in records if r.get(key) != value]
    if len(records) < original_len:
        save_json(filename, records)
        return True
    return False


def update_in_json(filename: str, key: str, value: Any, updated: Dict[str, Any]) -> bool:
    """
    Find the first record with *key* == *value* and replace it with *updated*.

    Returns:
        True if found and updated, False otherwise.
    """
    records: List[Dict[str, Any]] = load_json(filename, default=[])
    for idx, record in enumerate(records):
        if record.get(key) == value:
            records[idx] = updated
            save_json(filename, records)
            return True
    return False


def ensure_data_files() -> None:
    """Create empty JSON data files if they don't already exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    files = [
        "students.json", "rooms.json", "fees.json",
        "complaints.json", "visitors.json", "attendance.json", "mess.json",
    ]
    for fname in files:
        fpath = _path(fname)
        if not os.path.exists(fpath):
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump([], f)
