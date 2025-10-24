"""
Debug script untuk melihat detail data DL PRB Util per tanggal
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

def check_prb_util_data():
    """Check DL PRB Util data untuk 35 hari terakhir"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT date_column, g5_dlprb_util, dl_prb_util_5g_count_gt_085
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
    print("DL PRB UTIL DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date (MAX for both)
    daily = df.groupby('date_column').agg({
        'g5_dlprb_util': ['count', 'max', 'min', 'mean'],
        'dl_prb_util_5g_count_gt_085': ['max', 'min', 'mean']  # FIXED name
    }).reset_index()
    
    daily.columns = ['date', 'util_count', 'util_max', 'util_min', 'util_mean',
                     'count_max', 'count_min', 'count_mean']
    
    print(f"\nTotal unique dates: {len(daily)}")
    print("\n" + "="*70)
    print("DETAIL PER TANGGAL:")
    print("="*70)
    print(f"{'Tanggal':<15} {'Records':<10} {'PRB Util Max':<15} {'Count >85%':<15} {'Status':<20}")
    print("-"*70)
    
    for idx, row in daily.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d (%a)')
        count = int(row['util_count'])
        util_max = row['util_max']
        count_max = row['count_max']
        
        # Determine status (based on LINE data - PRIMARY)
        if pd.isna(util_max) or util_max == 0:
            status = "❌ SKIP (null/zero)"
        else:
            status = f"✓ VALID"
        
        print(f"{date_str:<15} {count:<10} {util_max*100:<14.2f}% {count_max:<14.0f} {status:<20}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    valid_days = daily[(daily['util_max'].notna()) & (daily['util_max'] > 0)]
    
    print(f"Days with valid data (>0): {len(valid_days)}")
    
    if len(valid_days) > 0:
        print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')}")
        print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
        
        print(f"\ng5_dlprb_util Statistics (MAX per day):")
        print(f"  Min: {valid_days['util_max'].min()*100:.2f}%")
        print(f"  Max: {valid_days['util_max'].max()*100:.2f}%")
        print(f"  Mean: {valid_days['util_max'].mean()*100:.2f}%")
        
        print(f"\ndlprb_util_5g_count_gt_085 Statistics (MAX per day):")
        print(f"  Min: {valid_days['count_max'].min():.0f} cells")
        print(f"  Max: {valid_days['count_max'].max():.0f} cells")
        print(f"  Mean: {valid_days['count_max'].mean():.0f} cells")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_prb_util_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
