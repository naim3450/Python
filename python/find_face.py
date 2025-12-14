import sys
import os
import shutil
from pathlib import Path
from io import BytesIO

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QProgressBar, QSpinBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from PIL import Image, ImageQt
import numpy as np
import face_recognition

# ---------- Worker thread that does scanning and matching ----------
class MatcherThread(QThread):
    progress = pyqtSignal(int)                 # percent
    status = pyqtSignal(str)                   # text status
    matched = pyqtSignal(str, QPixmap)         # image path + pixmap
    finished_signal = pyqtSignal(list)         # list of matched paths

    def __init__(self, folder, reference_path, tolerance=0.45):
        super().__init__()
        self.folder = Path(folder)
        self.reference_path = Path(reference_path)
        self.tolerance = tolerance
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        matched = []
        try:
            self.status.emit(f"Loading reference image...")
            ref_image = face_recognition.load_image_file(str(self.reference_path))
            ref_encs = face_recognition.face_encodings(ref_image)
            if not ref_encs:
                self.status.emit("No face found in reference image.")
                self.finished_signal.emit([])
                return
            ref_enc = ref_encs[0]
        except Exception as e:
            self.status.emit(f"Failed to load reference: {e}")
            self.finished_signal.emit([])
            return

        images = [p for p in self.folder.iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp')]
        total = max(1, len(images))
        self.status.emit(f"Scanning {total} images...")

        for idx, img_path in enumerate(images, start=1):
            if not self._is_running:
                self.status.emit("Cancelled.")
                break

            try:
                # load and get encodings
                unknown_img = face_recognition.load_image_file(str(img_path))
                encs = face_recognition.face_encodings(unknown_img)

                found = False
                if encs:
                    matches = face_recognition.compare_faces(encs, ref_enc, tolerance=self.tolerance)
                    if any(matches):
                        found = True

                # emit if matched
                if found:
                    matched.append(str(img_path))
                    pix = self._make_pixmap(str(img_path), max_size=200)
                    self.matched.emit(str(img_path), pix)

                percent = int((idx / total) * 100)
                self.progress.emit(percent)
                self.status.emit(f"Scanned {idx}/{total}: {img_path.name} {'(MATCH)' if found else ''}")

            except Exception as e:
                # continue on error but report
                self.status.emit(f"Error scanning {img_path.name}: {e}")

        self.status.emit("Finished scanning.")
        self.finished_signal.emit(matched)

    def _make_pixmap(self, path, max_size=200):
        try:
            im = Image.open(path)
            im.thumbnail((max_size, max_size), Image.LANCZOS)
            qim = ImageQt.ImageQt(im.convert("RGBA"))
            pix = QPixmap.fromImage(qim)
            return pix
        except Exception:
            # fallback: empty pixmap
            return QPixmap(max_size, max_size)


# ---------- Main Window ----------
class FaceMatcherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Matcher — Desktop GUI")
        self.resize(900, 600)
        self.folder = None
        self.reference = None
        self.matcher_thread = None
        self.matched_paths = []

        self._build_ui()

    def _build_ui(self):
        # Controls
        self.select_folder_btn = QPushButton("Select Folder to Scan")
        self.select_folder_btn.clicked.connect(self.select_folder)

        self.select_ref_btn = QPushButton("Select Reference Image")
        self.select_ref_btn.clicked.connect(self.select_reference)

        self.start_btn = QPushButton("Start Scan")
        self.start_btn.clicked.connect(self.start_scan)
        self.start_btn.setEnabled(False)

        self.cancel_btn = QPushButton("Cancel Scan")
        self.cancel_btn.clicked.connect(self.cancel_scan)
        self.cancel_btn.setEnabled(False)

        self.copy_btn = QPushButton("Copy Matches to...")
        self.copy_btn.clicked.connect(self.copy_matches)
        self.copy_btn.setEnabled(False)

        self.tolerance_label = QLabel("Tolerance (lower = stricter):")
        self.tolerance_spinner = QSpinBox()
        self.tolerance_spinner.setRange(20, 70)  # map to 0.20 - 0.70
        self.tolerance_spinner.setValue(45)

        # Status and progress
        self.status_label = QLabel("Ready.")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # List for matches with thumbnails
        self.matches_list = QListWidget()
        self.matches_list.setViewMode(QListWidget.IconMode)
        self.matches_list.setIconSize(Qt.QSize(160, 160))
        self.matches_list.setResizeMode(QListWidget.Adjust)
        self.matches_list.setSpacing(10)

        # Layout assembly
        top_row = QHBoxLayout()
        top_row.addWidget(self.select_folder_btn)
        top_row.addWidget(self.select_ref_btn)
        top_row.addWidget(self.start_btn)
        top_row.addWidget(self.cancel_btn)
        top_row.addWidget(self.copy_btn)
        top_row.addStretch()
        top_row.addWidget(self.tolerance_label)
        top_row.addWidget(self.tolerance_spinner)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QLabel("Matched Images:"))
        main_layout.addWidget(self.matches_list)

        self.setLayout(main_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder with images")
        if folder:
            self.folder = folder
            self.status_label.setText(f"Folder selected: {folder}")
            self._enable_start_if_ready()

    def select_reference(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select reference image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.reference = file_path
            self.status_label.setText(f"Reference selected: {Path(file_path).name}")
            self._enable_start_if_ready()

    def _enable_start_if_ready(self):
        if self.folder and self.reference:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

    def start_scan(self):
        if not (self.folder and self.reference):
            QMessageBox.warning(self, "Missing input", "Please select both folder and reference image.")
            return

        tolerance = self.tolerance_spinner.value() / 100.0
        # clear previous results
        self.matches_list.clear()
        self.matched_paths = []
        # set buttons
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.copy_btn.setEnabled(False)

        # create and start worker thread
        self.matcher_thread = MatcherThread(self.folder, self.reference, tolerance=tolerance)
        self.matcher_thread.progress.connect(self.progress_bar.setValue)
        self.matcher_thread.status.connect(self._set_status)
        self.matcher_thread.matched.connect(self._add_match_item)
        self.matcher_thread.finished_signal.connect(self._scan_finished)
        self.matcher_thread.start()
        self._set_status("Started scanning...")

    def cancel_scan(self):
        if self.matcher_thread:
            self.matcher_thread.stop()
            self._set_status("Stopping...")

    def _set_status(self, text):
        self.status_label.setText(text)

    def _add_match_item(self, path, pixmap):
        self.matched_paths.append(path)
        item = QListWidgetItem(QIcon(pixmap), Path(path).name)
        item.setToolTip(path)
        self.matches_list.addItem(item)

    def _scan_finished(self, matched_list):
        self._set_status(f"Scan finished. {len(matched_list)} matches found.")
        self.progress_bar.setValue(100)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.copy_btn.setEnabled(bool(matched_list))

    def copy_matches(self):
        if not self.matched_paths:
            QMessageBox.information(self, "No matches", "There are no matched images to copy.")
            return

        target = QFileDialog.getExistingDirectory(self, "Select destination folder to copy matched images")
        if not target:
            return

        copied = 0
        errors = []
        for p in self.matched_paths:
            try:
                dest = Path(target) / Path(p).name
                # avoid overwriting: if exists, append index
                i = 1
                dest_name = dest
                while dest_name.exists():
                    dest_name = Path(target) / (Path(p).stem + f"_{i}" + Path(p).suffix)
                    i += 1
                shutil.copy2(p, str(dest_name))
                copied += 1
            except Exception as e:
                errors.append((p, str(e)))

        QMessageBox.information(self, "Copy complete", f"Copied {copied} images to:\n{target}")
        if errors:
            self._set_status(f"Some errors occurred copying files. Check console for details.")
            print("Errors while copying:")
            for p, err in errors:
                print(p, err)


# ---------- run ----------
def main():
    app = QApplication(sys.argv)
    window = FaceMatcherApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()




# pip install PyQt5 Pillow numpy face_recognition
# conda install -c conda-forge dlib face_recognition
