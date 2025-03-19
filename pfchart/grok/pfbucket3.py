import psycopg2
import argparse
from typing import List, Dict
import matplotlib.pyplot as plt

def fetch_stock_history(conn, symbol: str) -> List[Dict]:
    """Fetch stock history from PostgreSQL for a given symbol."""
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
    """Generate a Point and Figure chart from stock history with an optional step size."""
    if not history:
        print("No data to process.")
        return []

    prices = [day['c'] for day in history]
    max_price = max(prices)
    min_price = min(prices)
    price_range = max_price - min_price

    if step is None:
        min_units = 50
        step = price_range / min_units
        if step == 0:
            step = 1.0
    else:
        if step <= 0:
            print(f"Invalid step value {step}; using default 1.0")
            step = 1.0
    print(f"Max Price: {max_price}, Min Price: {min_price}, Step: {step}")

    buckets = []
    current_bucket = None
    reversal_threshold = 3 * step

    for day in history:
        price = day['c']
        volume = day['v']

        if not buckets:
            bucket_idx = int((price - min_price) // step)
            current_bucket = {
                'mark': 'X',
                'high': price,
                'low': price,
                'volume': volume,
                'start_day': day['day']
            }
            buckets.append(current_bucket)
        else:
            if current_bucket['mark'] == 'X':
                if price > current_bucket['high']:
                    current_bucket['high'] = price
                    current_bucket['volume'] += volume
                elif price <= current_bucket['high'] - reversal_threshold:
                    current_bucket = {
                        'mark': 'O',
                        'high': price,
                        'low': price,
                        'volume': volume,
                        'start_day': day['day']
                    }
                    buckets.append(current_bucket)
                else:
                    current_bucket['volume'] += volume
                    current_bucket['low'] = min(current_bucket['low'], price)
            elif current_bucket['mark'] == 'O':
                if price < current_bucket['low']:
                    current_bucket['low'] = price
                    current_bucket['volume'] += volume
                elif price >= current_bucket['low'] + reversal_threshold:
                    current_bucket = {
                        'mark': 'X',
                        'high': price,
                        'low': price,
                        'volume': volume,
                        'start_day': day['day']
                    }
                    buckets.append(current_bucket)
                else:
                    current_bucket['volume'] += volume
                    current_bucket['high'] = max(current_bucket['high'], price)

    return buckets

def calculate_price_level_volumes(history: List[Dict[str, float]], min_price: float, step: float, max_price: float) -> List[float]:
    """Calculate accumulated volume for each price level."""
    num_levels = int((max_price - min_price) // step) + 1
    price_volumes = [0.0] * num_levels  # Initialize volume array for each price level

    for day in history:
        price = day['c']
        volume = day['v']
        level_idx = int((price - min_price) // step)
        if 0 <= level_idx < num_levels:  # Ensure index is within bounds
            price_volumes[level_idx] += volume

    return price_volumes

def draw_pf_chart_with_price_volume(buckets: List[Dict], history: List[Dict[str, float]], min_price: float, step: float, symbol: str):
    """Draw a P&F chart with price bars and a volume bar chart per price level."""
    if not buckets or not history:
        print("No data to plot.")
        return

    # Calculate price levels
    max_price = max(bucket['high'] for bucket in buckets)
    price_levels = [min_price + i * step for i in range(int((max_price - min_price) // step) + 1)]
    num_levels = len(price_levels)

    # Prepare P&F price chart data
    x_coords = []
    y_coords = []
    marks = []
    for col, bucket in enumerate(buckets):
        high_idx = int((bucket['high'] - min_price) // step)
        low_idx = int((bucket['low'] - min_price) // step)
        for row in range(low_idx, high_idx + 1):
            x_coords.append(col)
            y_coords.append(row)
            marks.append(bucket['mark'])

    # Calculate volume per price level
    price_volumes = calculate_price_level_volumes(history, min_price, step, max_price)

    # Create subplots: 2 rows, 1 column
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(len(buckets) * 0.5 + 2, num_levels * 0.4 + 3), 
                                   gridspec_kw={'height_ratios': [3, 1]})

    # Top subplot: P&F Price chart
    for i, (x, y, mark) in enumerate(zip(x_coords, y_coords, marks)):
        ax1.text(x, y, mark, fontsize=12, ha='center', va='center', 
                 color='blue' if mark == 'X' else 'red')
    ax1.set_xticks(range(len(buckets)))
    ax1.set_xticklabels([f"B{i+1}" for i in range(len(buckets))])
    ax1.set_yticks(range(num_levels))
    ax1.set_yticklabels([f"{p:.2f}" for p in price_levels])
    ax1.set_ylabel("Price Levels")
    ax1.set_title(f"Point and Figure Chart for {symbol} (Step: {step})")
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Bottom subplot: Volume chart per price level
    ax2.bar(range(num_levels), price_volumes, color='gray', width=0.8)
    ax2.set_xticks(range(num_levels))
    ax2.set_xticklabels([f"{p:.2f}" for p in price_levels], rotation=45)
    ax2.set_ylabel("Accumulated Volume")
    ax2.set_xlabel("Price Levels")

    # Adjust layout and display
    plt.tight_layout()
    plt.show()

def main(symbol: str, step: float = None):
    postgres_uri = 'postgresql://pfchart:pfchart1@localhost:5432/fzhou'
    try:
        conn = psycopg2.connect(postgres_uri)
        print(f"Connected to database: {postgres_uri}")
    except psycopg2.Error as e:
        print(f"Failed to connect to database: {e}")
        return

    stock_history = fetch_stock_history(conn, symbol)
    if not stock_history:
        print(f"No data found for symbol {symbol}")
        conn.close()
        return

    pf_chart = calculate_pf_chart(stock_history, step)
    min_price = min(day['c'] for day in stock_history)
    draw_pf_chart_with_price_volume(pf_chart, stock_history, min_price, 
                                    step if step else (max(day['c'] for day in stock_history) - min_price) / 50, symbol)

    for i, bucket in enumerate(pf_chart):
        print(f"Bucket {i + 1}: Mark={bucket['mark']}, High={bucket['high']}, "
              f"Low={bucket['low']}, Volume={bucket['volume']}, Start Day={bucket['start_day']}")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and draw a P&F chart with price-level volume from stock history.")
    parser.add_argument("symbol", help="Stock symbol (e.g., '600050')")
    parser.add_argument("--step", type=float, default=None, help="Custom step size (optional; e.g., 1.0)")
    args = parser.parse_args()
    main(args.symbol, args.step)
