import pandas as pd
import sqlite3

# Define the database file
DB_FILE = "ecommerce.db"

# Define the CSV files and their corresponding table names
CSV_FILES = {
    "ad_sales": "Product-Level Ad Sales and Metrics.csv",
    "eligibility": "Product-Level Eligibility Table.csv",
    "total_sales": "Product-Level Total Sales and Metrics.csv"
}

def create_database():
    """
    Reads data from CSV files and loads it into a SQLite database.
    """
    # Connect to the SQLite database (this will create the file if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    print(f"Database '{DB_FILE}' created/connected.")

    # Load each CSV into a new table
    for table_name, file_name in CSV_FILES.items():
        try:
            df = pd.read_csv(file_name)
            # Clean up column names (remove spaces and convert to lowercase)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Table '{table_name}' created and data loaded from '{file_name}'.")
        except FileNotFoundError:
            print(f"Error: The file '{file_name}' was not found. Please make sure it's in the same directory.")
        except Exception as e:
            print(f"An error occurred with {file_name}: {e}")

    # Close the connection
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    create_database()