from fastmcp import FastMCP
from sqlalchemy import result_tuple

from app.main import app


# Create MCP server from FastAPI app
mcp = FastMCP.from_fastapi(
    app=app,
    name="File Tracker AI Assistant"
)


@mcp.tool()
def get_files_by_date_and_operation_like_created_and_downloaded(
        start_date: str,
        end_date: str,
        operation: str
) -> str:
    print("TOOL EXECUTED")
    """
    Retrieves files for a given operation within a date range.

    Arguments:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    - operation:
        created
        downloaded


    IMPORTANT:
    If the user asks about a single day (today, yesterday, etc.),
    pass the same date for both start_date and end_date.
    """

    from app.database.mcp_helper_funtions import (
        get_files_by_date_and_operation
    )

    rows = get_files_by_date_and_operation(
        start_date=start_date,
        end_date=end_date,
        event_type=operation
    )

    if not rows:
        return (
            f"No files found between "
            f"{start_date} and {end_date} "
            f"for operation '{operation}'."
        )

    result = (
        f"Files found between {start_date} and "
        f"{end_date} for operation '{operation}':\n\n"
    )

    for row in rows:
        result += (
            f"file_id: {row['file_id']}\n"
            f"current_file_name: {row['current_file_name']}\n"
            f"current_location: {row['current_location']}\n"
            f"latest_operation: {row['latest_operation']}\n"
            f"Timestamp: {row['timestamp']}\n"
            f"-----------------------------------\n"
        )

    return result


@mcp.tool()
def get_files_by_date_and_operation_for_rename_delete_move(
        start_date: str,
        end_date: str,
        operation: str
) -> str:
    print("TOOL EXECUTED")
    """
    Retrieves files for a given operation within a date range.

    Arguments:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    - operation:
        moved
        renamed
        deleted


    IMPORTANT:
    If the user asks about a single day (today, yesterday, etc.),
    pass the same date for both start_date and end_date.
    """

    from app.database.mcp_helper_funtions import (
        get_files_by_date_and_operation_for_rename_delete_move
    )

    rows = get_files_by_date_and_operation_for_rename_delete_move(
        start_date=start_date,
        end_date=end_date,
        event_type=operation
    )

    if not rows:
        return (
            f"No files found between "
            f"{start_date} and {end_date} "
            f"for operation '{operation}'."
        )

    result = (
        f"Files found between {start_date} and "
        f"{end_date} for operation '{operation}':\n\n"
    )

    for row in rows:
        result += (
            f"file_id: {row['file_id']}\n"
            f"current_file_name: {row['current_file_name']}\n"
            f"current_location: {row['current_location']}\n"
            f"latest_operation: {row['latest_operation']}\n"
            f"Timestamp: {row['timestamp']}\n"
            f"-----------------------------------\n"
        )

    return result


if __name__ == "__main__":
    mcp.run()