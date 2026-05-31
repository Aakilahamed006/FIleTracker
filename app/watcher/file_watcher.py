from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import traceback
import os
from datetime import datetime

from app.watcher.event_processor import EventProcessor


class FileActivityHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.processor = EventProcessor()

    def on_created(self, event):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.processor.process_created(
                event.src_path,
                event.is_directory,
                timestamp
            )

        except Exception as e:
            print("Error in created:", e)
            traceback.print_exc()

    def on_deleted(self, event):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.processor.process_deleted(
                event.src_path,
                event.is_directory,
                timestamp
            )

        except Exception as e:
            print("Error in deleted:", e)
            traceback.print_exc()

    def on_moved(self, event):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.processor.process_moved(
                event.src_path,
                event.dest_path,
                event.is_directory,
                timestamp
            )

        except Exception as e:
            print("Error in moved:", e)
            traceback.print_exc()

    def on_modified(self, event):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.processor.process_modified(
                event.src_path,
                event.is_directory,
                timestamp
            )

        except Exception as e:
            print("Error in modified:", e)
            traceback.print_exc()


def start_watching():

    event_handler = FileActivityHandler()

    username = os.getlogin()

    watch_paths = [
        fr"C:\Users\{username}\Desktop",
        fr"C:\Users\{username}\Documents",
        fr"C:\Users\{username}\Downloads",
        fr"C:\Users\{username}\Pictures",
    ]

    observers = []

    try:

        for path in watch_paths:

            if os.path.exists(path):

                observer = Observer()

                observer.schedule(
                    event_handler,
                    path,
                    recursive=True
                )

                observer.start()

                observers.append(observer)

                print(f"Watching: {path}")

        print("\nMonitoring started...\n")

        while True:
            time.sleep(1)

    except Exception as e:

        print("Observer crashed:", e)
        traceback.print_exc()

    finally:

        for observer in observers:
            observer.stop()

        for observer in observers:
            observer.join()

        print("Observers stopped")


if __name__ == "__main__":
    start_watching()