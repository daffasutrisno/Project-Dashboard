"""
4G Dashboard generator
"""
import pandas as pd
from utils import (
    aggregate_daily_data, 
    aggregate_availability_data,
    interpolate_availability
)
from charts import (
    AvailabilityChart4G, LineChart4G, AreaChart4G, 
    BarChart4G, StackedBarChart4G
)

def generate_4g_charts(df):
    """Generate all 4G charts as individual images"""
    
    # Chart 1: Availability - SPECIAL HANDLING
    # Shows ALL valid dates (every day with data > 0)
    avail_data = aggregate_availability_data(df, 'g4_avail_auto', days_back=35)
    
    # Additional filter for 4G: only show values >= 0.99
    avail_data = avail_data[avail_data['g4_avail_auto'] >= 0.99].copy()
    
    # Interpolate for smooth line
    avail_data = interpolate_availability(avail_data, 'g4_avail_auto', threshold=0.99)
    
    # Use ALL valid days (removed [::2] slicing)
    chart = AvailabilityChart4G(
        avail_data['date_column'],
        avail_data['g4_avail_auto'],
        'Availability',
        '%'
    )
    charts = {'availability': chart.create()}
    
    # For OTHER charts: use standard aggregation
    metrics_4g = {
        's1_failure': 'max',
        'rrc_ue': 'max',
        'traffic_4g': 'sum',
        'eut_4g_bh': 'max',
        'dl_prb_util': 'max',
        'cqi_bh': 'max',
        'traffic_3id': 'sum',
        'traffic_im3': 'sum',
        'user_3id': 'sum',
        'user_im3': 'sum',
        'dl_user_thp_bhv': 'max'
    }
    
    # Aggregate - returns ALL valid days
    daily_data = aggregate_daily_data(df, metrics_4g)
    
    print(f"4G charts will use ALL {len(daily_data)} valid days (no skipping)")
    
    # Use ALL dates
    dates = daily_data['date_column']
    
    # Chart 2: S1SR
    chart = LineChart4G(
        dates,
        (1 - daily_data['s1_failure']) * 100,
        'S1SR',
        '%'
    )
    charts['s1sr'] = chart.create()
    
    # Chart 3: RRC Conn User
    chart = LineChart4G(
        dates,
        daily_data['rrc_ue'],
        'RRC Conn User',
        'Users'
    )
    charts['rrc_user'] = chart.create()
    
    # Chart 4: Traffic 4G
    chart = AreaChart4G(
        dates,
        daily_data['traffic_4g'],
        'Traffic 4G (GB)',
        'GB'
    )
    charts['traffic'] = chart.create()
    
    # Chart 5: EUT
    chart = LineChart4G(
        dates,
        daily_data['eut_4g_bh'],
        'EUT',
        'Mbps',
        color='#ff7f0e'
    )
    charts['eut'] = chart.create()
    
    # Chart 6: DL PRB Util
    chart = BarChart4G(
        dates,
        daily_data['dl_prb_util'] * 100,
        'DL PRB Util',
        '%'
    )
    charts['prb_util'] = chart.create()
    
    # Chart 7: CQI
    chart = LineChart4G(
        dates,
        daily_data['cqi_bh'],
        'CQI',
        'CQI',
        color='#ff7f0e'
    )
    charts['cqi'] = chart.create()
    
    # Chart 8: QPSK
    chart = LineChart4G(
        dates,
        daily_data['dl_user_thp_bhv'],
        'QPSK',
        'Mbps'
    )
    charts['qpsk'] = chart.create()
    
    # Chart 9: Traffic 4G - 5G
    chart = StackedBarChart4G(
        dates,
        daily_data['traffic_3id'],
        daily_data['traffic_im3'],
        'Traffic 4G - 5G',
        'GB',
        'traffic_3id',
        'traffic_im3'
    )
    charts['traffic_split'] = chart.create()
    
    # Chart 10: Ratio Traffic 4G - 5G
    total_traffic = daily_data['traffic_3id'] + daily_data['traffic_im3']
    ratio_3id = (daily_data['traffic_3id'] / total_traffic * 100).fillna(0)
    ratio_im3 = (daily_data['traffic_im3'] / total_traffic * 100).fillna(0)
    
    chart = StackedBarChart4G(
        dates,
        ratio_3id,
        ratio_im3,
        'Ratio traffic 4G - 5G',
        '%',
        '3ID',
        'IM3'
    )
    charts['ratio_traffic'] = chart.create()
    
    # Chart 11: RRC Conn 4G - 5G
    chart = StackedBarChart4G(
        dates,
        daily_data['user_3id'],
        daily_data['user_im3'],
        'RRC Conn 4G - 5G',
        'Users',
        'user_3id',
        'user_im3'
    )
    charts['user_split'] = chart.create()
    
    # Chart 12: Ratio RRC Conn 4G - 5G
    total_users = daily_data['user_3id'] + daily_data['user_im3']
    ratio_user_3id = (daily_data['user_3id'] / total_users * 100).fillna(0)
    ratio_user_im3 = (daily_data['user_im3'] / total_users * 100).fillna(0)
    
    chart = StackedBarChart4G(
        dates,
        ratio_user_3id,
        ratio_user_im3,
        'RRC Conn 4G - 5G',
        '%',
        'user_3ID',
        'user_IM3'
    )
    charts['ratio_user'] = chart.create()
    
    return charts
