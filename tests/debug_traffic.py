"""
Debug script untuk melihat detail data Total Traffic per tanggal
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

def check_traffic_data():
    """Check traffic data untuk 35 hari terakhir"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT date_column, traffic_5g
    FROM cluster_5g 
    WHERE date_column >= (SELECT MAX(date_column)::date - INTERVAL '35 days' FROM cluster_5g)
    ORDER BY date_column ASC, nc_5g
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    df['date_column'] = pd.to_datetime(df['date_column'])
    
    max_date = df['date_column'].max()
    min_date = max_date - pd.Timedelta(days=35)
    
    print("="*70)
    print("TOTAL TRAFFIC DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date (SUM for traffic)
    daily = df.groupby('date_column').agg({
        'traffic_5g': ['count', 'sum', 'min', 'max', 'mean']
    }).reset_index()
    
    daily.columns = ['date', 'count', 'sum_value', 'min_value', 'max_value', 'avg_value']
    
    print(f"\nTotal unique dates: {len(daily)}")
    print("\n" + "="*70)
    print("DETAIL PER TANGGAL:")
    print("="*70)
    print(f"{'Tanggal':<15} {'Records':<10} {'SUM Traffic':<15} {'Status':<20}")
    print("-"*70)
    
    for idx, row in daily.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d (%a)')
        count = int(row['count'])
        sum_val = row['sum_value']
        
        # Determine status
        if pd.isna(sum_val):
            status = "❌ SKIP (null)"
        elif sum_val < 0:
            status = "❌ SKIP (negative)"
        elif sum_val == 0:
            status = "⚠️  ZERO traffic"
        else:
            status = f"✓ VALID ({sum_val:.2f} GB)"
        
        print(f"{date_str:<15} {count:<10} {sum_val:<15.2f} {status:<20}")
    
    # Check for outliers > 50,000 GB
    outliers = daily[daily['sum_value'] > 50000]
    if len(outliers) > 0:
        print("\n⚠️  OUTLIERS DETECTED (> 50,000 GB):")
        for idx, row in outliers.iterrows():
            print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['sum_value']:.2f} GB")
        print("\n   These will be clipped to chart limit!")
    else:
        print("\n✓ No outliers > 50,000 GB")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    valid_days = daily[(daily['sum_value'].notna()) & (daily['sum_value'] >= 0)]
    
    print(f"Days with valid data (>= 0): {len(valid_days)}")
    
    if len(valid_days) > 0:
        print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')}")
        print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
        
        print(f"\nTraffic Statistics (SUM per day):")
        print(f"  Min: {valid_days['sum_value'].min():.2f} GB")
        print(f"  Max: {valid_days['sum_value'].max():.2f} GB")
        print(f"  Avg: {valid_days['sum_value'].mean():.2f} GB")
        print(f"  Total: {valid_days['sum_value'].sum():.2f} GB")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_traffic_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
