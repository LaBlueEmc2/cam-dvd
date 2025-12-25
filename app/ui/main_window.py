# app/ui/main_window.py
from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QMessageBox, QComboBox, QTextEdit, QGroupBox, QFormLayout,
    QTreeView
)
from PyQt6.QtGui import (QAction, QFileSystemModel)

from backend.storage import StorageManager, StorageDevice
from backend.video import cut_video_segment
from backend.hashing import sha256_file
from backend.logger import LogManager, CaptureLog
from backend.burn import burn_folder_to_disc


VIDEO_EXTS = ["*.mp4", "*.avi", "*.mkv", "*.dav", "*.h264", "*.h265"]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CAM-DVD Tool (Prototype)")
        self.resize(1100, 700)

        self.storage = StorageManager()
        self.logman = LogManager(log_dir=Path("logs"))
        Path("spool").mkdir(parents=True, exist_ok=True)

        self.selected_device: StorageDevice | None = None
        self.selected_file: Path | None = None
        self.output_dir: Path = Path("spool") / "job_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._build_ui()
        self._refresh_devices()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        # Device group
        gb_dev = QGroupBox("Nguồn dữ liệu (USB / SD / HDD)")
        dev_layout = QHBoxLayout(gb_dev)

        self.cb_devices = QComboBox()
        self.btn_refresh = QPushButton("Quét thiết bị")
        self.btn_mount = QPushButton("Mount (RO)")
        self.btn_mount.setEnabled(False)

        self.btn_refresh.clicked.connect(self._refresh_devices)
        self.btn_mount.clicked.connect(self._mount_selected_device)

        dev_layout.addWidget(QLabel("Thiết bị:"))
        dev_layout.addWidget(self.cb_devices, 1)
        dev_layout.addWidget(self.btn_refresh)
        dev_layout.addWidget(self.btn_mount)
        layout.addWidget(gb_dev)

        # Browser group (QTreeView rooted at mountpoint)
        gb_browser = QGroupBox("Duyệt file trong thiết bị (root = mountpoint)")
        b_layout = QVBoxLayout(gb_browser)

        self.model = QFileSystemModel()
        self.model.setReadOnly(True)
        self.model.setNameFilters(VIDEO_EXTS)
        self.model.setNameFilterDisables(False)  # chỉ hiện video

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setSortingEnabled(True)
        self.tree.doubleClicked.connect(self._on_tree_double_click)

        # Ẩn các cột không cần
        self.tree.setColumnWidth(0, 520)
        for col in [1, 2, 3]:
            self.tree.setColumnHidden(col, col != 1)  # giữ cột Size (1) nếu muốn
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)

        b_layout.addWidget(self.tree)
        layout.addWidget(gb_browser, 3)

        # File selection group
        gb_file = QGroupBox("File video đã chọn & khoảng thời gian cắt")
        form = QFormLayout(gb_file)

        self.ed_file = QLineEdit()
        self.ed_file.setReadOnly(True)
        form.addRow("File video:", self.ed_file)

        self.ed_start = QLineEdit("00:00:00")
        self.ed_end = QLineEdit("00:00:10")
        form.addRow("Start (HH:MM:SS):", self.ed_start)
        form.addRow("End (HH:MM:SS):", self.ed_end)

        layout.addWidget(gb_file)

        # Actions
        actions = QHBoxLayout()
        self.btn_cut_hash_log = QPushButton("Cắt + Hash + Log")
        self.btn_cut_hash_log.clicked.connect(self._do_cut_hash_log)

        self.btn_burn = QPushButton("Ghi đĩa (Burn)")
        self.btn_burn.clicked.connect(self._do_burn)

        actions.addWidget(self.btn_cut_hash_log)
        actions.addWidget(self.btn_burn)
        layout.addLayout(actions)

        # Status + log output
        self.lb_status = QLabel("Trạng thái: sẵn sàng")
        self.lb_status.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.lb_status)

        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        layout.addWidget(self.txt, 2)

        self.cb_devices.currentIndexChanged.connect(self._on_device_changed)

    def _log(self, msg: str) -> None:
        self.txt.append(msg)
        self.txt.ensureCursorVisible()

    def _set_status(self, s: str) -> None:
        self.lb_status.setText(f"Trạng thái: {s}")

    def _refresh_devices(self) -> None:
        self.cb_devices.blockSignals(True)
        self.cb_devices.clear()

        devices = self.storage.list_storage_devices()
        if not devices:
            self.cb_devices.addItem("(Không phát hiện thiết bị)", None)
            self.selected_device = None
        else:
            for d in devices:
                label = f"{d.name} | {d.model or '-'} | {d.size_human} | mount: {d.mountpoint or '-'}"
                self.cb_devices.addItem(label, d)
            self.selected_device = devices[0]

        self.cb_devices.blockSignals(False)
        self._on_device_changed()

    def _on_device_changed(self) -> None:
        data = self.cb_devices.currentData()
        self.selected_device = data if isinstance(data, StorageDevice) else None
        self.selected_file = None
        self.ed_file.setText("")

        if not self.selected_device:
            self.btn_mount.setEnabled(False)
            self._log("Chưa có thiết bị được chọn.")
            return

        d = self.selected_device
        self._log(f"Chọn thiết bị: {d.name} ({d.size_human})")

        # Mount button enable logic
        self.btn_mount.setEnabled(d.mountpoint is None and (d.fstype is not None))

        # Nếu đã có mountpoint -> set root cho tree view
        if d.mountpoint and d.mountpoint.exists():
            self._set_tree_root(d.mountpoint)
        else:
            # Chưa mount -> tree root về home để tránh hiển thị toàn hệ thống
            self._set_tree_root(Path.home())
            self._log("Thiết bị chưa được mount. Bấm 'Mount (RO)' để mount chỉ đọc.")

    def _mount_selected_device(self) -> None:
        if not self.selected_device:
            return
        d = self.selected_device
        try:
            self._set_status("mount RO…")
            mp = self.storage.mount_ro(d)
            self._log(f"Mount RO OK: {mp}")
            # Refresh devices to update mountpoint display
            self._refresh_devices()
        except Exception as e:
            QMessageBox.critical(self, "Mount lỗi", str(e))
        finally:
            self._set_status("sẵn sàng")

    def _set_tree_root(self, root_path: Path) -> None:
        root_str = str(root_path)
        self.model.setRootPath(root_str)
        self.tree.setRootIndex(self.model.index(root_str))
        self._log(f"Tree root: {root_str}")

    def _on_tree_double_click(self, idx) -> None:
        path = Path(self.model.filePath(idx))
        if path.is_file():
            self.selected_file = path
            self.ed_file.setText(str(path))
            self._log(f"Đã chọn file: {path}")

    def _do_cut_hash_log(self) -> None:
        if not self.selected_file or not self.selected_file.exists():
            QMessageBox.warning(self, "Thiếu file", "Vui lòng double-click để chọn file video trong tree.")
            return

        start = self.ed_start.text().strip()
        end = self.ed_end.text().strip()

        self._set_status("đang xử lý…")
        self._log("Bắt đầu cắt video…")

        try:
            out_name = f"cut_{self.selected_file.stem}_{start.replace(':','')}_{end.replace(':','')}{self.selected_file.suffix or '.mp4'}"
            out_path = self.output_dir / out_name

            cut_video_segment(self.selected_file, out_path, start, end)
            self._log(f"Đã cắt xong: {out_path}")

            h = sha256_file(out_path)
            self._log(f"SHA-256: {h}")

            cap = CaptureLog(
                unit_id="UNIT-001",
                operator_id=os.getenv("USER", "unknown"),
                source_device=asdict(self.selected_device) if self.selected_device else None,
                input_file=str(self.selected_file),
                start_time=start,
                end_time=end,
                output_file=str(out_path),
                sha256=h,
                status="OK",
                notes="Prototype log"
            )
            log_path = self.logman.write_capture_log(cap)
            self._log(f"Đã ghi nhật ký: {log_path}")

            QMessageBox.information(self, "Hoàn tất", "Cắt + Hash + Log thành công.")
        except Exception as e:
            self._log(f"[LỖI] {e}")
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            self._set_status("sẵn sàng")

    def _do_burn(self) -> None:
        folder = self.output_dir
        if not folder.exists() or not any(folder.iterdir()):
            QMessageBox.warning(self, "Không có dữ liệu", "Thư mục spool/job_output đang trống.")
            return

        self._set_status("đang ghi đĩa…")
        self._log("Bắt đầu ghi đĩa (burn)…")

        try:
            burn_folder_to_disc(folder, device="/dev/sr0")
            self._log("Ghi đĩa xong + verify OK.")
            QMessageBox.information(self, "Hoàn tất", "Ghi đĩa thành công.")
        except Exception as e:
            self._log(f"[LỖI burn] {e}")
            QMessageBox.critical(self, "Lỗi ghi đĩa", str(e))
        finally:
            self._set_status("sẵn sàng")
