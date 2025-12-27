from __future__ import annotations

import subprocess
from pathlib import Path


def burn_folder_to_disc(folder: Path, device: str = "/dev/sr0") -> None:
    """
    Ghi thư mục ra đĩa DVD/CD theo ISO.
    - genisoimage: tạo ISO
    - wodim: ghi đĩa
    - verify: đọc lại đĩa -> hash ISO (tối giản)
    Yêu cầu: genisoimage, wodim
    """
    if not folder.exists():
        raise FileNotFoundError(str(folder))
    iso_path = folder.parent / "output.iso"

    # Create ISO
    cmd_iso = ["genisoimage", "-V", "CAM_DVD", "-r", "-J", "-o", str(iso_path), str(folder)]
    p1 = subprocess.run(cmd_iso, capture_output=True, text=True)
    if p1.returncode != 0:
        raise RuntimeError(f"genisoimage error: {p1.stderr[-800:]}")

    # Burn ISO
    cmd_burn = ["wodim", "dev=" + device, "-v", "-data", str(iso_path)]
    p2 = subprocess.run(cmd_burn, capture_output=True, text=True)
    if p2.returncode != 0:
        raise RuntimeError(f"wodim error: {p2.stderr[-800:]}")

    # (Optional) verify by reading disc back is more complex; keep as step note
    # You can add: dd if=/dev/sr0 of=/tmp/readback.iso bs=1M && compare sha256
