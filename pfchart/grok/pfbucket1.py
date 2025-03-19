import psycopg2
import argparse
from typing import List, Dict

def fetch_stock_history(conn, symbol: str) -> List[Dict]:
    """
    Fetch stock history from PostgreSQL for a given symbol.
    Args:
        conn: psycopg2 connection object.
        symbol: Stock symbol (e.g., '600050').
    Returns:
        List of dicts with 'day', 'c', and 'v'.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT day, c, v 
                FROM stock.stockhistory 
                WHERE symbol = %s 
                ORDER BY day ASC
            """, (symbol,))
            rows = cur.fetchall()
            return [{'day': row[0], 'c': float(row[1]), 'v': float(row[2])} for row in rows]
    except psycopg2.Error as e:
        print(f"Error fetching data from PostgreSQL: {e}")
        return []

def calculate_pf_chart(history: List[Dict[str, float]], step: float = None) -> List[Dict]:
    """
    Generate a Point and Figure chart from stock history with an optional step size.
    Args:
        history: List of dicts with 'c' (close price) and 'v' (volume).
        step: Optional step size; if None, calculated for at least 50 steps.
    Returns:
        List of buckets with mark ('X' or 'O'), high/low prices, and volume.
    """
    if not history:
        print("No data to process.")
        return []

    # Step 1: Find max and min prices
    prices = [day['c'] for day in history]
    max_price = max(prices)
    min_price = min(prices)
    price_range = max_price - min_price

    # Step 2: Determine step size
    if step is None:
        # Default: Calculate step for at least 50 steps
        min_units = 50
        step = price_range / min_units
        if step == 0:  # Handle zero range
            step = 1.0
    else:
        # Use provided step value
        if step <= 0:
            print(f"Invalid step value {step}; using default 1.0")
            step = 1.0
    print(f"Max Price: {max_price}, Min Price: {min_price}, Step: {step}")

    # Step 3: Initialize P&F chart
    buckets = []
    current_bucket = None
    reversal_threshold = 3 * step  # 3 steps for reversal (X -> O or O -> X)

    for day in history:
        price = day['c']
        volume = day['v']

        if not buckets:  # First day
            # Start with an "X" bucket
            bucket_idx = int((price - min_price) // step)  # Bucket index from min_price
            current_bucket = {
                'mark': 'X',
                'high': price,
                'low': price,
                'volume': volume,
                'start_day': day['day']
            }
            buckets.append(current_bucket)
        else:
            # Check current bucket direction
            if current_bucket['mark'] == 'X':
                # Rising trend: update high or reverse to "O"
                if price > current_bucket['high']:
                    current_bucket['high'] = price
                    current_bucket['volume'] += volume
                elif price <= current_bucket['high'] - reversal_threshold:
                    # Reverse to "O" if price drops 3+ steps
                    current_bucket = {
                        'mark': 'O',
                        'high': price,
                        'low': price,
                        'volume': volume,
                        'start_day': day['day']
                    }
                    buckets.append(current_bucket)
                else:
                    # Within range, just add volume
                    current_bucket['volume'] += volume
                    current_bucket['low'] = min(current_bucket['low'], price)

            elif current_bucket['mark'] == 'O':
                # Falling trend: update low or reverse to "X"
                if price < current_bucket['low']:
                    current_bucket['low'] = price
                    current_bucket['volume'] += volume
                elif price >= current_bucket['low'] + reversal_threshold:
                    # Reverse to "X" if price rises 3+ steps
                    current_bucket = {
                        'mark': 'X',
                        'high': price,
                        'low': price,
                        'volume': volume,
                        'start_day': day['day']
                    }
                    buckets.append(current_bucket)
                else:
                    # Within range, just add volume
                    current_bucket['volume'] += volume
                    current_bucket['high'] = max(current_bucket['high'], price)

    return buckets

def main(symbol: str, step: float = None):
    # Database connection details
    postgres_uri = 'postgresql://pfchart:pfchart1@localhost:5432/fzhou'

    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(postgres_uri)
        print(f"Connected to database: {postgres_uri}")
    except psycopg2.Error as e:
        print(f"Failed to connect to database: {e}")
        return

    # Fetch stock history
    stock_history = fetch_stock_history(conn, symbol)
    if not stock_history:
        print(f"No data found for symbol {symbol}")
        conn.close()
        return

    # Generate P&F chart with optional step
    pf_chart = calculate_pf_chart(stock_history, step)

    # Print results
    for i, bucket in enumerate(pf_chart):
        print(f"Bucket {i + 1}: Mark={bucket['mark']}, High={bucket['high']}, "
              f"Low={bucket['low']}, Volume={bucket['volume']}, Start Day={bucket['start_day']}")

    # Clean up
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Point and Figure chart from stock history.")
    parser.add_argument("symbol", help="Stock symbol (e.g., '600050')")
    parser.add_argument("--step", type=float, default=None, help="Custom step size (optional; e.g., 1.0)")
    args = parser.parse_args()
    main(args.symbol, args.step)
