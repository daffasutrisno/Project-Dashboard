"""
Debug script untuk melihat detail data EUT vs DL User Thp per tanggal
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

def check_eut_thp_data():
    """Check EUT and DL User Thp data untuk 35 hari terakhir"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT date_column, traffic_5g, g5_userdl_thp
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
    print("EUT vs DL USER THP DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date (MAX for both)
    daily = df.groupby('date_column').agg({
        'traffic_5g': ['count', 'max', 'min', 'mean'],
        'g5_userdl_thp': ['max', 'min', 'mean']
    }).reset_index()
    
    daily.columns = ['date', 'traffic_count', 'traffic_max', 'traffic_min', 'traffic_mean',
                     'thp_max', 'thp_min', 'thp_mean']
    
    print(f"\nTotal unique dates: {len(daily)}")
    print("\n" + "="*70)
    print("DETAIL PER TANGGAL:")
    print("="*70)
    print(f"{'Tanggal':<15} {'Records':<10} {'Traffic Max':<15} {'Thp Max':<15} {'Status':<20}")
    print("-"*70)
    
    for idx, row in daily.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d (%a)')
        count = int(row['traffic_count'])
        traffic_max = row['traffic_max']
        thp_max = row['thp_max']
        
        # Determine status
        if pd.isna(traffic_max) or pd.isna(thp_max):
            status = "❌ SKIP (null)"
        elif traffic_max < 0 or thp_max < 0:
            status = "❌ SKIP (negative)"
        else:
            status = f"✓ VALID"
        
        print(f"{date_str:<15} {count:<10} {traffic_max:<15.2f} {thp_max:<15.2f} {status:<20}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    valid_days = daily[
        (daily['traffic_max'].notna()) & 
        (daily['thp_max'].notna()) &
        (daily['traffic_max'] >= 0) &
        (daily['thp_max'] >= 0)
    ]
    
    print(f"Days with valid data: {len(valid_days)}")
    
    if len(valid_days) > 0:
        print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')}")
        print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
        
        print(f"\nTraffic Statistics (MAX per day):")
        print(f"  Min: {valid_days['traffic_max'].min():.2f} GB")
        print(f"  Max: {valid_days['traffic_max'].max():.2f} GB")
        print(f"  Mean: {valid_days['traffic_max'].mean():.2f} GB")
        
        print(f"\nDL User Thp Statistics (MAX per day):")
        print(f"  Min: {valid_days['thp_max'].min():.2f}")
        print(f"  Max: {valid_days['thp_max'].max():.2f}")
        print(f"  Mean: {valid_days['thp_max'].mean():.2f}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_eut_thp_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
