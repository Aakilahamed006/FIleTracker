from datetime import datetime, timedelta

from app.database.models import FileInitiation, FileLifeCycle


def get_files_by_date_and_operation(
        self,
        start_date: str,
        end_date: str,
        event_type: str
) -> list:
    """
    Queries the database for files initialized/operated within a specific date range
    and returns their latest lifecycle state.

    Arguments:
    - start_date: 'YYYY-MM-DD'
    - end_date: 'YYYY-MM-DD'
    - event_type: str
    """

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    events = self.db.query(FileInitiation).filter(
        FileInitiation.file_operation == event_type,
        FileInitiation.timestamp >= start,
        FileInitiation.timestamp < end
    ).all()

    inited_list = []
    temp_events = {}

    for event in events:

        # File has never been operated on
        if not event.is_operated:
            inited_list.append(event)

        # File has lifecycle events
        else:
            file_lifecycle_events = self.db.query(FileLifeCycle).filter(
                FileLifeCycle.file_id == event.id
            ).all()

            for lifecycle in file_lifecycle_events:

                # Keep only the latest lifecycle event per file
                if (
                    lifecycle.file_id not in temp_events
                    or lifecycle.timestamp >
                    temp_events[lifecycle.file_id].timestamp
                ):
                    temp_events[lifecycle.file_id] = lifecycle

    result = []

    # Files that were never operated on
    for event in inited_list:
        result.append({
            "file_id": event.id,
            "file_name": event.file_name,
            "location": event.file_path,
            "operation": event.file_operation,
            "timestamp": event.timestamp
        })

    # Latest lifecycle state of operated files
    for lifecycle in temp_events.values():
        result.append({
            "file_id": lifecycle.file_id,
            "file_name": lifecycle.current_name,
            "location": lifecycle.current_location,
            "operation": lifecycle.file_operation,
            "timestamp": lifecycle.timestamp
        })

    return result