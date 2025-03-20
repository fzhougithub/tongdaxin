import psycopg2
import argparse
from datetime import datetime

def get_max_day(conn, symbol: str) -> datetime.date:
    """Get the latest day for a symbol in stockhistory."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MAX(day) 
            FROM stock.stockhistory 
            WHERE symbol = %s
        """, (symbol,))
        result = cur.fetchone()[0]
        return result if result else datetime.min.date()

def update_stockhistory(file_path: str, symbol: str):
    """Update stockhistory with new records from a CSV file based on max day."""
    # Database connection
    conn = psycopg2.connect('postgresql://pfchart:pfchart1@localhost:5432/fzhou')
    cur = conn.cursor()

    try:
        # Get the latest date in the table
        max_day = get_max_day(conn, symbol)
        print(f"Latest date in table for {symbol}: {max_day}")

        # Read CSV and filter new records
        new_rows = []
        with open(file_path, 'r') as f:
            for line in f:
                symbol_csv, day_str, o, h, l, c, amount, v, last = line.strip().split(',')
                day = datetime.strptime(day_str, '%Y-%m-%d').date()  # Adjust format as needed
                if day > max_day:  # Only include records after max_day
                    new_rows.append((
                        symbol_csv, day, float(o), float(h), float(l), float(c), 
                        float(amount), int(v), float(last)
                    ))

        # Insert new records in batches
        if new_rows:
            cur.executemany("""
                INSERT INTO stock.stockhistory (symbol, day, o, h, l, c, amount, v, last)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, day) DO NOTHING
            """, new_rows)
            print(f"Inserted {len(new_rows)} new records for {symbol}.")
        else:
            print(f"No new records found for {symbol} after {max_day}.")

        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error processing file: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update stockhistory with new records from CSV.")
    parser.add_argument("symbol", help="Stock symbol (e.g., '600050')")
    parser.add_argument("file_path", help="Path to CSV file (e.g., '/var/tellme/stock/sh/sh600050.day')")
    args = parser.parse_args()

    update_stockhistory(args.file_path, args.symbol)
