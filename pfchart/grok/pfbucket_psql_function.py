import psycopg2
import argparse
import matplotlib.pyplot as plt
import json

def fetch_pf_chart_data(conn, symbol: str, step: float = None) -> list:
    """Fetch Point and Figure chart data from PostgreSQL."""
    try:
        with conn.cursor() as cur:
            if step is None:
                cur.execute("SELECT stock.calculate_pf_chart_pg(%s);", (symbol,))
            else:
                cur.execute("SELECT stock.calculate_pf_chart_pg(%s, %s);", (symbol, step))
            result = cur.fetchone()[0]
            pf_chart = json.loads(result) if isinstance(result, str) else result
            return pf_chart if isinstance(pf_chart, list) else []
    except psycopg2.Error as e:
        print(f"Error fetching P&F chart data from PostgreSQL: {e}")
        return []

def draw_pf_chart_with_volume(buckets: list, symbol: str, step: float, output_file: str):
    """Draw a Point and Figure chart with price and volume subplots, saving to a file."""
    if not buckets:
        print("No buckets to plot.")
        return

    # Calculate price levels
    min_price = min(bucket['low'] for bucket in buckets)
    max_price = max(bucket['high'] for bucket in buckets)
    min_price = step * round(min_price / step)
    max_price = step * round(max_price / step + 0.5)
    price_levels = [min_price + i * step for i in range(int((max_price - min_price) / step) + 1)]
    num_levels = len(price_levels)

    print(f"min_price: {min_price}, max_price: {max_price}, step: {step}")
    print(f"price_levels: {price_levels}")

    x_coords = []
    y_coords = []
    marks = []
    for col, bucket in enumerate(buckets):
        print(f"Bucket {col + 1}: low={bucket['low']}, high={bucket['high']}, mark={bucket['mark']}")
        low_idx = min(range(len(price_levels)), key=lambda i: abs(price_levels[i] - bucket['low']))
        high_idx = min(range(len(price_levels)), key=lambda i: abs(price_levels[i] - bucket['high']))
        low_idx, high_idx = min(low_idx, high_idx), max(low_idx, high_idx)
        for row in range(low_idx, high_idx + 1):
            x_coords.append(col)
            y_coords.append(row)
            marks.append(bucket['mark'])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(len(buckets) * 0.5, num_levels * 0.4 + 3),
                                   gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

    for i, (x, y, mark) in enumerate(zip(x_coords, y_coords, marks)):
        ax1.text(x, y, mark, fontsize=12, ha='center', va='center',
                 color='blue' if mark == 'X' else 'red')
    ax1.set_yticks(range(len(price_levels)))
    ax1.set_yticklabels([f"{p:.2f}" for p in price_levels])
    ax1.set_ylabel("Price Levels")
    ax1.set_title(f"Point and Figure Chart for {symbol} (Step: {step})")
    ax1.grid(True, linestyle='--', alpha=0.7)

    bucket_indices = list(range(len(buckets)))
    volumes = [bucket['volume'] for bucket in buckets]
    ax2.bar(bucket_indices, volumes, color=['blue' if b['mark'] == 'X' else 'red' for b in buckets])
    ax2.set_xticks(bucket_indices)
    ax2.set_xticklabels([f"B{i+1}" for i in range(len(buckets))])
    ax2.set_ylabel("Accumulated Volume")
    ax2.set_xlabel("Buckets")

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', format='jpg')
    print(f"Chart saved to {output_file}")
    plt.close(fig)

def main(symbol: str, step: float = None):
    postgres_uri = 'postgresql://pfchart:pfchart1@localhost:5432/fzhou'
    output_dir = '/mnt/c/Users/Admin/Pictures/stock/'
    
    try:
        conn = psycopg2.connect(postgres_uri)
        print(f"Connected to database: {postgres_uri}")
    except psycopg2.Error as e:
        print(f"Failed to connect to database: {e}")
        return

    pf_chart = fetch_pf_chart_data(conn, symbol, step)
    if not pf_chart:
        print(f"No P&F chart data found for symbol {symbol}")
        conn.close()
        return

    effective_step = step if step is not None else pf_chart[0].get('step', 1.0)
    output_file = f"{output_dir}pf_chart_{symbol}_step_{effective_step:.2f}.jpg"
    draw_pf_chart_with_volume(pf_chart, symbol, effective_step, output_file)

    for i, bucket in enumerate(pf_chart):
        print(f"Bucket {i + 1}: Mark={bucket['mark']}, High={bucket['high']}, "
              f"Low={bucket['low']}, Volume={bucket['volume']}, Start Day={bucket['start_day']}")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw a Point and Figure chart using PostgreSQL data.")
    parser.add_argument("symbol", help="Stock symbol (e.g., '600050')")
    parser.add_argument("--step", type=float, default=None, help="Custom step size (optional; e.g., 1.0)")
    args = parser.parse_args()
    main(args.symbol, args.step)
