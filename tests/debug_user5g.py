"""
Debug script untuk melihat detail data User 5G per tanggal
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

def check_user5g_data():
    """Check User 5G data untuk 35 hari terakhir"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT date_column, sum_en_dc_user_5g_wd
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
    print("USER 5G DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date (MAX for user count)
    daily = df.groupby('date_column').agg({
        'sum_en_dc_user_5g_wd': ['count', 'max', 'min', 'mean']
    }).reset_index()
    
    daily.columns = ['date', 'count', 'max_value', 'min_value', 'avg_value']
    
    print(f"\nTotal unique dates: {len(daily)}")
    print("\n" + "="*70)
    print("DETAIL PER TANGGAL:")
    print("="*70)
    print(f"{'Tanggal':<15} {'Records':<10} {'Max Users':<15} {'Status':<20}")
    print("-"*70)
    
    for idx, row in daily.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d (%a)')
        count = int(row['count'])
        max_val = row['max_value']
        
        # Determine status
        if pd.isna(max_val):
            status = "❌ SKIP (null)"
        elif max_val < 0:
            status = "❌ SKIP (negative)"
        elif max_val == 0:
            status = "⚠️  ZERO users"
        else:
            status = f"✓ VALID ({max_val:.0f} users)"
        
        print(f"{date_str:<15} {count:<10} {max_val:<15.0f} {status:<20}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    valid_days = daily[
        (daily['max_value'].notna()) & 
        (daily['max_value'] >= 0)
    ]
    
    print(f"Days with valid data (>= 0): {len(valid_days)}")
    
    if len(valid_days) > 0:
        print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')}")
        print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
        
        print(f"\nUser 5G Statistics (MAX per day):")
        print(f"  Min: {valid_days['max_value'].min():.0f} users")
        print(f"  Max: {valid_days['max_value'].max():.0f} users")
        print(f"  Mean: {valid_days['max_value'].mean():.0f} users")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_user5g_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
