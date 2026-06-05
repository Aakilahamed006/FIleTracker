from sqlalchemy import inspect
from app.database.db import engine

def get_database_schema():

    print("FUNCTION CALLED")

    inspector = inspect(engine)

    tables = inspector.get_table_names()

   # print("TABLES:", tables)# you can uncomment the case of debugging

    if not tables:
        return "No tables found in database"

    schema_text = ""

    for table in tables:
        schema_text += f"\nTABLE: {table}\n"

        columns = inspector.get_columns(table)

        for column in columns:
            schema_text += f"- {column['name']} ({column['type']})\n"

        foreign_keys = inspector.get_foreign_keys(table)

        if foreign_keys:
            schema_text += "RELATIONSHIPS:\n"
            for fk in foreign_keys:
                schema_text += (
                    f"- {fk['constrained_columns']} -> "
                    f"{fk['referred_table']}({fk['referred_columns']})\n"
                )

    #print("SCHEMA GENERATED:\n", schema_text) #uncomment this to see the entire databse schema

    return schema_text

if __name__ == "__main__":
    get_database_schema()