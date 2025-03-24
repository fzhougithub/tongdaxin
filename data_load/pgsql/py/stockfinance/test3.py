from struct import *
import os

file_path = '/mnt/c/zd_zxjtzq_flatjy/vipdoc/cw/gpcw19960630.dat'
#file_path = '/mnt/c/zd_zxjtzq_flatjy/vipdoc/cw/gpsz301239.dat'

try:
    with open(file_path, 'rb') as cw_file:
        # Read header
        header_size = calcsize("<3h1H3L")  # 20 bytes
        file_size = os.path.getsize(file_path)
        if file_size < header_size:
            raise ValueError(f"File too small: {file_size} bytes < {header_size} bytes")

        data_header = cw_file.read(header_size)
        stock_header = unpack("<3h1H3L", data_header)
        max_count = stock_header[3]
        print(f"max_count: {max_count}")

        stock_item_size = calcsize("<6s1c1L")  # 11 bytes
        expected_min_size = header_size + max_count * stock_item_size
        if file_size < expected_min_size:
            print(f"Warning: File size {file_size} < expected {expected_min_size} for {max_count} items")

        # Process each stock
        for stock_idx in range(max_count):
            seek_pos = header_size + stock_idx * stock_item_size
            if seek_pos >= file_size:
                print(f"Skipping stock {stock_idx}: Seek position {seek_pos} exceeds file size {file_size}")
                break

            cw_file.seek(seek_pos)
            si = cw_file.read(stock_item_size)
            if len(si) != stock_item_size:
                print(f"Incomplete stock item at index {stock_idx}: {len(si)} bytes read")
                break

            stock_item = unpack("<6s1c1L", si)
            code = stock_item[0].decode('utf-8', errors='ignore').strip('\x00')
            foa = stock_item[2]
            print(f"Stock {code}, foa: {foa}")

            if foa >= file_size:
                print(f"Skipping {code}: foa {foa} exceeds file size {file_size}")
                continue

            cw_file.seek(foa)
            data_size_expected = calcsize('<264f')  # 1056 bytes
            info_data = cw_file.read(data_size_expected)
            data_size = len(info_data)

            if data_size != data_size_expected:
                print(f"Skipping {code}: Read {data_size} bytes, expected {data_size_expected}")
                continue

            cw_info = unpack('<264f', info_data)
            print(f"{code}: {cw_info[:5]}...")  # Print first 5 values for brevity

except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"Error: {e}")
