from pytdx.reader import HistoryFinancialReader
import pandas as pd
from datetime import datetime

# Configuration
profit_import_flag = 1
file_path = '/mnt/c/zd_zxjtzq_flatjy/vipdoc/cw/gpsz301239.dat'
stockcode_prefix = ['60', '00', '30']  # A-share prefixes (SH: 60, SZ: 00, CYB: 30)
file_date = datetime.now().strftime('%Y-%m-%d')  # Current date as fallback

def profit_report_import(df):
    """Process profit report data from DataFrame."""
    # Define key columns (adjust indices or names based on pytdx output)
    key_columns = {
        'report_date': 0,  # Assuming column 0 is date
        'gross_income_operation': 74,
        'net_profit': 95,
        'loss_assets_impairment': 81,
        'return_of_assets_treatment': 301,
        'loss_assets_credit': 517
        # Add other FINONE fields as needed
    }

    for index, row in df.iterrows():
        stock_code = str(index)  # Stock code from index
        report_date = str(row.iloc[key_columns['report_date']]).split('.')[0]
        prefix = stock_code[:2]

        # Skip invalid dates or non-A-share codes
        if not report_date.isdigit() or prefix not in stockcode_prefix:
            continue

        # Extract fields
        gross_income = row.iloc[key_columns['gross_income_operation']]
        net_profit = row.iloc[key_columns['net_profit']]
        loss_impairment = row.iloc[key_columns['loss_assets_impairment']]
        return_assets = row.iloc[key_columns['return_of_assets_treatment']]
        loss_credit = row.iloc[key_columns['loss_assets_credit']]

        # Print (or process further)
        print(stock_code, report_date, net_profit, loss_impairment, return_assets, loss_credit)

def main():
    pd.set_option('display.max_columns', None)
    reader = HistoryFinancialReader()

    try:
        # Load financial data
        results = reader.get_df(file_path)
        print(f"Loaded {len(results)} records with {len(results.columns)} columns.")
        
        if profit_import_flag == 1:
            print(f"PROFIT data importing on date: {file_date} in process ...")
            #profit_report_import(results)
            print(f"PROFIT data importing on date: {file_date} Done.")
    except Exception as e:
        print(f"Error loading or processing file {file_path}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
