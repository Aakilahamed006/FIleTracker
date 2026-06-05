from sqlalchemy import text
from app.database.db import SessionLocal


def execute_ai_query(sql_query: str) -> dict | list:

    db = SessionLocal()

    try:
        sql = sql_query.strip()
        query_type = sql.split()[0].lower()

        forbidden = ["delete", "update", "insert", "create", "drop", "alter"]

        if query_type in forbidden:
            return {"error": f"{query_type.upper()} operations are not allowed."}

        if any(word in sql.lower() for word in forbidden):
            return {"error": "Forbidden SQL operation detected."}

        # -------------------------
        # FIX IS HERE
        # -------------------------
        result = db.execute(text(sql))

        # SELECT results
        if result.returns_rows:
            return [dict(row._mapping) for row in result.fetchall()]

        db.commit()
        return {"message": "Query executed successfully"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()

if __name__ == "__main__":

    sql_query = """
    WITH downloaded_today AS (
        SELECT DISTINCT flc.file_id
        FROM file_initiation_table fit
        INNER JOIN file_life_cycle flc 
            ON fit.id = flc.file_id
        WHERE fit.is_operated = true
          AND fit.file_operation = "downloaded"
          AND DATE(flc.timestamp) = CURRENT_DATE
    ),
    latest_state AS (
        SELECT flc.file_id, MAX(flc.timestamp) AS max_ts
        FROM file_life_cycle flc
        WHERE flc.file_id IN (SELECT file_id FROM downloaded_today)
        GROUP BY flc.file_id
    )
    SELECT 
        flc.file_id,
        flc.current_location,
        flc.current_name,
        flc.file_operation,
        flc.timestamp
    FROM file_life_cycle flc
    JOIN latest_state ls 
        ON flc.file_id = ls.file_id 
       AND flc.timestamp = ls.max_ts;
    """

    final_result = execute_ai_query(sql_query)
    print(final_result)