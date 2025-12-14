import os
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from deepface import DeepFace
from shutil import copy2
from datetime import datetime

def is_image(filename):
    return filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))

class FaceScannerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Face Matching Scanner")
        self.root.geometry("900x650")

        self.folder_path = StringVar()
        self.ref_image_path = StringVar()

        self.current_preview = None
        self.preview_label = None  
        self.download_btn = None    # download button initially hidden

        self.create_ui()

    def create_ui(self):
        canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient=VERTICAL, command=canvas.yview)
        self.scroll_frame = Frame(canvas)

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # ---- Folder Selection ----
        Label(self.scroll_frame, text="Selected Folder:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=3)
        Entry(self.scroll_frame, textvariable=self.folder_path, width=70).pack(anchor="w", padx=10)
        Button(self.scroll_frame, text="Select Folder", command=self.select_folder, width=18).pack(anchor="w", padx=10, pady=3)

        # ---- Reference Selection ----
        Label(self.scroll_frame, text="Reference Image:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=3)
        Entry(self.scroll_frame, textvariable=self.ref_image_path, width=70).pack(anchor="w", padx=10)
        Button(self.scroll_frame, text="Select Reference Image", command=self.select_reference, width=22).pack(anchor="w", padx=10, pady=3)

        # Placeholder for preview
        self.preview_placeholder = Frame(self.scroll_frame)
        self.preview_placeholder.pack()

        # ---- Scan Log ----
        Label(self.scroll_frame, text="Scan Log:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=3)
        self.scan_box = Text(self.scroll_frame, height=6, width=100)
        self.scan_box.pack(padx=10)

        # ---- Matched Images ----
        Label(self.scroll_frame, text="Matched Images:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=3)
        self.match_box = Text(self.scroll_frame, height=6, width=100)
        self.match_box.pack(padx=10)

        # ---- Start Scan ----
        Button(
            self.scroll_frame,
            text="START SCAN",
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            command=self.start_scan_thread
        ).pack(pady=15)

        # --- Download button (hidden at first) ---
        self.download_btn = Button(
            self.scroll_frame,
            text="Download All Matched Images",
            bg="#007bff",
            fg="white",
            font=("Arial", 11, "bold"),
            width=30,
            command=self.download_matched_images
        )

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def select_reference(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if path:
            self.ref_image_path.set(path)

    def start_scan_thread(self):
        threading.Thread(target=self.start_scan, daemon=True).start()

    def show_preview(self, img_path):
        if self.preview_label is None:
            Label(self.preview_placeholder, text="Preview (Current Image):", font=("Arial", 11)).pack(anchor="w", padx=10, pady=5)
            self.preview_label = Label(self.preview_placeholder, width=250, height=160, bg="#dddddd")
            self.preview_label.pack(padx=10, pady=3)

        img = Image.open(img_path)
        img = img.resize((250, 160), Image.LANCZOS)
        self.current_preview = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.current_preview)

    def start_scan(self):
        folder = self.folder_path.get().strip()
        ref = self.ref_image_path.get().strip()

        self.scan_box.delete("1.0", END)
        self.match_box.delete("1.0", END)

        # Hide download button until finished
        self.download_btn.pack_forget()

        if not folder:
            messagebox.showerror("Error", "Please select a folder!")
            return

        if not ref:
            messagebox.showerror("Error", "Please select a reference image!")
            return

        try:
            DeepFace.verify(ref, ref)
        except:
            messagebox.showerror("Error", "Reference image has no detectable face!")
            return

        files = [f for f in os.listdir(folder) if is_image(f)]
        total = len(files)

        if total == 0:
            messagebox.showinfo("Empty Folder", "No images found.")
            return

        self.scan_box.insert(END, f"Scanning {total} images...\n\n")

        for i, file in enumerate(files, start=1):
            path = os.path.join(folder, file)

            self.show_preview(path)

            self.scan_box.insert(END, f"{i}/{total}: {file}\n")
            self.scan_box.see(END)

            try:
                result = DeepFace.verify(ref, path, model_name="Facenet")
                if result["verified"]:
                    self.match_box.insert(END, f"MATCH: {path}\n")
            except:
                self.scan_box.insert(END, " - No face detected\n")

        self.scan_box.insert(END, "\nScanning Completed.\n")

        # Show download button now
        self.download_btn.pack(pady=10)

    def download_matched_images(self):
        # Auto-create new folder for matched images
        folder_name = "Matched_Images_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        target_folder = os.path.join(os.getcwd(), folder_name)
        os.makedirs(target_folder, exist_ok=True)

        matched_lines = self.match_box.get("1.0", END).strip().split("\n")
        matched_paths = [line.replace("MATCH:", "").strip() for line in matched_lines if line.startswith("MATCH:")]

        if not matched_paths:
            messagebox.showinfo("No Matches", "No matched images found.")
            return

        count = 0
        for img_path in matched_paths:
            try:
                copy2(img_path, target_folder)
                count += 1
            except:
                pass

        messagebox.showinfo(
            "Download Complete",
            f"{count} matched images saved in folder:\n\n{target_folder}"
        )


root = Tk()
FaceScannerApp(root)
root.mainloop()

# pip install deepface opencv-python tf-keras pillow
