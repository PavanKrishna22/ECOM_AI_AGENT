import sqlite3

DB_FILE = "ecommerce.db"

def print_database_schema():
    """Connects to the database and prints the schema of all tables."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"--- Schema for database: {DB_FILE} ---")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        for table in tables:
            table_name = table[0]
            print(f"\nTable: '{table_name}'")
            print("-" * (len(table_name) + 9))
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"{'Column Name':<25} | {'Data Type'}")
            print("-" * 40)
            for col in columns:
                # col schema: (id, name, type, notnull, default_value, pk)
                print(f"{col[1]:<25} | {col[2]}")

        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Please ensure the '{DB_FILE}' file exists in the same directory.")

if __name__ == "__main__":
    print_database_schema()