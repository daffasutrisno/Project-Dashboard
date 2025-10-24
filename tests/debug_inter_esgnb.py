"""
Debug script untuk melihat detail data Inter esgNB per tanggal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

CSV_FALLBACK_PATH = 'cluster_5g.csv'

def check_inter_esgnb_data():
    """Check Inter esgNB data untuk 35 hari terakhir"""
    
    if not os.path.exists(CSV_FALLBACK_PATH):
        print(f"✗ CSV file not found: {CSV_FALLBACK_PATH}")
        return
    
    df = pd.read_csv(CSV_FALLBACK_PATH)
    df['date_column'] = pd.to_datetime(df['date_column'])
    
    max_date = df['date_column'].max()
    min_date = max_date - pd.Timedelta(days=35)
    
    print("="*70)
    print("INTER ESGNB DATA DEBUG - 35 HARI TERAKHIR")
    print("="*70)
    print(f"\nDate range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total records: {len(df)}")
    
    # Group by date (MAX for inter_esgnb)
    daily = df.groupby('date_column').agg({
        'inter_esgnb': ['count', 'max', 'min', 'mean']
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
    
    valid_days = daily[(daily['max_value'].notna()) & (daily['max_value'] >= 0)]
    
    print(f"Days with valid data (>= 0): {len(valid_days)}")
    
    if len(valid_days) > 0:
        print(f"\nFirst valid date: {valid_days.iloc[0]['date'].strftime('%Y-%m-%d')}")
        print(f"Last valid date: {valid_days.iloc[-1]['date'].strftime('%Y-%m-%d')}")
        
        print(f"\nInter esgNB Statistics (MAX per day):")
        print(f"  Min: {valid_days['max_value'].min():.6f} ({valid_days['max_value'].min()*100:.4f}%)")
        print(f"  Max: {valid_days['max_value'].max():.6f} ({valid_days['max_value'].max()*100:.4f}%)")
        print(f"  Mean: {valid_days['max_value'].mean():.6f} ({valid_days['max_value'].mean()*100:.4f}%)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        check_inter_esgnb_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
