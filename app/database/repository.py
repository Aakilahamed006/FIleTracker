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
            event = self.helpers.get_file_by_path(location)
            print("Entering deleted event")
            if event is not None:
                file_id=event.id

            if file_id is not None:
                self.helpers.set_file_operated_true_in_file_initiation(file_id)

            if event is None  :     #or  event.file_operation == "deleted":
                event=self.helpers.get_latest_file_by_path_life_cycle(location)
                file_id=event.file_id

            return self.helpers.save_event_record_in_file_life_cycle(file_id, operation, location, name, timestamp)


        if operation == "renamed" :

            event=self.helpers.get_file_by_path(location)

            file_id=self.helpers.resolve_file_id(file_id, location)

            if file_id is not None:
                self.helpers.set_file_operated_true_in_file_initiation(file_id)
            if event is None  :     #or  event.file_operation == "deleted":
                event=self.helpers.get_latest_file_by_path_life_cycle(location)
                file_id=event.file_id

            life_cycle_events=self.helpers.get_files_by_parent_path_file_life_cycle(location)

            if life_cycle_events is not None:
              for event in life_cycle_events:
                event.current_location=self.helpers.update_the_child_path(event.current_location, location,dest)
                self.helpers.save_event_record_in_file_life_cycle(event.file_id, "Path modified due renaming of parent file",event.current_location,event.current_name, event.timestamp)

            if not life_cycle_events:
              file_initiation_events = self.helpers.get_files_by_parent_path(location)
              if file_initiation_events is not None:
                for event in file_initiation_events:
                 self.helpers.set_file_operated_true_in_file_initiation(event.id)
                 event.file_path=self.helpers.update_the_child_path(event.file_path, location,dest)
                 print ("event file_path:"+event.file_path)
                 print ("event file_id:",event.id)
                 self.helpers.save_event_record_in_file_life_cycle(event.id, "Path modified due renaming of parent file",event.file_path,event.file_name, event.timestamp)

            return self.helpers.save_event_record_in_file_life_cycle(file_id, operation, dest, name, timestamp)

        if operation =="downloaded":
            try:
                file_extension = location.suffix.lstrip(".")
            except Exception:
                file_extension = ""
            self.helpers.save_event_record_in_file_initiation(location,name,timestamp,"downloaded",file_extension)


        print("methods not implemented")
        return None