from datetime import datetime, timedelta
from typing import Any

from google.protobuf import timestamp

from app.database.db import SessionLocal
from app.database.models import FileInitiation, FileLifeCycle


def get_files_by_date_and_operation(
        start_date: str,
        end_date: str,
        event_type: str
) -> list[Any] | str:
    """
    Queries the database for files initialized/operated within a specific date range
    and returns their latest lifecycle state.

    Arguments:
    - start_date: 'YYYY-MM-DD'
    - end_date: 'YYYY-MM-DD'
    - event_type: str
    """

    db = SessionLocal()

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

        events = db.query(FileInitiation).filter(
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
                file_lifecycle_events = db.query(FileLifeCycle).filter(
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
                "current_file_name": lifecycle.current_name,
                "current_location": lifecycle.current_location,
                "latest_operation": lifecycle.file_operation,
                "timestamp": lifecycle.timestamp
            })

        if result:
            return result

        return "No files downloaded"

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        db.close()




from datetime import datetime, timedelta
from app.database.db import SessionLocal
from app.database.models import FileLifeCycle


def get_files_by_date_and_operation_for_rename_delete_move(
    start_date: str,
    end_date: str,
    event_type: str
) -> list[dict] | str:

    db = SessionLocal()

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

        events = db.query(FileLifeCycle).filter(
            FileLifeCycle.file_operation == event_type,
            FileLifeCycle.timestamp >= start,
            FileLifeCycle.timestamp < end
        ).all()

        if not events:
            return "No events found"

        latest_events = {}

        for e in events:
            if e.file_id in latest_events:
                continue

            latest_events[e.file_id] = (
                db.query(FileLifeCycle)
                .filter(FileLifeCycle.file_id == e.file_id)
                .order_by(FileLifeCycle.timestamp.desc())
                .first()
            )
        result = []

        for event in latest_events.values():
            result.append({
                "file_id": event.file_id,
                "current_file_name": event.current_name,
                "current_location": event.current_location,
                "latest_operation": event.file_operation,
                "timestamp": event.timestamp
            })
        return result

    except Exception as ex:
        return f"Error: {str(ex)}"

    finally:
        db.close()


def get_all_files_with_latest_state():
    db = SessionLocal()

    try:
        # Get latest lifecycle events first
        events = (
            db.query(FileLifeCycle)
            .order_by(FileLifeCycle.timestamp.desc())
            .all()
        )

        # Get files that have never been operated on
        initiated_files = (
            db.query(FileInitiation)
            .filter(FileInitiation.is_operated == False)
            .all()
        )

        latest_events = {}

        # Keep only the newest event per file_id
        for event in events:
            if event.file_id not in latest_events:
                latest_events[event.file_id] = event

        result = []

        # Add latest lifecycle states
        for event in latest_events.values():
            result.append({
                "file_id": event.file_id,
                "current_file_name": event.current_name,
                "current_location": event.current_location,
                "latest_operation": event.file_operation,
                "timestamp": event.timestamp
            })

        # Add files that have no lifecycle events yet
        for file in initiated_files:
            result.append({
                "file_id": file.id,
                "current_file_name": file.file_name,
                "current_location": file.file_path,
                "latest_operation": file.file_operation,
                "timestamp": file.timestamp
            })

        # Optional: sort everything by timestamp descending
        result.sort(key=lambda x: x["timestamp"], reverse=True)

        return result

    except Exception as ex:
        return f"Error: {str(ex)}"

    finally:
        db.close()



if __name__ == "__main__":
    result = get_all_files_with_latest_state()

    print(result)