"""
Test script untuk chart Availability
Quick testing tanpa generate seluruh PPT
"""

import sys
import os

# Add project root to path
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

def get_availability_data():
    """Fetch availability data"""
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

def plot_availability(df):
    """Plot availability chart"""
    
    # Aggregate by date (max per day)
    daily = df.groupby('date_column').agg({'avail_auto_5g': 'max'}).reset_index()
    
    # Filter: only keep days with availability > 0
    daily = daily[daily['avail_auto_5g'] > 0].copy()
    
    print(f"\nData points: {len(daily)}")
    print(f"Date range: {daily['date_column'].min()} to {daily['date_column'].max()}")
    print(f"Showing ALL {len(daily)} valid days - EVERY DAY")
    
    # Show all data
    print("\nAll data points:")
    for idx, row in daily.iterrows():
        print(f"  {row['date_column'].strftime('%Y-%m-%d')}: {row['avail_auto_5g']:.4f} ({row['avail_auto_5g']*100:.2f}%)")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use numeric x-axis for equal spacing
    n_points = len(daily)
    x_data = np.arange(n_points)
    values = daily['avail_auto_5g'].values * 100
    
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
    
    # Set y-axis: 99.00 to 100.20
    ax.set_ylim(99.00, 100.20)
    yticks = np.arange(99.00, 100.21, 0.20)
    ax.set_yticks(yticks)
    yticklabels = [f'{y:.2f}%' if abs(y - 100.20) > 0.01 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    # Set x-axis
    ax.set_xlim(-0.5, n_points - 0.5)
    
    # X-axis labels - SHOW ALL DAYS with YEAR
    tick_positions = x_data
    tick_labels = [daily['date_column'].iloc[i].strftime('%d/%m/%Y') for i in range(n_points)]
    
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Formatting
    ax.set_title('Availability Test - 5G (EVERY DAY)', fontweight='bold', fontsize=14)
    ax.set_ylabel('%', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    
    # Save
    output_file = f'tests/availability_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    # Show
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("AVAILABILITY CHART TEST")
        print("="*60)
        
        df = get_availability_data()
        print(f"\nTotal records: {len(df)}")
        
        plot_availability(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
