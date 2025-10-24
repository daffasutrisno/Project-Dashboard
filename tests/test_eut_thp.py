"""
Test script untuk chart EUT vs DL User Thp (Dual Line Chart)
Using: g5_eut_bhv vs g5_userdl_thp
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

def get_eut_thp_data():
    """Fetch EUT and DL User Thp data"""
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

def plot_eut_thp(df):
    """Plot EUT vs DL User Thp chart (DUAL LINE CHART)"""
    
    # Aggregate by date (MAX per day for both)
    daily = df.groupby('date_column').agg({
        'g5_eut_bhv': 'max',      # Line 1: EUT (follows)
        'g5_userdl_thp': 'max'    # Line 2: DL User Thp (PRIMARY)
    }).reset_index()
    
    # Filter based on Thp (PRIMARY) - skip zero/null (like Availability)
    daily = daily[
        (daily['g5_userdl_thp'].notna()) & 
        (daily['g5_userdl_thp'] > 0)
    ].copy()
    
    print(f"\nData points (based on Thp PRIMARY): {len(daily)}")
    print(f"Date range: {daily['date_column'].min()} to {daily['date_column'].max()}")
    
    # Show all data
    print("\nAll valid days:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: eut={row['g5_eut_bhv']:.2f}, thp={row['g5_userdl_thp']:.2f}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(daily)
    x_data = np.arange(n_points)
    
    # Line 2: g5_userdl_thp (PRIMARY - orange) - plot first (behind)
    values2 = daily['g5_userdl_thp'].values
    
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            spl2 = make_interp_spline(x_data, values2, k=3)
            values_smooth2 = spl2(x_smooth)
            ax.plot(x_smooth, values_smooth2, color='#ff7f0e', linewidth=3.5, 
                   zorder=19, solid_capstyle='round', label='g5_userdl_thp')
        except:
            ax.plot(x_data, values2, color='#ff7f0e', linewidth=3.5, 
                   zorder=19, solid_capstyle='round', label='g5_userdl_thp')
    
    # Line 1: g5_eut_bhv (FOLLOWS - blue) - only where data exists
    values1 = daily['g5_eut_bhv'].values
    eut_mask = (pd.Series(values1).notna()) & (pd.Series(values1) > 0)
    eut_indices = np.where(eut_mask)[0]
    
    if len(eut_indices) > 0:
        eut_x = x_data[eut_indices]
        eut_y = values1[eut_indices]
        
        print(f"\nEUT data points: {len(eut_indices)} (follows Thp index)")
        
        if len(eut_indices) > 3:
            x_smooth_eut = np.linspace(eut_x.min(), eut_x.max(), 300)
            try:
                spl1 = make_interp_spline(eut_x, eut_y, k=3)
                values_smooth1 = spl1(x_smooth_eut)
                ax.plot(x_smooth_eut, values_smooth1, color='#1f77b4', linewidth=3.5, 
                       zorder=20, solid_capstyle='round', label='g5_eut_bhv')
            except:
                ax.plot(eut_x, eut_y, color='#1f77b4', linewidth=3.5, 
                       zorder=20, solid_capstyle='round', label='g5_eut_bhv')
    
    # Legend
    ax.legend(loc='upper left', fontsize=9)
    
    # Y-axis: 0 to 120 with interval 20, hide 120
    ax.set_ylim(0, 120)
    yticks = np.arange(0, 121, 20)
    ax.set_yticks(yticks)
    
    # HIDE label 120 (top padding)
    yticklabels = [f'{int(y)}' if abs(y - 120) > 0.1 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels with YEAR
    tick_positions = x_data
    tick_labels = [daily['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting with TRANSPARENT grid and ticks
    ax.set_title('EUT vs DL User Thp - 5G (DUAL LINE)', fontweight='bold', fontsize=14)
    ax.set_ylabel('Value', fontsize=10)
    
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
    output_file = f'tests/eut_thp_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("EUT vs DL USER THP CHART TEST (DUAL LINE)")
        print("="*60)
        
        df = get_eut_thp_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_eut_thp(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
