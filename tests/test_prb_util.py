"""
Test script untuk chart DL PRB Util (Line + Bar overlay)
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

def get_prb_util_data():
    """Fetch PRB Util data"""
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

def apply_interval_logic_with_gap(daily_data, interval=2):
    """Apply interval logic: every 2 days from END with GAP DETECTION"""
    result_indices = []
    current_idx = len(daily_data) - 1
    
    print("\nApplying EVERY 2 DAYS logic (FROM END, WITH GAP DETECTION):")
    print("-" * 70)
    
    while current_idx >= 0:
        current_date = daily_data.iloc[current_idx]['date_column']
        print(f"✓ Index {current_idx}: {current_date.strftime('%Y-%m-%d')} - INCLUDED")
        result_indices.append(current_idx)
        
        next_idx = current_idx - interval
        
        if next_idx >= 0:
            next_date = daily_data.iloc[next_idx]['date_column']
            days_diff = (current_date - next_date).days
            
            print(f"  → Prev index {next_idx}: {next_date.strftime('%Y-%m-%d')} (gap: {days_diff} days)")
            
            if days_diff > interval * 1.5:
                print(f"  ⚠ Gap detected! Jumping -{interval} more (total: {interval*2} days)")
                next_idx = next_idx - interval
            
            current_idx = next_idx
        else:
            break
    
    result_indices.reverse()
    return daily_data.iloc[result_indices]

def plot_prb_util(df):
    """Plot DL PRB Util chart (LINE + BAR with DUAL Y-AXIS)"""
    
    # Aggregate by date (MAX per day for both)
    daily = df.groupby('date_column').agg({
        'g5_dlprb_util': 'max',           # Line (PRIMARY - patokan) - Left Y
        'dl_prb_util_5g_count_gt_085': 'max'  # Bar (follows) - Right Y
    }).reset_index()
    
    # Filter based on line data (PRIMARY) - skip zero/null
    daily = daily[
        (daily['g5_dlprb_util'].notna()) & 
        (daily['g5_dlprb_util'] > 0)
    ].copy()
    
    print(f"\nStep 1 - Daily Aggregation (based on g5_dlprb_util PRIMARY):")
    print(f"  Total valid days (>0): {len(daily)}")
    
    # Apply interval logic with gap detection
    display_data = apply_interval_logic_with_gap(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure with DUAL Y-AXIS
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Create second y-axis (shares same x-axis)
    ax2 = ax1.twinx()
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    
    # LEFT Y-AXIS (ax1): Line chart - g5_dlprb_util (%)
    values_line = display_data['g5_dlprb_util'].values * 100
    
    # Plot LINE on ax1 (left y-axis)
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            spl = make_interp_spline(x_data, values_line, k=3)
            values_smooth = spl(x_smooth)
            line1 = ax1.plot(x_smooth, values_smooth, color='#1f77b4', linewidth=3.5, 
                           zorder=20, solid_capstyle='round', label='5G_DL_PRB_UTIL (%)')
        except:
            line1 = ax1.plot(x_data, values_line, color='#1f77b4', linewidth=3.5, 
                           zorder=20, solid_capstyle='round', label='5G_DL_PRB_UTIL (%)')
    
    # RIGHT Y-AXIS (ax2): Bar chart - dl_prb_util_5g_count_gt_085 (cells)
    values_bar = display_data['dl_prb_util_5g_count_gt_085'].values
    
    # Plot BAR on ax2 (right y-axis) - VERY TRANSPARENT
    bar_mask = (pd.Series(values_bar).notna()) & (pd.Series(values_bar) > 0)
    bar_indices = np.where(bar_mask)[0]
    
    if len(bar_indices) > 0:
        bars = ax2.bar(bar_indices, values_bar[bar_indices], color='#ff7f0e', 
                       width=0.8, alpha=0.3, zorder=10, label='#Cells_DL PRB>85%')
    
    # Configure LEFT Y-AXIS (ax1 - percentage): 0-50% with interval 5%, hide 50%
    ax1.set_ylim(0, 50)
    yticks_left = np.arange(0, 51, 5)
    ax1.set_yticks(yticks_left)
    
    # HIDE label 50% (top padding)
    yticklabels_left = [f'{int(y)}%' if abs(y - 50) > 0.1 else '' for y in yticks_left]
    ax1.set_yticklabels(yticklabels_left)
    
    ax1.set_ylabel('PRB Util (%)', fontsize=10, color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4', labelsize=8)
    
    # Configure RIGHT Y-AXIS (ax2 - cells count): 0-10 with interval 1, hide 10
    ax2.set_ylim(0, 10)
    yticks_right = np.arange(0, 11, 1)
    ax2.set_yticks(yticks_right)
    
    # HIDE label 10 (top padding), show 9
    yticklabels_right = [f'{int(y)}' if abs(y - 10) > 0.1 else '' for y in yticks_right]
    ax2.set_yticklabels(yticklabels_right)
    
    ax2.set_ylabel('#Cells PRB>85%', fontsize=10, color='#ff7f0e')
    ax2.tick_params(axis='y', labelcolor='#ff7f0e', labelsize=8)
    
    # Set x-axis
    ax1.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Title
    ax1.set_title('DL PRB Util vs #Cells PRB Util >85% (Dual Y-Axis)', 
                  fontweight='bold', fontsize=14)
    
    # Grid (only on ax1)
    ax1.grid(True, alpha=0.15, linestyle='--', linewidth=0.5, color='lightgray', zorder=1)
    
    # Transparent borders
    for spine in ax1.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.6)
        spine.set_alpha(0.4)
    
    for spine in ax2.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.6)
        spine.set_alpha(0.4)
    
    # THIN tick marks
    ax1.tick_params(axis='both', which='both', width=0.5, length=3, color='gray', 
                   direction='out', pad=2)
    ax2.tick_params(axis='y', which='both', width=0.5, length=3, color='gray', 
                   direction='out', pad=2)
    
    # Transparent x-labels
    for label in ax1.get_xticklabels():
        label.set_alpha(0.8)
    
    # Combined legend (both axes)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/prb_util_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("DL PRB UTIL CHART TEST (LINE + BAR)")
        print("="*60)
        
        df = get_prb_util_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_prb_util(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
