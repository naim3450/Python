import os
import shutil
from datetime import datetime

# ---- SETTINGS ----
FOLDER_TO_ORGANIZE = os.path.expanduser("~/Downloads")  # Change if needed
ORGANIZE_BY = "type"  # "type" or "date"
# -------------------

def get_file_type(extension):
    file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".md", ".rtf"],
        "Spreadsheets": [".xls", ".xlsx", ".csv"],
        "Videos": [".mp4", ".avi", ".mov", ".mkv"],
        "Audio": [".mp3", ".wav", ".aac"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Programs": [".exe", ".msi", ".dmg", ".pkg"],
        "Code": [".py", ".js", ".html", ".css", ".json", ".java"]
    }

    extension = extension.lower()
    for category, exts in file_types.items():
        if extension in exts:
            return category
    return "Others"


def organize_by_type(file_path, filename):
    extension = os.path.splitext(filename)[1]
    folder_name = get_file_type(extension)
    target_folder = os.path.join(FOLDER_TO_ORGANIZE, folder_name)
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(target_folder, filename))


def organize_by_date(file_path, filename):
    creation_time = os.path.getctime(file_path)
    date_folder = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")
    target_folder = os.path.join(FOLDER_TO_ORGANIZE, date_folder)
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(target_folder, filename))


def organize_files():
    for filename in os.listdir(FOLDER_TO_ORGANIZE):
        file_path = os.path.join(FOLDER_TO_ORGANIZE, filename)

        if os.path.isfile(file_path) and not filename.startswith("."):
            if ORGANIZE_BY == "type":
                organize_by_type(file_path, filename)
            elif ORGANIZE_BY == "date":
                organize_by_date(file_path, filename)

    print("✨ Files organized successfully!")


if __name__ == "__main__":
    organize_files()
