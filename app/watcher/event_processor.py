# app/watcher/event_processor.py

from pathlib import Path
import os
from datetime import datetime


class EventProcessor:

    def __init__(self):
        self.recent_deletes = []
        self.temp_files = {}
        self.modified_cache = {}

    # ---------------- UTILITY ----------------
    def is_temp_file(self, path):
        filename = os.path.basename(path)
        return filename.endswith((".tmp", ".crdownload", ".part"))

    def get_download_path(self):
        return os.path.join(os.path.expanduser("~"), "Downloads")

    # ---------------- CREATED ----------------
    def process_created(self, path, is_directory, timestamp):

        downloads_path = self.get_download_path()

        # ❌ ignore temp files completely
        if self.is_temp_file(path):
            return

        # DOWNLOAD detection (final file in Downloads)
        if downloads_path in path:
            if self.temp_files:
                self.temp_files.clear()
                print(f"[{timestamp}] DOWNLOADED FILE COMPLETED: {path}")
                return

            print(f"[{timestamp}] DOWNLOADED FILE: {path}")
            return

        # Folder creation
        if is_directory:
            print(f"[{timestamp}] CREATED Folder: {path}")
            return

        # TEMP download start (extra safety)
        filename = os.path.basename(path)
        if filename.endswith((".tmp", ".crdownload", ".part")):
            self.temp_files[filename] = {
                "path": path,
                "time": timestamp
            }
            return



        # normal file creation
        print(f"[{timestamp}] CREATED FILE: {path}")

    # ---------------- DELETED ----------------
    def process_deleted(self, path, is_directory, timestamp):

        # ❌ ignore temp deletions
        if self.is_temp_file(path):
            return

        self.recent_deletes.append({
            "path": path,
            "name": os.path.basename(path),
            "timestamp": timestamp,
            "is_directory": is_directory
        })

        print(f"[{timestamp}] DELETED {'Folder' if is_directory else 'File'}: {path}")

    # ---------------- MOVED / RENAMED ----------------
    def process_moved(self, src_path, dest_path, is_directory, timestamp):

        # ❌ ignore temp file moves
        if self.is_temp_file(src_path) or self.is_temp_file(dest_path):
            return

        src_parent = str(Path(src_path).parent)
        dest_parent = str(Path(dest_path).parent)

        src_name = Path(src_path).name
        dest_name = Path(dest_path).name

        event_type = "Folder" if is_directory else "File"

        # RENAMED
        if src_parent == dest_parent:
            print(
                f"[{timestamp}] RENAMED {event_type}: "
                f"{src_name} -> {dest_name}"
            )
            return

        # MOVED
        print(
            f"[{timestamp}] MOVED {event_type}: "
            f"{src_path} -> {dest_path}"
        )

    # ---------------- MODIFIED ----------------
    def process_modified(self, path, is_directory, timestamp):

        # ignore folders
        if is_directory:
            return

        # ignore temp files
        if self.is_temp_file(path):
            return

        # debounce spam events
        last_time = self.modified_cache.get(path)

        now = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

        if last_time:
            diff = (now - last_time).total_seconds()
            if diff < 2:
                return

        self.modified_cache[path] = now

        print(f"[{timestamp}] MODIFIED FILE: {path}")