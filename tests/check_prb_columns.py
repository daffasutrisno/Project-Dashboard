"""
Script untuk mengecek column yang tersedia untuk PRB Util
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2

DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def check_prb_columns():
    """Check columns related to PRB"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get all columns
    query = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'cluster_5g' 
    AND (
        column_name ILIKE '%prb%' OR
        column_name ILIKE '%util%' OR
        column_name ILIKE '%085%' OR
        column_name ILIKE '%85%'
    )
    ORDER BY column_name
    """
    
    cursor.execute(query)
    columns = cursor.fetchall()
    
    print("="*70)
    print("COLUMNS RELATED TO PRB/UTIL:")
    print("="*70)
    
    for col in columns:
        print(f"  - {col[0]}")
    
    print("\n" + "="*70)
    print("SAMPLE DATA:")
    print("="*70)
    
    # Get sample data
    query_sample = """
    SELECT date_column, g5_dlprb_util
    FROM cluster_5g 
    ORDER BY date_column DESC
    LIMIT 10
    """
    
    cursor.execute(query_sample)
    rows = cursor.fetchall()
    
    print(f"{'Date':<15} {'g5_dlprb_util':<20}")
    print("-"*70)
    for row in rows:
        print(f"{str(row[0]):<15} {row[1]:<20}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("💡 REKOMENDASI:")
    print("="*70)
    print("Kemungkinan column untuk bar chart:")
    print("  1. Cari column dengan nama mirip 'count' atau 'gt_085' atau 'over_85'")
    print("  2. Atau buat perhitungan sendiri dari data mentah")
    print("  3. Atau gunakan hanya line chart (g5_dlprb_util)")
    print("="*70)

if __name__ == "__main__":
    try:
        check_prb_columns()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
