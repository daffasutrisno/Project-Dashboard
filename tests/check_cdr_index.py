"""
Script untuk mengetahui perhitungan index awal chart Call Drop Rate
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import pandas as pd

DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def calculate_cdr_index():
    conn = psycopg2.connect(**DB_CONFIG)
    
    query_max = "SELECT MAX(date_column) as max_date FROM cluster_5g"
    max_date = pd.read_sql(query_max, conn).iloc[0]['max_date']
    
    print("="*70)
    print("PERHITUNGAN INDEX AWAL CHART CALL DROP RATE")
    print("="*70)
    
    print(f"\n1. TANGGAL MAKSIMUM DI DATABASE:")
    print(f"   {max_date}")
    
    start_date = max_date - pd.Timedelta(days=35)
    print(f"\n2. TANGGAL AWAL RANGE (MAX - 35 hari):")
    print(f"   {start_date}")
    
    print(f"\n3. RANGE DATA YANG DIAMBIL:")
    print(f"   {start_date} s/d {max_date}")
    
    query_range = f"""
    SELECT date_column, 
           COUNT(*) as record_count,
           MAX(g5_cdr) as max_cdr,
           MIN(g5_cdr) as min_cdr,
           AVG(g5_cdr) as avg_cdr
    FROM cluster_5g 
    WHERE date_column >= '{start_date}'
    GROUP BY date_column
    ORDER BY date_column
    """
    
    df_range = pd.read_sql(query_range, conn)
    conn.close()
    
    print(f"\n4. DATA YANG DITEMUKAN:")
    print(f"   Total hari dengan data: {len(df_range)}")
    
    # Find first valid date (CDR >= 0, bisa 0)
    valid_dates = df_range[df_range['max_cdr'] >= 0]
    
    if len(valid_dates) > 0:
        first_valid = valid_dates.iloc[0]
        print(f"\n5. INDEX AWAL CHART:")
        print(f"   Tanggal: {first_valid['date_column']}")
        print(f"   CDR Max: {first_valid['max_cdr']:.6f} ({first_valid['max_cdr']*100:.4f}%)")
        print(f"   CDR Min: {first_valid['min_cdr']:.6f} ({first_valid['min_cdr']*100:.4f}%)")
        print(f"   CDR Avg: {first_valid['avg_cdr']:.6f} ({first_valid['avg_cdr']*100:.4f}%)")
        print(f"   Jumlah record: {first_valid['record_count']}")
        
        days_skipped = (first_valid['date_column'] - start_date).days
        print(f"\n6. HARI YANG DI-SKIP:")
        print(f"   {days_skipped} hari")
        
        if days_skipped > 0:
            print(f"\n   Alasan di-skip: Data tidak ada atau negative/null")
    
    print("\n" + "="*70)
    print("CATATAN:")
    print("="*70)
    print("- CDR (Call Drop Rate) bisa bernilai 0 (valid)")
    print("- Hanya skip jika: tidak ada data, negative, atau null")
    print("- Format: 0.0000 - 1.0000 (dikali 100 untuk persentase)")
    print("- Y-axis range: -0.002% to 0.020% (sesuaikan dengan data aktual)")
    print("="*70)

if __name__ == "__main__":
    try:
        calculate_cdr_index()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
