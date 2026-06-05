from app.database.models import FileInitiation, FileLifeCycle


class FileRepositoryHelpers:

    def __init__(self, db):
        self.db = db

    # -----------------------------------
    # PRIVATE HELPERS
    # -----------------------------------

    def resolve_file_id(self, file_id, location):
        if file_id is not None:
            return file_id

        file_record = self.get_file_by_path(location)

        if file_record is None:
            print("⚠️ File not tracked:", location)
            return None

        file_record.is_operated = True
        try:
            self.db.add(file_record)
            print("Flagged to operated is true")
        except:
            self.db.rollback()
            print("saving Failed")

        return file_record.id



    def save_event_record_in_file_life_cycle(self, file_id, operation, location, name, timestamp, ):
        record = FileLifeCycle(
            file_id=file_id,
            file_operation=operation,
            current_location=location,
            current_name=name,
            timestamp=timestamp
        )
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

            print(f"✔ Event saved: {operation} -> {location}")
            return record

        except Exception as e:
            self.db.rollback()
            print(f"❌ DB error while saving event: {e}")
            return None

    def save_event_record_in_file_initiation(self, location, name, timestamp,file_operation,file_extension):
        record = FileInitiation(
            file_path=location,
            file_name=name,
            is_operated=False,
            file_operation=file_operation,
            file_extension=file_extension if file_extension else "",
            timestamp=timestamp

        )
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

            print("Downloaded records saved successfully")
        except Exception as e:
            self.db.rollback()
            print("Error while saving event: {e}")
            return e

    # -----------------------------------
    # QUERIES
    # -----------------------------------

    def get_file_by_path(self, path):
        return self.db.query(FileInitiation).filter(
            FileInitiation.file_path == path
        ).first()

    def get_latest_file_by_path_life_cycle (self, path):
        return (self.db.query(FileLifeCycle).filter(
            FileLifeCycle.current_location == path
        ).order_by(FileLifeCycle.timestamp.desc())
                .first())

    def get_files_by_parent_path(self, parent_path):
        parent_path = parent_path.rstrip("\\") + "\\"

        records = self.db.query(FileInitiation).filter(
            FileInitiation.file_path.startswith(parent_path)
        ).all()

        latest_records = {}

        for record in records:
            if (
                    record.id not in latest_records
                    or record.timestamp > latest_records[record.id].timestamp
            ):
                latest_records[record.id] = record

        return list(latest_records.values())


    def get_files_by_parent_path_file_life_cycle(self, parent_path):
        parent_path = parent_path.rstrip("\\") + "\\"

        records = self.db.query(FileLifeCycle).filter(
            FileLifeCycle.current_location.startswith(parent_path)
        ).all()

        latest_records = {}

        for record in records:
            if (
                    record.file_id not in latest_records
                    or record.timestamp > latest_records[record.file_id].timestamp
            ):
                latest_records[record.file_id] = record

        return list(latest_records.values())



    def close(self):
        self.db.close()

    def get_latest_event_by_file_id(self, file_id):
        return (
            self.db.query(FileLifeCycle)
            .filter(FileLifeCycle.file_id == file_id)
            .order_by(FileLifeCycle.timestamp.desc())
            .first()
        )
    def set_file_operated_true_in_file_initiation (self,location):
        self.db.query(FileInitiation).filter(
            FileInitiation.file_path == location
        ).update({"file_operation": True})
        self.db.commit()


    def update_the_child_path(self,current_path, old_path, new_path):
        """
        Returns updated path if it is inside the renamed folder.
        Otherwise returns original path.
        """

        if current_path and current_path.startswith(old_path):
            return current_path.replace(old_path, new_path, 1)

        return current_path

    def set_file_operated_true_in_file_initiation_by_file_id(self, file_id):
        self.db.query(FileInitiation).filter(
            FileInitiation.id == file_id
        ).update({"is_operated": True})
        self.db.commit()