"""
Debug script untuk melihat detail data availability per tanggal
Melihat mengapa index dimulai dari 19/09
"""

import psycopg2
import pandas as pd
from datetime import datetime

# Database config
DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def check_availability_data():
    """Check availability data untuk 35 hari terakhir"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Get 35 days data
    query = """
    SELECT date_column, avail_auto_5g
    FROM cluster_5g 
    WHERE date_column >= (SELECT MAX(date_column)::date - INTERVAL '35 days' FROM cluster_5g)
    ORDER BY date_column ASC, nc_5g
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    df['date_column'] = pd.to_datetime(df['date_column'])
    
    # Get date range
    max_date = df['date_column'].max()
    min_date = max_date - pd.Timedelta(days=35)
    
    print("="*70)
    print("AVAILABILITY DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date
    daily = df.groupby('date_column').agg({
        'avail_auto_5g': ['count', 'max', 'min', 'mean']
    }).reset_index()
    
    daily.columns = ['date', 'count', 'max_value', 'min_value', 'avg_value']
    
    print(f"\nTotal unique dates: {len(daily)}")
    print("\n" + "="*70)
    print("DETAIL PER TANGGAL:")
    print("="*70)
    print(f"{'Tanggal':<15} {'Records':<10} {'Max Value':<15} {'Status':<20}")
    print("-"*70)
    
    for idx, row in daily.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d (%a)')
        count = int(row['count'])
        max_val = row['max_value']
        
        # Determine status
        if max_val == 0:
            status = "❌ SKIP (all zero)"
        elif max_val > 0:
            status = f"✓ VALID ({max_val*100:.2f}%)"
        else:
            status = "❌ SKIP (null/negative)"
        
        print(f"{date_str:<15} {count:<10} {max_val:<15.6f} {status:<20}")
    
    # Create complete date range
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    print("\n" + "="*70)
    print("MISSING DATES (tidak ada data sama sekali):")
    print("="*70)
    
    existing_dates = set(daily['date'].dt.date)
    missing_count = 0
    
    for date in date_range:
        if date.date() not in existing_dates:
            print(f"❌ {date.strftime('%Y-%m-%d (%a)')}: NO DATA")
            missing_count += 1
    
    if missing_count == 0:
        print("✓ Semua tanggal ada datanya")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    valid_days = daily[daily['max_value'] > 0]
    zero_days = daily[daily['max_value'] == 0]
    
    print(f"Total days in range: {len(date_range)}")
    print(f"Days with data: {len(daily)}")
    print(f"Days with NO data: {missing_count}")
    print(f"Days with valid data (>0): {len(valid_days)}")
    print(f"Days with zero data: {len(zero_days)}")
    
    print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')} ← INDEX AWAL CHART")
    print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_availability_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
