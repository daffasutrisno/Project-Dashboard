"""
Test script untuk chart User 5G (Bar Chart)
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

def get_user5g_data():
    """Fetch User 5G data"""
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
    No gap checking, like CDR
    """
    n_total = len(daily_data)
    result_indices = list(range(n_total - 1, -1, -interval))
    result_indices.reverse()
    
    print("\nApplying SIMPLE EVERY 2 DAYS logic (FROM END):")
    print("-" * 70)
    
    for i, idx in enumerate(result_indices):
        date = daily_data.iloc[idx]['date_column']
        value = daily_data.iloc[idx]['sum_en_dc_user_5g_wd']
        print(f"✓ Display {i+1}: Index {idx} - {date.strftime('%Y-%m-%d')} - {value:.0f} users")
    
    return daily_data.iloc[result_indices]

def plot_user5g(df):
    """Plot User 5G chart (BAR CHART)"""
    
    # Aggregate by date (MAX per day - NOT SUM!)
    daily = df.groupby('date_column').agg({'sum_en_dc_user_5g_wd': 'max'}).reset_index()
    
    # Filter: keep NOT NULL (zero is VALID!)
    daily = daily[daily['sum_en_dc_user_5g_wd'].notna()].copy()
    
    print(f"\nStep 1 - Daily Aggregation (MAX per day):")
    print(f"  Total valid days (not null): {len(daily)}")
    
    print(f"\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['sum_en_dc_user_5g_wd']:.0f} users")
    
    # Apply interval logic (every 2 days from end, simple)
    display_data = apply_interval_logic_simple(daily, interval=2)
    
    print(f"\nStep 2 - After Interval Logic:")
    print(f"  Days to display: {len(display_data)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(display_data)
    x_data = np.arange(n_points)
    values = display_data['sum_en_dc_user_5g_wd'].values
    
    # Plot BAR CHART
    ax.bar(x_data, values, color='#1f77b4', width=0.8, zorder=10)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [display_data['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting with TRANSPARENT grid and ticks
    ax.set_title('User 5G (BAR CHART)', fontweight='bold', fontsize=14)
    ax.set_ylabel('Users', fontsize=10)
    
    # Y-axis: 0 to 400,000 with interval 50,000, hide 400,000
    ax.set_ylim(0, 400000)
    yticks = np.arange(0, 401000, 50000)
    ax.set_yticks(yticks)
    
    # Format y-axis labels: HIDE 400,000 (top padding)
    from matplotlib.ticker import FuncFormatter
    def format_y_axis(y, _):
        if abs(y - 400000) < 100:  # Hide 400,000
            return ''
        return f'{int(y/1000)}K'  # Format as K (thousands)
    
    ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))
    
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
    output_file = f'tests/user5g_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("USER 5G CHART TEST (BAR CHART)")
        print("="*60)
        
        df = get_user5g_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_user5g(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
