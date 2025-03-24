import argparse
import psycopg2
import os
from datetime import datetime

def create_table(conn, table_name):
    """Creates a stock data table in PostgreSQL if it doesn't exist."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    symbol VARCHAR(50),
                    day DATE,
                    o FLOAT,
                    h FLOAT,
                    l FLOAT,
                    c FLOAT,
                    amount FLOAT,
                    v INTEGER,
                    PRIMARY KEY (symbol, day) -- Unique constraint on symbol and day
                );
            """)
            conn.commit()
            print(f"Table '{table_name}' is ready.")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        conn.rollback()

def load_stock_data(postgres_uri, database_name, table_name, input_file):
    """Loads stock data into a PostgreSQL table, adding 'symbol' and converting to schema."""

    conn = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(postgres_uri)
        # Ensure the table exists
        create_table(conn, table_name)

        # Extract symbol from filename (e.g., "TK2023.txt" -> "TK")
        base_name = os.path.basename(input_file)
        try:
            symbol = base_name[2:-4]
            if not symbol:
                raise ValueError("Symbol is empty")
        except (IndexError, ValueError):
            print(f"Warning: Invalid filename format: {base_name}. Skipping file.")
            return

        with open(input_file, 'r') as file:
            with conn.cursor() as cur:
                for line in file:
                    try:
                        date_str, o, h, l, c, amount, v, unknown = line.strip().split()

                        # Convert date string to datetime object
                        try:
                            day = datetime.strptime(str(date_str), "%Y%m%d")
                        except ValueError:
                            print(f"Warning: Invalid date format: {date_str}. Skipping line")
                            continue

                        # Prepare data for insertion
                        data = (
                            symbol,
                            day,
                            float(o),
                            float(h),
                            float(l),
                            float(c),
                            float(amount),
                            int(v)
                        )

                        # Insert into PostgreSQL table
                        cur.execute(f"""
                            INSERT INTO {table_name} (symbol, day, o, h, l, c, amount, v)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, day) DO NOTHING;
                        """, data)

                    except ValueError:
                        print(f"Warning: Could not convert data in line: {line.strip()}. Skipping.")
                    except psycopg2.Error as e:
                        print(f"Database error inserting data: {e}. Skipping line.")
                        conn.rollback()  # Roll back on error
                    else:
                        conn.commit()  # Commit each successful insert

        print(f"Data from '{input_file}' loaded into '{database_name}.{table_name}' with symbol '{symbol}'")

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL or executing query: {e}")
    except Exception as e:
        print(f"A general error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load stock data into PostgreSQL.")
    parser.add_argument("postgres_uri", help="PostgreSQL connection URI (e.g., 'postgresql://user:password@localhost:5432/dbname')")
    parser.add_argument("database_name", help="Database name (for reference)")
    parser.add_argument("table_name", help="Table name")
    parser.add_argument("input_file", help="Input file path")

    args = parser.parse_args()

    load_stock_data(args.postgres_uri, args.database_name, args.table_name, args.input_file)
