"""
Test script untuk chart Accessibility dengan logic EVERY 2 DAYS
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from datetime import datetime

DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def get_accessibility_data():
    """Fetch accessibility data"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT *
    FROM cluster_5g 
    WHERE date_column >= (SELECT MAX(date_column)::date - INTERVAL '35 days' FROM cluster_5g)
    ORDER BY date_column ASC, nc_5g
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    df['date_column'] = pd.to_datetime(df['date_column'])
    
    return df

def apply_interval_logic(daily_data, interval=2):
    """
    Apply interval logic: every 2 days, COUNT FROM END (newest)
    If data is missing at expected interval, jump becomes 4 days
    """
    result_indices = []
    current_idx = len(daily_data) - 1  # Start from LAST index
    
    print("\nApplying EVERY 2 DAYS logic (FROM END):")
    print("-" * 70)
    
    while current_idx >= 0:
        current_date = daily_data.iloc[current_idx]['date_column']
        print(f"✓ Index {current_idx}: {current_date.strftime('%Y-%m-%d')} - INCLUDED")
        result_indices.append(current_idx)
        
        # Try to jump by interval (2 days) BACKWARD
        next_idx = current_idx - interval
        
        # Check if next_idx exists
        if next_idx >= 0:
            # Check actual date difference
            next_date = daily_data.iloc[next_idx]['date_column']
            days_diff = (current_date - next_date).days
            
            print(f"  → Prev index {next_idx}: {next_date.strftime('%Y-%m-%d')} (gap: {days_diff} days)")
            
            # If gap is larger than expected (means some days were skipped)
            if days_diff > interval * 1.5:  # tolerance
                print(f"  ⚠ Gap detected! Data missing. Jumping -{interval} more (total: {interval*2} days)")
                next_idx = next_idx - interval
            
            current_idx = next_idx
        else:
            break
    
    # Reverse to chronological order
    result_indices.reverse()
    return daily_data.iloc[result_indices]

def plot_accessibility(df):
    """Plot accessibility chart"""
    
    # Step 1: Aggregate by date (max per day)
    daily = df.groupby('date_column').agg({'da_5g': 'max'}).reset_index()
    
    # Step 2: Filter - only keep days with da_5g > 0
    daily = daily[daily['da_5g'] > 0].copy()
    
    print(f"\nStep 1 - Daily Aggregation:")
    print(f"  Total valid days (>0): {len(daily)}")
    print(f"  Date range: {daily['date_column'].min()} to {daily['date_column'].max()}")
    
    print(f"\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['da_5g']:.4f} ({row['da_5g']*100:.2f}%)")
    
    # Step 3: Apply interval logic (every 2 days, or 4 if gap)
    display_data = apply_interval_logic(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['da_5g'].values * 100
    
    # Plot smooth line
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            spl = make_interp_spline(x_data, values, k=3)
            values_smooth = spl(x_smooth)
            ax.plot(x_smooth, values_smooth, color='#1f77b4', linewidth=2)
        except:
            ax.plot(x_data, values, color='#1f77b4', linewidth=2)
    else:
        ax.plot(x_data, values, color='#1f77b4', linewidth=2)
    
    # Set y-axis: 96.00 to 101.00
    ax.set_ylim(96.00, 101.00)
    
    # Set y-ticks
    yticks = np.arange(96.00, 101.01, 1.0)  # 96, 97, 98, 99, 100, 101
    ax.set_yticks(yticks)
    
    # HIDE label 101% (top padding), sama seperti Availability hide 100.20%
    yticklabels = [f'{y:.2f}%' if abs(y - 101.00) > 0.01 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels - SHOW ALL DISPLAYED DAYS with YEAR
    tick_positions = x_data
    tick_labels_str = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels_str, rotation=45, ha='right')
    
    # Formatting
    ax.set_title('Accessibility Test - 5G (EVERY 2 DAYS, Hide 101%)', fontweight='bold', fontsize=14)
    
    ax.set_ylabel('%', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/accessibility_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    try:
        print("="*70)
        print("ACCESSIBILITY CHART TEST - EVERY 2 DAYS LOGIC")
        print("="*70)
        
        df = get_accessibility_data()
        print(f"\nTotal records from DB: {len(df)}")
        
        plot_accessibility(df)
        
        print("\n" + "="*70)
        print("✓ Test completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
