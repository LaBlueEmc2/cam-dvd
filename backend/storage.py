# backend/storage.py
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class StorageDevice:
    name: str                 # e.g. /dev/sda1
    kname: str                # e.g. sda1
    model: Optional[str]
    size_bytes: int
    size_human: str
    fstype: Optional[str]
    mountpoint: Optional[Path]
    tran: Optional[str]       # usb/mmc/nvme/sata/...
    ro: bool
    type: Optional[str] = None   # disk/part/rom/loop/lvm/crypt...
    rm: Optional[bool] = None    # removable
    pkname: Optional[str] = None # parent disk name (sda, nvme0n1,...)


class StorageManager:
    """
    Liệt kê thiết bị lưu trữ theo lsblk.
    Mục tiêu: chỉ hiện USB/SD/HDD rời (và /dev/sr0 để burn), ẩn ổ hệ thống.
    """

    SYSTEM_MOUNTPOINTS = {"/", "/boot", "/boot/efi"}

    def list_storage_devices(self) -> list[StorageDevice]:
        # -J: JSON, -b: size bytes
        # thêm: TYPE, RM, PKNAME để lọc ổ hệ thống
        cmd = ["lsblk", "-J", "-b", "-o",
               "NAME,KNAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINT,TRAN,RO,RM,PKNAME"]
        p = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(p.stdout)

        out: list[StorageDevice] = []
        for dev in data.get("blockdevices", []):
            out.extend(self._flatten(dev))

        root_parents = self._get_root_parent_disks()

        filtered: list[StorageDevice] = []
        for d in out:
            if not d.name.startswith("/dev/"):
                continue

            # 1) Bỏ loại ảo/hệ thống thường gặp
            if d.kname.startswith(("loop", "dm-")):
                continue
            if d.type in {"lvm", "crypt"}:
                continue

            # 2) Bỏ mọi thứ thuộc ổ hệ thống (root disk + các partition của nó)
            # root_parents chứa: {'nvme0n1', 'sda', ...}
            if d.pkname and d.pkname in root_parents:
                continue
            # nếu bản thân là root disk
            if d.kname in root_parents:
                continue

            # 3) Bỏ mountpoint hệ thống
            if d.mountpoint and str(d.mountpoint) in self.SYSTEM_MOUNTPOINTS:
                continue

            # 4) Cho phép ổ quang để burn
            if d.kname.startswith("sr"):
                filtered.append(d)
                continue

            # 5) Chỉ giữ thiết bị rời / gắn ngoài:
            #    - tran=usb/mmc
            #    - hoặc rm=1
            #    - hoặc mount dưới /media hoặc /run/media (auto-mount)
            mp = str(d.mountpoint) if d.mountpoint else ""
            is_removable_like = (d.tran in {"usb", "mmc"} or bool(d.rm))
            is_user_mount = mp.startswith("/media/") or mp.startswith("/run/media/")

            if is_removable_like or is_user_mount:
                # thường chỉ cần partition (part) để duyệt file
                # nhưng có NVR export ra disk dạng "disk" không phân vùng → vẫn giữ nếu có mountpoint
                if d.type in {"part", "disk"}:
                    filtered.append(d)

        # Sort: mounted first, then usb/mmc first
        def key(x: StorageDevice):
            mp = 0 if x.mountpoint else 1
            t = 0 if x.tran in {"usb", "mmc"} else 1
            return (mp, t, x.name)

        filtered.sort(key=key)

        for i, d in enumerate(filtered):
            filtered[i].size_human = self._human(d.size_bytes)

        return filtered

    # -------- helpers --------

    def _get_root_parent_disks(self) -> set[str]:
        """
        Trả về tập parent disks của filesystem '/' (để loại trừ ổ hệ thống).
        Ví dụ:
          - nếu '/' nằm trên /dev/nvme0n1p3 => return {'nvme0n1'}
          - nếu '/' nằm trên /dev/dm-0 => truy ra pkname => nvme0n1/sda...
        """
        parents: set[str] = set()

        # find source of '/'
        src = ""
        try:
            p = subprocess.run(["findmnt", "-n", "-o", "SOURCE", "/"],
                               capture_output=True, text=True, check=True)
            src = (p.stdout or "").strip()
        except Exception:
            src = ""

        # normalize source (strip [..] for LVM or mapper)
        # example: /dev/mapper/ubuntu--vg-ubuntu--lv
        if src.startswith("/dev/mapper/"):
            # ask lsblk for pkname chain
            pass

        # query pkname chain
        # lsblk -no PKNAME <device> returns parent kernel name (e.g. nvme0n1)
        def pkname_of(dev: str) -> str:
            try:
                pp = subprocess.run(["lsblk", "-no", "PKNAME", dev],
                                    capture_output=True, text=True, check=True)
                return (pp.stdout or "").strip()
            except Exception:
                return ""

        # If findmnt gave /dev/dm-0, try pkname -> might be nvme0n1
        if src.startswith("/dev/"):
            pk = pkname_of(src)
            if pk:
                parents.add(pk)

            # Also, if src itself is a partition, add its own parent disk via regex
            # nvme0n1p3 -> nvme0n1 ; sda3 -> sda
            m = re.match(r"^/dev/(nvme\d+n\d+)", src)
            if m:
                parents.add(m.group(1))
            m2 = re.match(r"^/dev/([a-z]+)\d+$", src)
            if m2:
                parents.add(m2.group(1))

        # Fallback: also add disk that contains /boot if exists
        for mp in ("/boot", "/boot/efi"):
            try:
                pp = subprocess.run(["findmnt", "-n", "-o", "SOURCE", mp],
                                    capture_output=True, text=True, check=True)
                s2 = (pp.stdout or "").strip()
                if s2.startswith("/dev/"):
                    pk2 = pkname_of(s2)
                    if pk2:
                        parents.add(pk2)
            except Exception:
                pass

        return parents

    def _flatten(self, node: dict, parent: str | None = None) -> list[StorageDevice]:
        devices: list[StorageDevice] = []
        name = node.get("name")
        kname = node.get("kname", name)
        devpath = f"/dev/{kname}" if kname else f"/dev/{name}"

        mp = node.get("mountpoint")
        d = StorageDevice(
            name=devpath,
            kname=kname,
            model=node.get("model"),
            size_bytes=int(node.get("size") or 0),
            size_human="",
            fstype=node.get("fstype"),
            mountpoint=Path(mp) if mp else None,
            tran=node.get("tran"),
            ro=bool(int(node.get("ro") or 0)),
            type=node.get("type"),
            rm=bool(int(node.get("rm") or 0)) if node.get("rm") is not None else None,
            pkname=node.get("pkname"),
        )
        devices.append(d)

        for ch in node.get("children", []) or []:
            devices.extend(self._flatten(ch, parent=devpath))
        return devices

    def _human(self, n: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        f = float(n)
        i = 0
        while f >= 1024 and i < len(units) - 1:
            f /= 1024
            i += 1
        return f"{f:.1f}{units[i]}"
