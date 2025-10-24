"""
Test script untuk chart Inter esgNB pscell change
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

# TEMPORARY: CSV fallback
CSV_FALLBACK_PATH = 'cluster_5g.csv'

def get_inter_esgnb_data(use_csv=True):
    """Fetch Inter esgNB data (with CSV fallback)"""
    
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
    
    # Original database code
    try:
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
    except Exception as e:
        print(f"✗ Database error: {e}")
        if os.path.exists(CSV_FALLBACK_PATH):
            print(f"⚠️  Falling back to CSV...")
            return get_inter_esgnb_data(use_csv=True)
        raise

def apply_interval_logic_simple(daily_data, interval=2):
    """
    Apply simple interval logic: every 2 days from END
    No gap checking, like CDR
    """
    n_total = len(daily_data)
    result_indices = list(range(n_total - 1, -1, -interval))
    result_indices.reverse()
    
    print("\nApplying SIMPLE EVERY 2 DAYS logic (FROM END):")
    print("-" * 70)
    
    for i, idx in enumerate(result_indices):
        date = daily_data.iloc[idx]['date_column']
        value = daily_data.iloc[idx]['inter_esgnb']
        print(f"✓ Display {i+1}: Index {idx} - {date.strftime('%Y-%m-%d')} - {value:.6f} ({value*100:.4f}%)")
    
    return daily_data.iloc[result_indices]

def plot_inter_esgnb(df):
    """Plot Inter esgNB chart (LINE CHART)"""
    
    # Aggregate by date (MAX per day)
    daily = df.groupby('date_column').agg({'inter_esgnb': 'max'}).reset_index()
    
    # Filter: keep NOT NULL (zero is VALID, like CDR)
    daily = daily[daily['inter_esgnb'].notna()].copy()
    
    print(f"\nStep 1 - Daily Aggregation (MAX per day):")
    print(f"  Total valid days (not null): {len(daily)}")
    
    print(f"\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['inter_esgnb']:.6f} ({row['inter_esgnb']*100:.4f}%)")
    
    # Apply interval logic (every 2 days from end, simple)
    display_data = apply_interval_logic_simple(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['inter_esgnb'].values * 100  # Convert to percentage
    
    # Plot BOLD smooth line WITH CLIPPING
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            # Use k=2 (quadratic) instead of k=3 (cubic) for less overshoot
            spl = make_interp_spline(x_data, values, k=2)
            values_smooth = spl(x_smooth)
            
            # Clip values to valid range: 0% to 120%
            values_smooth = np.clip(values_smooth, 0, 120)
            
            ax.plot(x_smooth, values_smooth, color='#1f77b4', linewidth=3.5, 
                   zorder=20, solid_capstyle='round')
        except:
            ax.plot(x_data, values, color='#1f77b4', linewidth=3.5, 
                   zorder=20, solid_capstyle='round')
    else:
        ax.plot(x_data, values, color='#1f77b4', linewidth=3.5, 
               zorder=20, solid_capstyle='round')
    
    # Set y-axis: 0% to 120% with interval 20%, hide 120%
    ax.set_ylim(0, 120)
    yticks = np.arange(0, 121, 20)
    ax.set_yticks(yticks)
    
    # HIDE label 120% (top padding)
    yticklabels = [f'{int(y)}%' if abs(y - 120) > 0.1 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting
    ax.set_title('inter_esgnb_pscell_change', fontweight='bold', fontsize=14)
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
    output_file = f'tests/inter_esgnb_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("INTER ESGNB CHART TEST")
        print("="*60)
        
        # TEMPORARY: use CSV if database is down
        df = get_inter_esgnb_data(use_csv=True)
        print(f"\nTotal records: {len(df)}")
        
        plot_inter_esgnb(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
