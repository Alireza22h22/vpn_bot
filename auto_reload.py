from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = subprocess.Popen(["python", "main.py"])

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print("تغییر شناسایی شد! راه‌اندازی مجدد...")
            self.process.kill()
            time.sleep(1)
            self.process = subprocess.Popen(["python", "main.py"])

if __name__ == "__main__":
    path = "."
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
