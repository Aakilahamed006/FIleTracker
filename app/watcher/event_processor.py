import os
from pathlib import Path


class EventProcessor:

    def __init__(self, repo=None):
        self.repo = repo
        self.known_files = set()

    # ----------------------------------
    # NOISE FILTER
    # ----------------------------------
    def is_noise_event(self, path):
        filename = os.path.basename(path)

        ignored_folders = [
            ".idea", ".git", ".vscode",
            "__pycache__", "node_modules",
            ".venv", "venv",
            ".gradle", ".cxx", "build",
            "target", "dist",
            ".pytest_cache"
            ,"tracker.db-journal",
            "database"
        ]

        if any(folder in path for folder in ignored_folders):
            return True

        if (
            filename.startswith("~$")
            or filename.endswith("~")
            or filename.endswith(".tmp")
            or filename.endswith(".TMP")
            or filename.endswith(".crdownload")
            or filename.endswith(".part")
            or filename.endswith(".db")
            or filename.endswith(".sqlite")
            or filename.endswith(".sqlite3")
        ):
            return True

        return False

    # ----------------------------------
    # DOWNLOAD CHECK
    # ----------------------------------
    def is_download_path(self, path):
        downloads_path = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )
        return path.startswith(downloads_path)

    # ----------------------------------
    # DB CALL SAFETY WRAPPERS
    # ----------------------------------
    def safe_create_folder(self, path, time):
        if not self.repo:
           # print("[DEBUG] safe_create_folder: repo is None")
            return
           #print(f"[DEBUG] safe_create_folder called for: {path}")
        try:
            folder_name = Path(path).name
            return self.repo.create_folder(
                file_name=folder_name,
                file_extension="",
                file_path=path,
                timestamp=time,
                is_operated=False
            )
        except Exception as e:
            print(f"[ERROR] safe_create_folder failed for {path}: {e}")

    def safe_create_file(self, path, time):
        if not self.repo:
            #print("[DEBUG] safe_create_file: repo is None")
            return
        #   print(f"[DEBUG] safe_create_file called for: {path}")
        try:
            file_name = Path(path).name
            file_extension = Path(path).suffix.lstrip(".")
            return self.repo.create_file(
                file_name=file_name,
                file_extension=file_extension,
                file_path=path,
                timestamp=time,
                is_operated=False
            )
        except Exception as e:
            print(f"[ERROR] safe_create_file failed for {path}: {e}")

    def safe_add_event(self, operation, path,name, time, dest=None):
        if not self.repo:
            return
        try:
            self.repo.add_event(
                file_id=None,
                operation=operation,
                location=path,
                name=name,
                timestamp=time,
                dest=dest
            )
        except Exception as e:
            print(f"[ERROR] safe_add_event failed for {path}: {e}")

    # ----------------------------------
    # MAIN PROCESSOR
    # ----------------------------------
    def process_event_group(self, events):

        filtered_events = []

        for event in events:
            if self.is_noise_event(event["path"]):
                continue
            if event.get("dest") and self.is_noise_event(event["dest"]):
                continue
            filtered_events.append(event)

        if not filtered_events:
            return

        print("\n========== EVENT GROUP ==========")

        skip_indexes = set()
        downloaded_files = set()

        # =====================================================
        # MOVE DETECTION (DELETE + CREATE pairs)
        # =====================================================
        for i, event1 in enumerate(filtered_events):

            if event1["type"] != "deleted":
                continue

            deleted_path = event1["path"]
            deleted_name = Path(deleted_path).name
            deleted_is_dir = event1.get("is_dir", False)

            for j, event2 in enumerate(filtered_events):

                if j <= i:
                    continue

                if event2["type"] != "created":
                    continue

                created_path = event2["path"]
                created_name = Path(created_path).name
                created_is_dir = event2.get("is_dir", False)

                # -------------------------------
                # FILE MOVE (strict match)
                # -------------------------------
                if not deleted_is_dir:
                    if deleted_name == created_name:
                        print(
                            f"{event1['time']} MOVED FILE:\n"
                            f"    FROM: {deleted_path}\n"
                            f"    TO  : {created_path}"
                        )

                        self.safe_add_event(
                            "moved",
                            deleted_path,
                            event1["time"],
                            created_path
                        )

                        skip_indexes.add(i)
                        skip_indexes.add(j)
                        break

                # -------------------------------
                # DIRECTORY MOVE (looser match)
                # -------------------------------
                else:
                    # directories often rename/move together → allow any match
                    print(
                        f"{event1['time']} MOVED DIR:\n"
                        f"    FROM: {deleted_path}\n"
                        f"    TO  : {created_path}"
                    )

                    self.safe_add_event(
                        "moved",
                        deleted_path,
                        event1["time"],
                        created_path
                    )

                    skip_indexes.add(i)
                    skip_indexes.add(j)
                    break

        # =====================================================
        # PROCESS REMAINING EVENTS
        # =====================================================
        skip_next = False
        for i, event in enumerate(filtered_events):

            if i in skip_indexes:
                continue
            if skip_next:
                skip_next = False
                continue
            path = event["path"]

            # ----------------------------------
            # FILE / FOLDER CREATION (ONLY ONCE)
            # ----------------------------------

            if event["type"] == "created":



                if path not in self.known_files:
                    self.known_files.add(path)
                    #print(f"[DEBUG] is_dir value: {event.get('is_dir')} | path: {path}")

                    if event.get("is_dir"):
                        print(f"{event['time']} CREATED DIR: {path}")
                        self.safe_create_folder(path, event["time"])
                        skip_next = True
                    else:
                        print(f"{event['time']} CREATED: {path}")
                        self.safe_create_file(path, event["time"])
                        skip_next = True
                continue

            # ----------------------------------
            # RENAME / MOVE
            # ----------------------------------
            if event["type"] == "moved":

                dest = event.get("dest")
                if not dest:
                    continue

                src_parent = str(Path(path).parent)
                dest_parent = str(Path(dest).parent)

                if src_parent == dest_parent:
                    print(
                        f"{event['time']} RENAMED:\n"
                        f"    {path} -> {dest}"
                    )
                    name = Path(dest).name
                    print(name)
                    # FIX: pass original `path` as location, not `dest`
                    self.safe_add_event(
                        "renamed",
                        path,
                        name,
                        event["time"],
                        dest
                    )
                    continue

                ##print(
                    f"{event['time']} MOVED:\n"
                    f"    {path} -> {dest}"
               # )
                #self.safe_add_event(
                    "moved",
                    path,
                    event["time"],
                    dest
                #)
                #continue

            # ----------------------------------
            # DOWNLOAD
            # ----------------------------------
            if (
                event["type"] == "modified"
                and not event.get("is_dir", False)
                and self.is_download_path(path)
            ):
                if path in downloaded_files:
                    continue

                downloaded_files.add(path)
                print(f"{event['time']} DOWNLOADED: {path}")
                self.safe_add_event(
                    "downloaded",
                    path,
                    event["time"]
                )
                continue

            # ----------------------------------
            # DELETE
            # ----------------------------------
            if event["type"] == "deleted":

                if skip_next:
                    skip_next = False
                    continue
                print(f"{event['time']} DELETED: {path}")
                name = Path(path).name
                self.safe_add_event(
                    "deleted",
                    path,
                    name,
                    event["time"]
                )
                skip_next = True
                continue

            # ----------------------------------
            # MODIFIED
            # ----------------------------------
            if event["type"] == "modified":
                print(f"{event['time']} MODIFIED: {path}")
                name = Path(path).name
                self.safe_add_event(
                    "modified",
                    path,
                    name,
                    event["time"]
                )
                continue

        print("=================================\n")
