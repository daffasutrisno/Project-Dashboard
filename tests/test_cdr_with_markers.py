"""
Test CDR dengan marker khusus untuk nilai zero
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

def get_cdr_data():
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

def plot_cdr_with_markers(df):
    """Plot CDR with special markers for zero values"""
    
    daily = df.groupby('date_column').agg({'g5_cdr': 'max'}).reset_index()
    daily = daily[daily['g5_cdr'] >= 0].copy()
    
    print(f"\nData points: {len(daily)}")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    n_points = len(daily)
    x_data = np.arange(n_points)
    values = daily['g5_cdr'].values * 100
    
    # Offset zero values
    ZERO_OFFSET = 0.0001  # 0.0001% offset for visibility
    values_display = values.copy()
    zero_mask = values == 0
    values_display[zero_mask] = ZERO_OFFSET
    
    # Find zero positions
    zero_indices = np.where(zero_mask)[0]
    
    # Plot smooth line
    if n_points > 3:
        x_smooth = np.linspace(0, n_points - 1, 300)
        try:
            spl = make_interp_spline(x_data, values_display, k=3)
            values_smooth = spl(x_smooth)
            values_smooth = np.maximum(values_smooth, 0)
            ax.plot(x_smooth, values_smooth, color='#1f77b4', linewidth=2, zorder=10)
        except:
            ax.plot(x_data, values_display, color='#1f77b4', linewidth=2, zorder=10)
    
    # Add markers at zero points for emphasis
    if len(zero_indices) > 0:
        ax.scatter(zero_indices, values_display[zero_indices], 
                  color='red', s=50, marker='o', zorder=15, 
                  label=f'Zero values ({len(zero_indices)})', alpha=0.7)
        ax.legend(loc='upper right', fontsize=8)
        print(f"\n⚠️  {len(zero_indices)} zero values marked with red circles")
    
    # Set y-axis
    ax.set_ylim(0, 0.016)
    yticks = np.arange(0, 0.017, 0.002)
    ax.set_yticks(yticks)
    yticklabels = [f'{y:.3f}%' if abs(y - 0.016) > 0.0001 else '' for y in yticks]
    ax.set_yticklabels(yticklabels)
    
    ax.set_xlim(-0.5, n_points - 0.5)
    
    tick_positions = x_data
    tick_labels = [daily['date_column'].iloc[i].strftime('%d/%m') for i in range(n_points)]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    ax.set_title('Call Drop Rate - 5G (Zero Offset + Markers)', fontweight='bold', fontsize=14)
    ax.set_ylabel('%', fontsize=10)
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, color='lightgray', zorder=1)
    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-', alpha=0.25, zorder=2)
    
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.6)
        spine.set_alpha(0.4)
    
    ax.tick_params(axis='both', which='both', width=0.5, length=3, color='gray', 
                  direction='out', labelsize=8, pad=2)
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_alpha(0.8)
    
    plt.tight_layout()
    
    output_file = f'tests/cdr_with_markers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    try:
        print("="*60)
        print("CDR CHART WITH ZERO MARKERS")
        print("="*60)
        
        df = get_cdr_data()
        plot_cdr_with_markers(df)
        
        print("\n✓ Test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
