"""
Test script untuk chart Call Drop Rate (CDR)
Quick testing tanpa generate seluruh PPT
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

# Database config
DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def get_cdr_data():
    """Fetch Call Drop Rate data"""
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

def apply_interval_logic_simple(daily_data, interval=2):
    """
    Apply simple interval logic: every 2 days, COUNT FROM END (newest)
    NO gap checking, just take every Nth row from the end
    """
    n_total = len(daily_data)
    
    # Calculate indices from end: n-1, n-3, n-5, ...
    result_indices = list(range(n_total - 1, -1, -interval))
    
    # Reverse to chronological order
    result_indices.reverse()
    
    print("\nApplying SIMPLE EVERY 2 DAYS logic (FROM END):")
    print("-" * 70)
    
    for i, idx in enumerate(result_indices):
        date = daily_data.iloc[idx]['date_column']
        value = daily_data.iloc[idx]['g5_cdr']
        print(f"✓ Display {i+1}: Index {idx} - {date.strftime('%Y-%m-%d')} - {value:.6f} ({value*100:.4f}%)")
    
    return daily_data.iloc[result_indices]

def plot_cdr(df):
    """Plot Call Drop Rate chart with SIMPLE every 2 days"""
    
    # Aggregate by date (max per day)
    daily = df.groupby('date_column').agg({'g5_cdr': 'max'}).reset_index()
    
    # Filter: only keep NOT NULL and >= 0 (zero is VALID)
    daily = daily[(daily['g5_cdr'].notna()) & (daily['g5_cdr'] >= 0)].copy()
    
    print(f"\nStep 1 - Daily Aggregation:")
    print(f"  Total valid days (not null, >= 0): {len(daily)}")
    print(f"  Date range: {daily['date_column'].min()} to {daily['date_column'].max()}")
    
    print(f"\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['g5_cdr']:.6f} ({row['g5_cdr']*100:.4f}%)")
    
    # Apply SIMPLE interval logic (every 2 days, no gap checking)
    display_data = apply_interval_logic_simple(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['g5_cdr'].values * 100  # Convert to percentage, NO OFFSET
    
    # Plot smooth line with THICKER linewidth and HIGH zorder
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            spl = make_interp_spline(x_data, values, k=3)
            values_smooth = spl(x_smooth)
            
            # CLIP to minimum 0 - no negative values
            values_smooth = np.maximum(values_smooth, 0)
            
            # BOLD line with HIGH zorder (always on top)
            ax.plot(x_smooth, values_smooth, color='#1f77b4', 
                   linewidth=3.5, zorder=20, solid_capstyle='round')
        except:
            ax.plot(x_data, values, color='#1f77b4', 
                   linewidth=3.5, zorder=20, solid_capstyle='round')
    else:
        ax.plot(x_data, values, color='#1f77b4', 
               linewidth=3.5, zorder=20, solid_capstyle='round')
    
    # Set y-axis: 0.000% to 0.016%
    ax.set_ylim(0, 0.016)
    yticks = np.arange(0, 0.017, 0.002)
    ax.set_yticks(yticks)
    
    # HIDE label 0.016% (top padding)
    yticklabels = [f'{y:.3f}%' if abs(y - 0.016) > 0.0001 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting with TRANSPARENT grid and ticks
    ax.set_title('Call Drop Rate - 5G (0-0.016%)', fontweight='bold', fontsize=14)
    ax.set_ylabel('%', fontsize=10)
    
    # Transparent grid (LOWER zorder)
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5, 
           color='lightgray', zorder=1)
    
    # Subtle horizontal line at y=0 (LOWER zorder)
    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-', 
              alpha=0.2, zorder=2)
    
    # Transparent borders
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.6)
        spine.set_alpha(0.4)
    
    # THIN and TRANSPARENT tick marks
    ax.tick_params(
        axis='both',
        which='both',
        width=0.5,
        length=3,
        color='gray',
        direction='out',
        labelsize=8,
        pad=2
    )
    
    # X-axis specific
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    
    # Transparent labels
    for label in ax.get_xticklabels():
        label.set_alpha(0.8)
    
    for label in ax.get_yticklabels():
        label.set_alpha(0.8)
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/cdr_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("CALL DROP RATE (CDR) CHART TEST")
        print("="*60)
        
        df = get_cdr_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_cdr(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
