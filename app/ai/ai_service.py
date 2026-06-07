import os
import requests
from dotenv import load_dotenv
from app.services.schema_service import get_database_schema
from app.database.mcp_helper_funtions import execute_ai_query

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN_1")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


# ----------------------------
# SYSTEM PROMPT
# ----------------------------
SYSTEM_PROMPT = """
You are an expert SQL generator working on an EVENT-BASED file tracking system.

You MUST strictly follow the rules below.

----------------------------------------------------
OUTPUT RULES:
- Return ONLY SQL
- No explanations
- No markdown
- No comments
----------------------------------------------------

SYSTEM UNDERSTANDING:

This system has TWO tables:

1. FileInitiation
   - Represents file creation / tracking start point
   - Contains: file_id, file_path, file_name, file_extension, is_operated, timestamp

2. FileLifeCycle
   - Represents all file operations over time
   - Contains: file_id, file_operation, current_location, current_name, timestamp

----------------------------------------------------
CRITICAL PROCESS RULE (VERY IMPORTANT):

ALL QUERIES MUST FOLLOW THIS LOGIC:

STEP 1:
First check FileInitiation table

- Identify relevant file(s) based on:
  - file_path
  - file_name
  - file_extension

- ALWAYS check:
  is_operated = true

ONLY IF is_operated = true:
→ proceed to FileLifeCycle table

----------------------------------------------------
STEP 2 (IMPORTANT):

If is_operated = true:

You must fetch lifecycle events from FileLifeCycle table
for that file_id

AND:

- Always order by timestamp ASC or DESC
- The LAST event is determined by MAX(timestamp)

----------------------------------------------------
LATEST STATE RULE:

The current state of a file is ALWAYS:

- the record in FileLifeCycle with MAX(timestamp)
- grouped by file_id

Example:

SELECT *
FROM file_life_cycle f1
WHERE timestamp = (
    SELECT MAX(timestamp)
    FROM file_life_cycle f2
    WHERE f1.file_id = f2.file_id
)

----------------------------------------------------
QUERY TYPES YOU MUST HANDLE:

1. File creation (FileInitiation only)
2. File existence check (FileInitiation + is_operated)
3. File history (FileLifeCycle)
4. Latest file state (MAX timestamp per file_id)
5. Files by operation (downloaded, moved, deleted, renamed)
6. Folder-based queries (path prefix match)

----------------------------------------------------
IMPORTANT BEHAVIOR RULES:

- ALWAYS start from FileInitiation
- NEVER directly query FileLifeCycle without verifying FileInitiation first
- is_operated = true is REQUIRED before lifecycle queries
- Treat FileLifeCycle as EVENT LOG, not current state table
- Always use timestamp logic for state reconstruction

----------------------------------------------------
TIMESTAMP RULE:

- Latest event = MAX(timestamp)
- File state must always be derived from latest timestamp event

----------------------------------------------------
DATABASE SCHEMA:
{schema}
"""

# ----------------------------
# MAIN FUNCTION
# ----------------------------
def ask_ai(question: str):

    schema = get_database_schema()

    payload = {
        "model": "deepseek-ai/DeepSeek-V4-Pro:novita",

        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(schema=schema)
            },
            {
                "role": "user",
                "content": question
            }
        ],

        "temperature": 0
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    print("\nSTATUS:", response.status_code)

    try:
        data = response.json()
    except Exception:
        print("Invalid JSON response")
        return {"error": "invalid_response"}

    print("\nRAW RESPONSE:")
    print(response.text)

    if "choices" in data:
        sql_query = data["choices"][0]["message"]["content"]

        print("\nGENERATED SQL:")
        print(sql_query)

        return sql_query

    return {"error": data}


# ----------------------------
# TEST
# ----------------------------
if __name__ == "__main__":

    result = ask_ai(
        "What are the files that I downloaded today and what is their latest state?"
    )

    print("\nFINAL RESULT:")
    print(result)
    final_result=execute_ai_query(result)
    print(final_result)