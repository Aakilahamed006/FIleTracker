from fastmcp import FastMCP
from app.main import app

# Create an MCP server directly FROM your FastAPI app
mcp = FastMCP.from_fastapi(
    app=app,
    name="File Tracker AI Assistant"
)


# Overriding or adding explicit documentation for the LLM agent
@mcp.tool()
def get_downloaded_files(start_date: str, end_date: str) -> str:
    """
    Retrieves files downloaded within a specific date range or on a specific single day.

    Arguments:
    - start_date: The beginning of the date range (Format: 'YYYY-MM-DD').
    - end_date: The end of the date range (Format: 'YYYY-MM-DD').
                 CRITICAL: If the user asks for a single day (e.g., 'yesterday' or 'today'),
                 you must pass the exact same date to BOTH start_date and end_date.
    """
    # Reuses your database query logic
    from app.database import query_downloads

    rows = query_downloads(start_date, end_date)
    if not rows:
        return f"No files found for the requested timeframe ({start_date} to {end_date})."

    result = f"Here are the files found from {start_date} to {end_date}:\n"
    for row in rows:
        result += f"- {row[0]} (Downloaded: {row[1]})\n"
    return result


if __name__ == "__main__":
    mcp.run()