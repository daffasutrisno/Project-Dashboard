"""
Script observasi detail untuk data Total Traffic
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

def observe_traffic_data():
    """Observasi lengkap data Total Traffic"""
    
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
    print("OBSERVASI DATA TOTAL TRAFFIC - traffic_5g")
    print("="*80)
    
    print(f"\n📅 PERIODE DATA:")
    print(f"   Tanggal sekarang: {current_date}")
    print(f"   35 hari ke belakang: {start_date}")
    print(f"   Range: {start_date} s/d {current_date}")
    
    # Get all traffic data in range
    query_all = f"""
    SELECT date_column, traffic_5g
    FROM cluster_5g 
    WHERE date_column >= '{start_date}'
    ORDER BY date_column ASC, nc_5g
    """
    
    df_all = pd.read_sql(query_all, conn)
    df_all['date_column'] = pd.to_datetime(df_all['date_column'])
    
    print(f"\n📊 TOTAL RECORDS:")
    print(f"   Total records: {len(df_all):,}")
    
    # Filter valid data (not null)
    df_valid = df_all[df_all['traffic_5g'].notna()].copy()
    print(f"   Valid records (not null): {len(df_valid):,}")
    print(f"   Null records: {len(df_all) - len(df_valid):,}")
    
    if len(df_valid) == 0:
        print("\n⚠️ Tidak ada data valid!")
        return
    
    # Statistics - RAW DATA (per record)
    print(f"\n📈 STATISTIK - RAW DATA (PER RECORD):")
    print(f"   Min: {df_valid['traffic_5g'].min():.2f} GB")
    print(f"   Max: {df_valid['traffic_5g'].max():.2f} GB")
    print(f"   Mean: {df_valid['traffic_5g'].mean():.2f} GB")
    print(f"   Median: {df_valid['traffic_5g'].median():.2f} GB")
    print(f"   Total: {df_valid['traffic_5g'].sum():.2f} GB")
    
    # Daily aggregation (MAX per day - BUKAN SUM!)
    print(f"\n📅 AGREGASI PER HARI (MAX per hari):")
    daily = df_all.groupby('date_column').agg({
        'traffic_5g': ['count', 'max', 'min', 'mean']  # MAX, bukan SUM
    }).reset_index()
    
    daily.columns = ['date', 'count', 'max_value', 'min_value', 'avg_value']
    daily = daily[daily['max_value'].notna()]
    
    print(f"   Total hari dengan data: {len(daily)}")
    
    # Daily MAX statistics
    print(f"\n   Statistik MAX value per hari:")
    print(f"   Min dari max harian: {daily['max_value'].min():.2f} GB")
    print(f"   Max dari max harian: {daily['max_value'].max():.2f} GB")
    print(f"   Mean dari max harian: {daily['max_value'].mean():.2f} GB")
    
    # Days with zero
    zero_days = (daily['max_value'] == 0).sum()
    print(f"\n   Hari dengan max = 0: {zero_days} hari")
    print(f"   Hari dengan max > 0: {len(daily) - zero_days} hari")
    
    # Show top 10 highest traffic days
    print(f"\n🔝 TOP 10 HARI DENGAN TRAFFIC TERTINGGI (MAX per hari):")
    top_days = daily.nlargest(10, 'max_value')
    for idx, row in top_days.iterrows():
        print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['max_value']:,.2f} GB - {int(row['count'])} records")
    
    # Show bottom 10 (non-zero)
    print(f"\n🔻 BOTTOM 10 HARI DENGAN TRAFFIC TERENDAH (NON-ZERO):")
    nonzero_days = daily[daily['max_value'] > 0]
    if len(nonzero_days) >= 10:
        bottom_days = nonzero_days.nsmallest(10, 'max_value')
    else:
        bottom_days = nonzero_days
    
    for idx, row in bottom_days.iterrows():
        print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['max_value']:,.2f} GB - {int(row['count'])} records")
    
    # Percentiles
    print(f"\n📊 PERCENTILES (DAILY MAX):")
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        val = np.percentile(daily['max_value'], p)
        print(f"   P{p:2d}: {val:,.2f} GB")
    
    # Distribution analysis
    print(f"\n📊 DISTRIBUSI DATA (DAILY MAX VALUES):")
    bins = [
        (0, 10000, "0 - 10K GB"),
        (10000, 20000, "10K - 20K GB"),
        (20000, 30000, "20K - 30K GB"),
        (30000, 40000, "30K - 40K GB"),
        (40000, 50000, "40K - 50K GB"),
        (50000, float('inf'), "> 50K GB")
    ]
    
    for min_val, max_val, label in bins:
        count = ((daily['max_value'] >= min_val) & (daily['max_value'] < max_val)).sum()
        pct = count / len(daily) * 100 if len(daily) > 0 else 0
        print(f"   {label}: {count} hari ({pct:.1f}%)")
    
    # Check for outliers > 50,000 GB
    outliers = daily[daily['max_value'] > 50000]
    if len(outliers) > 0:
        print(f"\n⚠️  OUTLIERS DETECTED (> 50,000 GB):")
        for idx, row in outliers.iterrows():
            print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['max_value']:,.2f} GB")
        print(f"\n   Total {len(outliers)} hari melebihi 50K GB")
    else:
        print(f"\n✓ No outliers > 50,000 GB")
    
    # Recommendation for Y-axis
    print(f"\n💡 REKOMENDASI Y-AXIS RANGE:")
    min_traffic = daily['max_value'].min()
    max_traffic = daily['max_value'].max()
    
    print(f"\n   Data range: {min_traffic:,.2f} GB - {max_traffic:,.2f} GB")
    
    # Option 1: 0-50,000 with interval 10,000
    print(f"\n   Option 1 (RECOMMENDED):")
    print(f"   Range: 0 - 50,000 GB")
    print(f"   Interval: 10,000 GB")
    print(f"   Ticks: 0, 10K, 20K, 30K, 40K, 50K (6 ticks)")
    if max_traffic > 50000:
        print(f"   ⚠️  WARNING: Max data ({max_traffic:,.0f}) > 50,000!")
    else:
        print(f"   ✓ Padding: {50000 - max_traffic:,.0f} GB ({(50000-max_traffic)/max_traffic*100:.1f}%)")
    
    # Option 2: 0-50,000 with interval 5,000
    print(f"\n   Option 2 (More Detail):")
    print(f"   Range: 0 - 50,000 GB")
    print(f"   Interval: 5,000 GB")
    print(f"   Ticks: 0, 5K, 10K, 15K, ..., 45K, 50K (11 ticks)")
    if max_traffic > 50000:
        print(f"   ⚠️  WARNING: Max data ({max_traffic:,.0f}) > 50,000!")
    else:
        print(f"   ✓ Padding: {50000 - max_traffic:,.0f} GB")
    
    # Option 3: Dynamic based on max
    if max_traffic > 50000:
        suggested_max = int(np.ceil(max_traffic / 10000) * 10000)
        print(f"\n   Option 3 (Dynamic for outliers):")
        print(f"   Range: 0 - {suggested_max:,} GB")
        print(f"   Interval: {int(suggested_max/5):,} GB")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✓ Observasi selesai!")
    print("="*80)

if __name__ == "__main__":
    try:
        observe_traffic_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
