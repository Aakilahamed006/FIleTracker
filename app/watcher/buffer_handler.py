from watchdog.events import FileSystemEventHandler
from datetime import datetime
from collections import deque
import threading
import time

from app.watcher.event_processor import EventProcessor


class BufferHandler(FileSystemEventHandler):

    def __init__(self, repo=None):
        self.buffer = deque()
        self.lock = threading.Lock()

        self.window_seconds = 1.5
        self.timer = None

        self.processor = EventProcessor(repo=repo)

    # ---------------- PATHS ----------------
    def get_watch_paths(self):

        import os
        user = os.getlogin()

        return [
            fr"C:\Users\{user}\Desktop",
            fr"C:\Users\{user}\Documents",
            fr"C:\Users\{user}\Downloads",
            fr"C:\Users\{user}\Pictures",
        ]

    # ---------------- ADD EVENT ----------------
    def add_event(self, event_type, event):

        with self.lock:
            self.buffer.append({
                "type": event_type,
                "path": event.src_path,
                "dest": getattr(event, "dest_path", None),
                "is_dir": event.is_directory,
                "time": datetime.now()
            })

            # Start timer only for first event in batch
            if len(self.buffer) == 1:
                self.timer = threading.Timer(self.window_seconds, self.flush)
                self.timer.start()

    # ---------------- FLUSH ----------------
    def flush(self):

        with self.lock:
            if not self.buffer:
                return

            ready = list(self.buffer)
            self.buffer.clear()

        # Process outside lock
        self.processor.process_event_group(ready)

    # ---------------- WATCHDOG HOOKS ----------------
    def on_created(self, event):
        self.add_event("created", event)

    def on_deleted(self, event):
        self.add_event("deleted", event)

    def on_moved(self, event):
        self.add_event("moved", event)

    def on_modified(self, event):
        self.add_event("modified", event)