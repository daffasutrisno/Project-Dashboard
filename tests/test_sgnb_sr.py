"""
Test script untuk chart Sgnb addition SR
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

def get_sgnb_sr_data():
    """Fetch Sgnb addition SR data"""
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
    Apply simple interval logic: every 2 days from END
    """
    n_total = len(daily_data)
    result_indices = list(range(n_total - 1, -1, -interval))
    result_indices.reverse()
    
    print("\nApplying EVERY 2 DAYS logic (FROM END):")
    print("-" * 70)
    
    for i, idx in enumerate(result_indices):
        date = daily_data.iloc[idx]['date_column']
        value = daily_data.iloc[idx]['sgnb_addition_sr']
        print(f"✓ Display {i+1}: Index {idx} - {date.strftime('%Y-%m-%d')} - {value:.6f} ({value*100:.4f}%)")
    
    return daily_data.iloc[result_indices]

def apply_interval_logic_with_gap(daily_data, interval=2):
    """
    Apply interval logic: every 2 days from END with GAP DETECTION
    Same as Accessibility
    """
    result_indices = []
    current_idx = len(daily_data) - 1  # Start from LAST index
    
    print("\nApplying EVERY 2 DAYS logic (FROM END, WITH GAP DETECTION):")
    print("-" * 70)
    
    while current_idx >= 0:
        current_date = daily_data.iloc[current_idx]['date_column']
        print(f"✓ Index {current_idx}: {current_date.strftime('%Y-%m-%d')} - INCLUDED")
        result_indices.append(current_idx)
        
        # Try to jump by interval (2 days) BACKWARD
        next_idx = current_idx - interval
        
        if next_idx >= 0:
            next_date = daily_data.iloc[next_idx]['date_column']
            days_diff = (current_date - next_date).days
            
            print(f"  → Prev index {next_idx}: {next_date.strftime('%Y-%m-%d')} (gap: {days_diff} days)")
            
            # Gap detection
            if days_diff > interval * 1.5:
                print(f"  ⚠ Gap detected! Jumping -{interval} more (total: {interval*2} days)")
                next_idx = next_idx - interval
            
            current_idx = next_idx
        else:
            break
    
    result_indices.reverse()
    return daily_data.iloc[result_indices]

def plot_sgnb_sr(df):
    """Plot Sgnb addition SR chart"""
    
    # Aggregate by date (max per day)
    daily = df.groupby('date_column').agg({'sgnb_addition_sr': 'max'}).reset_index()
    
    # Filter: skip zero or null (like Accessibility)
    daily = daily[(daily['sgnb_addition_sr'].notna()) & (daily['sgnb_addition_sr'] > 0)].copy()
    
    print(f"\nStep 1 - Daily Aggregation:")
    print(f"  Total valid days (>0): {len(daily)}")
    
    # Apply interval logic with gap detection
    display_data = apply_interval_logic_with_gap(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['sgnb_addition_sr'].values * 100  # Convert to percentage
    
    # Plot BOLD smooth line with CLIPPING
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            spl = make_interp_spline(x_data, values, k=3)
            values_smooth = spl(x_smooth)
            
            # CLIP to reasonable range (avoid negative if needed)
            values_smooth = np.maximum(values_smooth, 0)
            
            ax.plot(x_smooth, values_smooth, color='#1f77b4', linewidth=3.5, 
                   zorder=20, solid_capstyle='round')
        except:
            ax.plot(x_data, values, color='#1f77b4', linewidth=3.5, 
                   zorder=20, solid_capstyle='round')
    else:
        ax.plot(x_data, values, color='#1f77b4', linewidth=3.5, 
               zorder=20, solid_capstyle='round')
    
    # Set y-axis: 99.00% to 100.20% with interval 0.20% (SAME AS AVAILABILITY)
    ax.set_ylim(99.00, 100.20)
    yticks = np.arange(99.00, 100.21, 0.20)
    ax.set_yticks(yticks)
    
    # HIDE label 100.20% (top padding) - SAME AS AVAILABILITY
    yticklabels = [f'{y:.2f}%' if abs(y - 100.20) > 0.01 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['sgnb_addition_sr'].iloc[i] for i in range(n_points)]
    tick_labels_str = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels_str, rotation=45, ha='right')
    
    # Formatting with TRANSPARENT grid and ticks
    ax.set_title('Sgnb addition SR - 5G (Every 2 Days)', fontweight='bold', fontsize=14)
    ax.set_ylabel('%', fontsize=10)
    
    # Transparent grid
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5, color='lightgray', zorder=1)
    
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
    
    # Transparent labels
    for label in ax.get_xticklabels():
        label.set_alpha(0.8)
    
    for label in ax.get_yticklabels():
        label.set_alpha(0.8)
    
    # Format y-axis
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.2f}%'))
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/sgnb_sr_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("SGNB ADDITION SR CHART TEST")
        print("="*60)
        
        df = get_sgnb_sr_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_sgnb_sr(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
