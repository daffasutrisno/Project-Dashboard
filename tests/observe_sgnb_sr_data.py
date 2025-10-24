"""
Script observasi detail untuk data Sgnb addition SR
Melihat min/max value, distribusi data, dan statistik lengkap
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import pandas as pd
import numpy as np

DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def observe_sgnb_sr_data():
    """Observasi lengkap data Sgnb addition SR"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Get current date and 35 days back
    query_dates = """
    SELECT 
        MAX(date_column) as current_date,
        MAX(date_column)::date - INTERVAL '35 days' as start_date
    FROM cluster_5g
    """
    
    dates_info = pd.read_sql(query_dates, conn)
    current_date = dates_info.iloc[0]['current_date']
    start_date = dates_info.iloc[0]['start_date']
    
    print("="*80)
    print("OBSERVASI DATA SGNB ADDITION SR - sgnb_addition_sr")
    print("="*80)
    
    print(f"\n📅 PERIODE DATA:")
    print(f"   Tanggal sekarang: {current_date}")
    print(f"   35 hari ke belakang: {start_date}")
    
    # Get all data in range
    query_all = f"""
    SELECT date_column, sgnb_addition_sr
    FROM cluster_5g 
    WHERE date_column >= '{start_date}'
    ORDER BY date_column ASC, nc_5g
    """
    
    df_all = pd.read_sql(query_all, conn)
    df_all['date_column'] = pd.to_datetime(df_all['date_column'])
    
    print(f"\n📊 TOTAL RECORDS: {len(df_all):,}")
    
    # Filter valid data
    df_valid = df_all[df_all['sgnb_addition_sr'].notna()].copy()
    print(f"   Valid records (not null): {len(df_valid):,}")
    
    if len(df_valid) == 0:
        print("\n⚠️ Tidak ada data valid!")
        return
    
    # Statistics - ALL DATA
    print(f"\n📈 STATISTIK - SEMUA DATA (TERMASUK ZERO):")
    print(f"   Min: {df_valid['sgnb_addition_sr'].min():.8f} ({df_valid['sgnb_addition_sr'].min()*100:.6f}%)")
    print(f"   Max: {df_valid['sgnb_addition_sr'].max():.8f} ({df_valid['sgnb_addition_sr'].max()*100:.6f}%)")
    print(f"   Mean: {df_valid['sgnb_addition_sr'].mean():.8f} ({df_valid['sgnb_addition_sr'].mean()*100:.6f}%)")
    print(f"   Median: {df_valid['sgnb_addition_sr'].median():.8f} ({df_valid['sgnb_addition_sr'].median()*100:.6f}%)")
    
    # Percentiles
    print(f"\n📊 PERCENTILES:")
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        val = np.percentile(df_valid['sgnb_addition_sr'], p)
        print(f"   P{p:2d}: {val:.8f} ({val*100:.6f}%)")
    
    # Daily aggregation
    print(f"\n📅 AGREGASI PER HARI (MAX per hari):")
    daily = df_all.groupby('date_column').agg({
        'sgnb_addition_sr': ['count', 'max', 'min', 'mean']
    }).reset_index()
    
    daily.columns = ['date', 'count', 'max_value', 'min_value', 'avg_value']
    daily = daily[daily['max_value'].notna()]
    
    print(f"   Total hari dengan data: {len(daily)}")
    print(f"\n   Statistik MAX value per hari:")
    print(f"   Min dari max harian: {daily['max_value'].min():.8f} ({daily['max_value'].min()*100:.6f}%)")
    print(f"   Max dari max harian: {daily['max_value'].max():.8f} ({daily['max_value'].max()*100:.6f}%)")
    
    # Recommendation
    print(f"\n💡 REKOMENDASI Y-AXIS RANGE:")
    min_val = daily['max_value'].min()
    max_val = daily['max_value'].max()
    
    # Suggest range
    suggested_min = max(min_val - 0.01, 0.98)  # At least 98%
    suggested_max = min(max_val + 0.005, 1.005)  # Max 100.5%
    
    print(f"   Suggested min: {suggested_min:.3f} ({suggested_min*100:.1f}%)")
    print(f"   Suggested max: {suggested_max:.3f} ({suggested_max*100:.1f}%)")
    print(f"   Current setting: 98.00% to 100.50%")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✓ Observasi selesai!")
    print("="*80)

if __name__ == "__main__":
    try:
        observe_sgnb_sr_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
