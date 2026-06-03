from app.database.db import SessionLocal
from app.database.models import FileInitiation
from app.database.file_repository_helpers import FileRepositoryHelpers


class FileRepository:

    def __init__(self):
        self.db = SessionLocal()
        self.helpers = FileRepositoryHelpers(self.db)

    # -----------------------------------
    # FILE CREATION
    # -----------------------------------

    def create_file(self, file_name, file_extension, file_path, timestamp, is_operated=False, file_operation="created"):
        existing = self.helpers.get_file_by_path(file_path)
        if existing:
            return existing

        record = FileInitiation(
            file_name=file_name,
            file_extension=file_extension,
            file_path=file_path,
            timestamp=timestamp,
            is_operated=is_operated,
            file_operation=file_operation
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    def create_folder(self, file_name, file_extension, file_path, timestamp, is_operated=False):
        return self.create_file(
            file_name=file_name,
            file_extension=file_extension,
            file_path=file_path,
            timestamp=timestamp,
            is_operated=is_operated,
            file_operation="created"
        )

    # -----------------------------------
    # EVENT LOGGING
    # -----------------------------------

    def add_event(self, file_id, operation, location, name, timestamp, dest=None):
        if operation == "deleted":
            file_id = self.helpers.resolve_file_id(file_id, location)
            if file_id is None:
                return None

            if not self.helpers.cascade_delete_initiation(location):
                return None

            if not self.helpers.cascade_delete_lifecycle(location):
                return None

            return self.helpers.save_event_record_in_file_life_cycle(file_id, operation, location, name, timestamp)

        if operation == "renamed" :

            event=self.helpers.get_file_by_path(location)

            file_id=self.helpers.resolve_file_id(file_id, location)
            if file_id is not None:
                self.helpers.set_file_operated_true_in_file_initiation(file_id)
            if event is None or not event.file_operation == "deleted":
                event=self.helpers.get_latest_file_by_path_life_cycle(location)
                file_id=event.file_id

            events=self.helpers.get_files_by_parent_path_file_life_cycle(location)
            for event in events:
                event.current_location=self.helpers.update_the_child_path(event.current_location, location,dest)
                self.helpers.save_event_record_in_file_life_cycle(event.file_id, event.operation,event.current_location, event.timestamp)

            return self.helpers.save_event_record_in_file_life_cycle(file_id, operation, dest, name, timestamp)

        print("methods not implemented")
        return None