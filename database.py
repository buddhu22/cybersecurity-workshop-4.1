"""Small JSON persistence layer for synthetic notice records."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "notices.json"
logger = logging.getLogger(__name__)


class NoticeStoreError(Exception):
    """Raised when existing notice data cannot safely be read or written."""


def load_notices(path: Path = DATA_FILE) -> list[dict[str, Any]]:
    """Load notices, creating an empty store when the file does not exist."""
    if not path.exists():
        save_notices([], path)
        return []
    try:
        with path.open("r", encoding="utf-8") as notice_file:
            data = json.load(notice_file)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        logger.exception("Could not load notice JSON store")
        raise NoticeStoreError("Notice data could not be read safely.") from error
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        logger.error("Notice JSON store has an unexpected structure")
        raise NoticeStoreError("Notice data has an invalid structure.")
    return data


def save_notices(notices: list[dict[str, Any]], path: Path = DATA_FILE) -> None:
    """Write notices without replacing the file until serialization succeeds."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(notices, ensure_ascii=False, indent=2) + "\n"
        temporary_path = path.with_name(f"{path.name}.tmp")
        temporary_path.write_text(serialized, encoding="utf-8")
        temporary_path.replace(path)
    except OSError as error:
        logger.exception("Could not save notice JSON store")
        raise NoticeStoreError("Notice data could not be saved.") from error


def next_notice_id(notices: list[dict[str, Any]]) -> str:
    """Generate the next unused sequential notice ID."""
    used_ids = {str(notice.get("id", "")) for notice in notices}
    number = 1
    while f"N{number:03d}" in used_ids:
        number += 1
    return f"N{number:03d}"


def create_notice(
    notices: list[dict[str, Any]], fields: dict[str, str], path: Path = DATA_FILE
) -> dict[str, Any]:
    """Create and persist a notice using validated form fields."""
    notice = {
        "id": next_notice_id(notices),
        **fields,
        "status": fields["item_type"],
        "created_at": datetime.now().replace(microsecond=0).isoformat(),
    }
    save_notices([*notices, notice], path)
    return notice


def resolve_notice(notices: list[dict[str, Any]], notice_id: str, path: Path = DATA_FILE) -> bool:
    """Mark a notice resolved and persist it. Return whether it changed."""
    for notice in notices:
        if notice.get("id") == notice_id:
            if notice.get("status") == "Resolved":
                return False
            notice["status"] = "Resolved"
            save_notices(notices, path)
            return True
    return False
