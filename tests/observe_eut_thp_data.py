"""
Script observasi untuk mengecek data EUT vs DL User Thp
Membandingkan semua kemungkinan column untuk EUT
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

def observe_eut_thp_data():
    """Observasi lengkap data EUT vs DL User Thp"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Check all possible EUT/Throughput-related columns
    query_columns = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'cluster_5g' 
    AND (
        column_name ILIKE '%thp%' OR
        column_name ILIKE '%throughput%' OR
        column_name ILIKE '%eut%' OR
        column_name ILIKE '%traffic%'
    )
    ORDER BY column_name
    """
    
    columns_df = pd.read_sql(query_columns, conn)
    
    print("="*80)
    print("KOLOM YANG BERKAITAN DENGAN THROUGHPUT/EUT/TRAFFIC:")
    print("="*80)
    for col in columns_df['column_name']:
        print(f"  - {col}")
    
    # Get sample data with all relevant columns
    query_data = """
    SELECT date_column, 
           traffic_5g,
           g5_userdl_thp,
           g5_celldl_thp,
           g5_eut_bhv,
           eut_4g_bh
    FROM cluster_5g 
    WHERE date_column >= (SELECT MAX(date_column)::date - INTERVAL '7 days' FROM cluster_5g)
    ORDER BY date_column DESC
    LIMIT 50
    """
    
    df = pd.read_sql(query_data, conn)
    df['date_column'] = pd.to_datetime(df['date_column'])
    
    print(f"\n{'='*80}")
    print("SAMPLE DATA (20 records terbaru):")
    print("="*80)
    print(f"{'Date':<12} {'traffic_5g':<14} {'g5_userdl_thp':<16} {'g5_celldl_thp':<16} {'g5_eut_bhv':<14} {'eut_4g_bh':<12}")
    print("-"*80)
    
    for idx, row in df.head(20).iterrows():
        print(f"{row['date_column'].strftime('%Y-%m-%d'):<12} "
              f"{row['traffic_5g']:>13.2f} "
              f"{row['g5_userdl_thp']:>15.2f} "
              f"{row['g5_celldl_thp']:>15.2f} "
              f"{row['g5_eut_bhv']:>13.2f} "
              f"{row['eut_4g_bh']:>11.2f}")
    
    # Aggregate by date (MAX per day)
    daily = df.groupby('date_column').agg({
        'traffic_5g': 'max',
        'g5_userdl_thp': 'max',
        'g5_celldl_thp': 'max',
        'g5_eut_bhv': 'max',
        'eut_4g_bh': 'max'
    }).reset_index()
    
    print(f"\n{'='*80}")
    print("STATISTIK (MAX per hari):")
    print("="*80)
    
    columns_to_check = ['traffic_5g', 'g5_userdl_thp', 'g5_celldl_thp', 'g5_eut_bhv', 'eut_4g_bh']
    
    for col in columns_to_check:
        if col in daily.columns and daily[col].notna().any():
            print(f"\n{col}:")
            print(f"  Min: {daily[col].min():.2f}")
            print(f"  Max: {daily[col].max():.2f}")
            print(f"  Mean: {daily[col].mean():.2f}")
    
    print(f"\n{'='*80}")
    print("PERBANDINGAN UNTUK CHART 'EUT vs DL User Thp':")
    print("="*80)
    
    # Option 1: traffic_5g / 1000 vs g5_userdl_thp (CURRENT - SALAH)
    print("\n❌ Option 1 (CURRENT): traffic_5g / 1000 vs g5_userdl_thp")
    if daily['traffic_5g'].notna().any() and daily['g5_userdl_thp'].notna().any():
        traffic_scaled = daily['traffic_5g'] / 1000
        print(f"  Line 1: {traffic_scaled.min():.2f} - {traffic_scaled.max():.2f}")
        print(f"  Line 2: {daily['g5_userdl_thp'].min():.2f} - {daily['g5_userdl_thp'].max():.2f}")
        ratio = traffic_scaled.mean() / daily['g5_userdl_thp'].mean() if daily['g5_userdl_thp'].mean() > 0 else 0
        print(f"  Rasio: {ratio:.2f}x")
        print(f"  ⚠️  Traffic adalah volume (GB), bukan throughput!")
    
    # Option 2: g5_eut_bhv vs g5_userdl_thp (RECOMMENDED - 5G SPECIFIC)
    print("\n✅ Option 2 (BEST): g5_eut_bhv vs g5_userdl_thp")
    if daily['g5_eut_bhv'].notna().any() and daily['g5_userdl_thp'].notna().any():
        print(f"  Line 1 (g5_eut_bhv): {daily['g5_eut_bhv'].min():.2f} - {daily['g5_eut_bhv'].max():.2f}")
        print(f"  Line 2 (g5_userdl_thp): {daily['g5_userdl_thp'].min():.2f} - {daily['g5_userdl_thp'].max():.2f}")
        ratio = daily['g5_eut_bhv'].mean() / daily['g5_userdl_thp'].mean() if daily['g5_userdl_thp'].mean() > 0 else 0
        print(f"  Rasio: {ratio:.2f}x")
        print(f"  ✓ EUT 5G (Effective User Throughput) vs User DL Thp")
        print(f"  ✓ Kedua-duanya spesifik untuk 5G")
    
    # Option 3: g5_celldl_thp vs g5_userdl_thp
    print("\n⚠️  Option 3: g5_celldl_thp vs g5_userdl_thp")
    if daily['g5_celldl_thp'].notna().any() and daily['g5_userdl_thp'].notna().any():
        print(f"  Line 1 (g5_celldl_thp): {daily['g5_celldl_thp'].min():.2f} - {daily['g5_celldl_thp'].max():.2f}")
        print(f"  Line 2 (g5_userdl_thp): {daily['g5_userdl_thp'].min():.2f} - {daily['g5_userdl_thp'].max():.2f}")
        ratio = daily['g5_celldl_thp'].mean() / daily['g5_userdl_thp'].mean() if daily['g5_userdl_thp'].mean() > 0 else 0
        print(f"  Rasio: {ratio:.2f}x")
        print(f"  Cell DL Thp vs User DL Thp (beda perspektif)")
    
    print(f"\n{'='*80}")
    print("💡 REKOMENDASI FINAL:")
    print("="*80)
    
    if daily['g5_eut_bhv'].notna().any():
        print("\n  ✅ GUNAKAN: g5_eut_bhv vs g5_userdl_thp")
        print("\n  Alasan:")
        print("    1. g5_eut_bhv = 5G Effective User Throughput (metric utama)")
        print("    2. g5_userdl_thp = 5G User DL Throughput")
        print("    3. Kedua-duanya adalah throughput metrics (Mbps)")
        print("    4. Spesifik untuk 5G (bukan 4G)")
        print("    5. Range value comparable")
        
        print("\n  Chart 'EUT vs DL User Thp' akan menunjukkan:")
        print("    - Line 1 (blue): g5_eut_bhv - Effective User Throughput")
        print("    - Line 2 (orange): g5_userdl_thp - User DL Throughput")
        
        print("\n  Ini membandingkan:")
        print("    - EUT (overall throughput effectiveness)")
        print("    - vs User DL Thp (actual user download speed)")
    elif daily['g5_celldl_thp'].notna().any():
        print("\n  Alternative: g5_celldl_thp vs g5_userdl_thp")
        print("  (Jika g5_eut_bhv tidak tersedia)")
    else:
        print("\n  ⚠️  Tidak ada column 5G EUT yang tersedia")
    
    conn.close()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        observe_eut_thp_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
