from __future__ import annotations

import subprocess
from pathlib import Path


def cut_video_segment(input_path: Path, output_path: Path, start_hms: str, end_hms: str) -> None:
    """
    Cắt đoạn video bằng ffmpeg.
    - Cách an toàn: dùng -ss, -to, re-encode nhẹ để tương thích rộng.
    - Nếu muốn nhanh hơn: có thể dùng stream copy (nhưng dễ lệch keyframe).
    """
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-ss", start_hms,
        "-to", end_hms,
        "-i", str(input_path),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {p.stderr[-800:]}")
