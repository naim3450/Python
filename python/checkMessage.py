import json
import os
from datetime import datetime

# Change this path to where your message JSON files are
messages_folder = 'path/to/your/facebook/messages/inbox'

# The message you want to search
search_text = "happy birthday"

def search_messages(folder_path, search_text):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = data.get("messages", [])
                    for msg in messages:
                        if msg.get("type") == "Generic" and msg.get("sender_name") and msg.get("content"):
                            if search_text.lower() in msg["content"].lower():
                                timestamp = int(msg["timestamp_ms"])
                                date = datetime.fromtimestamp(timestamp / 1000)
                                sender = msg["sender_name"]
                                print(f"[{date}] {sender}: {msg['content']}")

# Call the function
search_messages(messages_folder, search_text)
