from watchdog.observers import Observer
from app.database.models import Base
from app.database.repository import FileRepository
from app.database.db import engine
from app.watcher.buffer_handler import BufferHandler
import time


def start_watching():

    Base.metadata.create_all(bind=engine)

    repo = FileRepository()
    handler = BufferHandler(repo=repo)

    observer = Observer()

    watch_paths = handler.get_watch_paths()

    for path in watch_paths:
        observer.schedule(handler, path, recursive=True)

    observer.start()

    print("Watching started...")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_watching()
