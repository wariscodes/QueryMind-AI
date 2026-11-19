import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


env_path = Path(__file__).parent / ".venv" / ".env"
load_dotenv(env_path)

connection = None

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

    print("MySQL connection successful!")
    print("Database:", connection.database)

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for row in tables:
        table_name = row[0]
        print(f"\nTable: {table_name}")

        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        columns = cursor.fetchall()

        for column in columns:
            print(f"  {column[0]} - {column[1]}")

    cursor.close()

except mysql.connector.Error as error:
    print("MySQL error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
