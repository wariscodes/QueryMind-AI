import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from google import genai
import sqlglot
from sqlglot import exp

from sql_validator import get_sql_operation, validate_sql


# Load settings from the project's existing .venv/.env file.
ENV_PATH = Path(__file__).parent / ".venv" / ".env"
load_dotenv(ENV_PATH)


def get_database_connection():
    """Connect to the configured MySQL database."""
    required_settings = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]

    for setting in required_settings:
        if os.getenv(setting) is None:
            raise ValueError(f"{setting} .env file mein nahi mila.")

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_database_schema():
    """Fetch actual table and column names from MySQL."""
    connection = None
    cursor = None

    try:
        db_name = os.getenv("DB_NAME")
        if not db_name:
            return False, "DB_NAME .env file mein nahi mila."

        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, ORDINAL_POSITION
            """,
            (db_name,),
        )

        rows = cursor.fetchall()
        if not rows:
            return False, f"Database '{db_name}' mein koi table nahi mila."

        schema_lines = []
        current_table = None
        for table_name, column_name, column_type in rows:
            if table_name != current_table:
                current_table = table_name
                schema_lines.append(f"\nTable: {table_name}")
            schema_lines.append(f"  {column_name} - {column_type}")

        return True, "\n".join(schema_lines).strip()

    except (mysql.connector.Error, ValueError) as error:
        return False, f"Database schema fetch failed: {error}"

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def generate_sql(question, schema=None):
    """Generate and validate one SELECT or conditional UPDATE query."""
    if not isinstance(question, str) or not question.strip():
        return False, "Please enter a question."

    if not isinstance(schema, str) or not schema.strip():
        success, result = get_database_schema()
        if not success:
            return False, result
        schema = result

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "GEMINI_API_KEY .venv/.env file mein nahi mili."

    prompt = f"""
You generate MySQL SELECT and UPDATE queries from natural-language requests.

Database schema:
{schema}

User request:
{question}

Rules:
- Generate exactly one SQL query.
- Allow SELECT for retrieving data.
- Allow UPDATE only when the user clearly asks to change existing data.
- Every UPDATE must have a specific WHERE condition identifying the intended row(s).
- Never use WHERE 1=1, WHERE TRUE, or an unconditional condition.
- Use only tables and columns from the supplied schema.
- Do not invent IDs, values, tables, or columns that are not supplied or present in the schema.
- Do not generate INSERT, DELETE, REPLACE, DROP, ALTER, CREATE, TRUNCATE,
  GRANT, CALL, or any other data/schema-changing command.
- Do not generate UPDATE with JOIN or FROM.
- Do not use SELECT INTO or locking SELECT clauses.
- If a request needs INSERT, DELETE, or a schema change, return exactly UNSUPPORTED_OPERATION.
- If the request is missing important information needed for a safe UPDATE,
  return exactly NEEDS_CLARIFICATION.
- Return SQL only, without Markdown fences or explanation.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        sql = response.text
        if not sql or not sql.strip():
            return False, "Gemini returned an empty response."

        sql = sql.strip()
        if sql.startswith("```"):
            lines = sql.splitlines()
            sql = "\n".join(
                line for line in lines if not line.strip().startswith("```")
            ).strip()

        marker = sql.upper().strip()
        if marker == "UNSUPPORTED_OPERATION":
            return False, (
                "This request is not supported yet. This version supports "
                "retrieving data and updating existing records only."
            )
        if marker == "NEEDS_CLARIFICATION":
            return False, (
                "I need more details to safely update the record. "
                "Please mention which record and what value should change."
            )

        is_valid, result = validate_sql(sql)
        if not is_valid:
            return False, result

        return True, result

    except Exception as error:
        return False, f"SQL generation failed: {error}"


def execute_sql(sql, confirm_update=False):
    """Execute SELECT immediately; execute UPDATE only after explicit confirmation."""
    connection = None
    cursor = None

    is_valid, normalized_sql = validate_sql(sql)
    if not is_valid:
        return False, normalized_sql

    operation = get_sql_operation(normalized_sql)
    if operation not in ("SELECT", "UPDATE"):
        return False, "Only SELECT and UPDATE queries can be executed."

    if operation == "UPDATE" and confirm_update is not True:
        return False, "UPDATE requires user confirmation before execution."

    try:
        statements = sqlglot.parse(normalized_sql, read="mysql")
        if len(statements) != 1 or statements[0] is None:
            return False, "Only one SQL statement is allowed."

        statement = statements[0]
        if operation == "SELECT" and not isinstance(statement, exp.Select):
            return False, "Invalid SELECT query."
        if operation == "UPDATE" and not isinstance(statement, exp.Update):
            return False, "Invalid UPDATE query."

        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute(normalized_sql)

        if operation == "SELECT":
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return True, {"operation": "SELECT", "columns": columns, "rows": rows}

        affected_rows = cursor.rowcount
        connection.commit()
        return True, {
            "operation": "UPDATE",
            "affected_rows": affected_rows,
        }

    except Exception as error:
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                pass
        return False, f"SQL execution failed: {error}"

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
