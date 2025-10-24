"""
Test script untuk chart Total Traffic (Area Chart)
Quick testing tanpa generate seluruh PPT
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Database config
DB_CONFIG = {
    'host': '1.tcp.ap.ngrok.io',
    'port': 21039,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'option88'
}

def get_traffic_data():
    """Fetch traffic data"""
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
        value = daily_data.iloc[current_idx]['traffic_5g']
        print(f"✓ Index {current_idx}: {current_date.strftime('%Y-%m-%d')} - {value:.2f} GB - INCLUDED")
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

def plot_traffic(df):
    """Plot Total Traffic chart (AREA CHART)"""
    
    # Aggregate by date (MAX per day - BUKAN SUM!)
    daily = df.groupby('date_column').agg({'traffic_5g': 'max'}).reset_index()
    
    # Filter: keep NOT NULL (zero is VALID!)
    daily = daily[daily['traffic_5g'].notna()].copy()
    
    print(f"\nStep 1 - Daily Aggregation (MAX per day):")
    print(f"  Total valid days (not null): {len(daily)}")
    print(f"  Date range: {daily['date_column'].min()} to {daily['date_column'].max()}")
    
    print(f"\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['traffic_5g']:.2f} GB")
    
    # Apply interval logic with gap detection
    display_data = apply_interval_logic_with_gap(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['traffic_5g'].values  # Already in GB
    
    # Plot AREA CHART (penuh/solid dengan fill)
    ax.fill_between(x_data, values, alpha=0.7, color='#17516d', zorder=10)
    ax.plot(x_data, values, color='#17516d', linewidth=3.5, zorder=20, solid_capstyle='round')
    
    # Set y-axis: 0 to 50,000 GB with interval 5,000
    ax.set_ylim(0, 50000)
    yticks = np.arange(0, 51000, 5000)
    ax.set_yticks(yticks)
    
    # Format y-axis labels: HIDE 50,000 (top padding)
    from matplotlib.ticker import FuncFormatter
    def format_y_axis(y, _):
        if abs(y - 50000) < 100:  # Hide 50,000
            return ''
        return f'{int(y):,}'
    
    ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting with TRANSPARENT grid and ticks
    ax.set_title('Total Traffic - 5G (AREA CHART)', fontweight='bold', fontsize=14)
    ax.set_ylabel('GB', fontsize=10)
    
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
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/traffic_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("TOTAL TRAFFIC CHART TEST (AREA CHART)")
        print("="*60)
        
        df = get_traffic_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_traffic(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
