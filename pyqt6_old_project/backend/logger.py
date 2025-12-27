from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class CaptureLog:
    unit_id: str
    operator_id: str
    source_device: Optional[dict[str, Any]]
    input_file: str
    start_time: str
    end_time: str
    output_file: str
    sha256: str
    status: str
    notes: str = ""


def _json_default(o: Any) -> Any:
    # Fix: PosixPath / Path không JSON được
    if isinstance(o, Path):
        return str(o)
    return str(o)


class LogManager:
    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write_capture_log(self, cap: CaptureLog) -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.log_dir / f"capture_{cap.unit_id}_{ts}.json"
        payload = {
            "schema": "cam-dvd.capture.v1",
            "created_at_utc": ts,
            "data": cap.__dict__,
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
            encoding="utf-8",
        )
        return path