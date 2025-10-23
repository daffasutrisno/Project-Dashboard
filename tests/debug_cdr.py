"""
Debug script untuk melihat detail data Call Drop Rate per tanggal
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

def check_cdr_data():
    """Check CDR data untuk 35 hari terakhir"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT date_column, g5_cdr
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
    print("CALL DROP RATE DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date
    daily = df.groupby('date_column').agg({
        'g5_cdr': ['count', 'max', 'min', 'mean']
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
        # CDR bisa bernilai 0 (valid), tidak di-skip
        if pd.isna(max_val):
            status = "❌ SKIP (null)"
        elif max_val < 0:
            status = "❌ SKIP (negative)"
        else:
            status = f"✓ VALID ({max_val*100:.4f}%)"
        
        print(f"{date_str:<15} {count:<10} {max_val:<15.6f} {status:<20}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    valid_days = daily[daily['max_value'] >= 0]
    invalid_days = daily[(daily['max_value'] < 0) | (daily['max_value'].isna())]
    
    print(f"Days with valid data (>=0): {len(valid_days)}")
    print(f"Days with invalid data: {len(invalid_days)}")
    
    if len(valid_days) > 0:
        print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')} ← INDEX AWAL CHART")
        print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
        
        print(f"\nCDR Statistics:")
        print(f"  Min CDR: {valid_days['max_value'].min():.6f} ({valid_days['max_value'].min()*100:.4f}%)")
        print(f"  Max CDR: {valid_days['max_value'].max():.6f} ({valid_days['max_value'].max()*100:.4f}%)")
        print(f"  Avg CDR: {valid_days['max_value'].mean():.6f} ({valid_days['max_value'].mean()*100:.4f}%)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_cdr_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
