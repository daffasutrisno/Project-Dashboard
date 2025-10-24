"""
Test script untuk chart Intra sgNB intrafreq pscell change
Quick testing tanpa generate seluruh PPT
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from datetime import datetime

# TEMPORARY: CSV fallback
CSV_FALLBACK_PATH = 'cluster_5g.csv'

def get_intra_sgnb_data(use_csv=True):
    """Fetch Intra sgNB intrafreq data (with CSV fallback)"""
    
    if use_csv and os.path.exists(CSV_FALLBACK_PATH):
        print(f"⚠️  Using CSV fallback: {CSV_FALLBACK_PATH}")
        df = pd.read_csv(CSV_FALLBACK_PATH)
        df['date_column'] = pd.to_datetime(df['date_column'])
        
        # Get last 35 days from CSV
        max_date = df['date_column'].max()
        start_date = max_date - pd.Timedelta(days=35)
        df = df[df['date_column'] >= start_date].copy()
        df = df.sort_values(['date_column', 'nc_5g']).reset_index(drop=True)
        
        print(f"✓ CSV loaded: {len(df)} records")
        return df
    
    raise FileNotFoundError(f"CSV file not found: {CSV_FALLBACK_PATH}")

def apply_interval_logic_with_gap(daily_data, interval=2):
    """
    Apply interval logic: every 2 days from END with GAP DETECTION
    Like Accessibility and Intra esgNB
    """
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

def plot_intra_sgnb(df):
    """Plot Intra sgNB intrafreq chart (LINE CHART)"""
    
    # Aggregate by date (MAX per day)
    daily = df.groupby('date_column').agg({'intra_sgnb_intrafreq': 'max'}).reset_index()
    
    # Filter: skip zero/null (like Availability and Intra esgNB)
    daily = daily[
        (daily['intra_sgnb_intrafreq'].notna()) & 
        (daily['intra_sgnb_intrafreq'] > 0)
    ].copy()
    
    print(f"\nStep 1 - Daily Aggregation (MAX per day):")
    print(f"  Total valid days (>0): {len(daily)}")
    
    print(f"\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['intra_sgnb_intrafreq']:.6f} ({row['intra_sgnb_intrafreq']*100:.4f}%)")
    
    # Apply interval logic with gap detection
    display_data = apply_interval_logic_with_gap(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['intra_sgnb_intrafreq'].values * 100  # Convert to percentage
    
    # Plot BOLD smooth line WITH CLIPPING
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            # Use k=2 (quadratic) to reduce overshoot
            spl = make_interp_spline(x_data, values, k=2)
            values_smooth = spl(x_smooth)
            
            # Clip values to valid range: 99.80% to 100.02%
            values_smooth = np.clip(values_smooth, 99.80, 100.02)
            
            ax.plot(x_smooth, values_smooth, color='#1f77b4', linewidth=3.5, 
                   zorder=20, solid_capstyle='round')
        except:
            ax.plot(x_data, values, color='#1f77b4', linewidth=3.5, 
                   zorder=20, solid_capstyle='round')
    else:
        ax.plot(x_data, values, color='#1f77b4', linewidth=3.5, 
               zorder=20, solid_capstyle='round')
    
    # Set y-axis: 99.80% to 100.02% with interval 0.02%, hide 100.02%
    # SAME AS INTRA ESGNB
    ax.set_ylim(99.80, 100.02)
    yticks = np.arange(99.80, 100.021, 0.02)
    ax.set_yticks(yticks)
    
    # HIDE label 100.02% (top padding)
    yticklabels = [f'{y:.2f}%' if abs(y - 100.02) > 0.001 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting
    ax.set_title('intra_sgnb_intrafreq_pscell_change', fontweight='bold', fontsize=14)
    ax.set_ylabel('%', fontsize=10)
    
    # Transparent grid
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5, color='lightgray', zorder=1)
    
    # Transparent borders
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.6)
        spine.set_alpha(0.4)
    
    # THIN tick marks
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
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/intra_sgnb_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("INTRA SGNB INTRAFREQ CHART TEST")
        print("="*60)
        
        # TEMPORARY: use CSV if database is down
        df = get_intra_sgnb_data(use_csv=True)
        print(f"\nTotal records: {len(df)}")
        
        plot_intra_sgnb(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
