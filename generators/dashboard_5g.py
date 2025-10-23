"""
5G Dashboard generator
"""
from utils import (
    aggregate_daily_data, 
    aggregate_availability_data,
    aggregate_accessibility_data,
    aggregate_cdr_data,  # NEW
    interpolate_availability, 
    validate_daily_data
)
from charts import (
    AvailabilityChart5G, LineChart5G, AreaChart5G, 
    BarChart5G, DualLineChart5G, CDRChart5G
)

def generate_5g_charts(df):
    """Generate all 5G charts as individual images"""
    
    charts = {}
    
    # Chart 1: Availability - EVERY DAY (LOCKED)
    avail_data = aggregate_availability_data(df, 'avail_auto_5g', days_back=35)
    avail_data = interpolate_availability(avail_data, 'avail_auto_5g', threshold=0)
    
    chart = AvailabilityChart5G(
        avail_data['date_column'],
        avail_data['avail_auto_5g'],
        'Availability',
        '%'
    )
    charts['availability'] = chart.create()
    
    # Chart 2: Accessibility - EVERY 2 DAYS (or 4 if gap) (LOCKED)
    access_data = aggregate_accessibility_data(df, 'da_5g', days_back=35, interval=2)
    
    chart = LineChart5G(
        access_data['date_column'],
        access_data['da_5g'] * 100,
        'Accessibility',
        '%',
        ylim=(96, 101),
        ytick_format='{:.2f}%',
        hide_top_label=True
    )
    charts['accessibility'] = chart.create()
    
    # Chart 3: Call Drop Rate - EVERY 2 DAYS (simple, no gap checking)
    cdr_data = aggregate_cdr_data(df, 'g5_cdr', days_back=35, interval=2)
    
    chart = CDRChart5G(
        cdr_data['date_column'],
        cdr_data['g5_cdr'],
        'Call Drop Rate',
        '%'
    )
    charts['cdr'] = chart.create()
    
    # For OTHER charts: use standard aggregation
    # Returns ALL valid days (not every 2 days anymore)
    metrics_5g = {
        'da_5g': 'max',
        'g5_cdr': 'max',
        'sgnb_addition_sr': 'max',
        'traffic_5g': 'sum',
        'g5_userdl_thp': 'max',
        'sum_en_dc_user_5g_wd': 'max',
        'g5_dlprb_util': 'max',
        'inter_esgnb': 'max',
        'intra_esgnb': 'max',
        'inter_sgnb_intrafreq': 'max',
        'intra_sgnb_intrafreq': 'max'
    }
    
    # Aggregate daily data - returns ALL valid days
    daily_data = aggregate_daily_data(df, metrics_5g)
    
    print(f"5G charts will use ALL {len(daily_data)} valid days (no skipping)")
    
    # Use ALL dates (removed [::2] slicing)
    dates = daily_data['date_column']
    data_display = daily_data
    
    # Chart 4: Sgnb addition SR
    chart = LineChart5G(
        dates,
        data_display['sgnb_addition_sr'] * 100,
        'Sgnb addition SR',
        '%',
        ylim=(98, 100.5),
        ytick_format='{:.2f}%'
    )
    charts['sgnb_sr'] = chart.create()
    
    # Chart 5: Total Traffic
    chart = AreaChart5G(
        dates,
        data_display['traffic_5g'],
        'Total Traffic (GB)',
        'GB'
    )
    charts['traffic'] = chart.create()
    
    # Chart 6: EUT vs DL User Thp
    chart = DualLineChart5G(
        dates,
        data_display['traffic_5g'] / 1000,
        data_display['g5_userdl_thp'],
        'EUT vs DL User Thp',
        'Value',
        'traffic_5g',
        'dl_user_thp_5g'
    )
    charts['eut_thp'] = chart.create()
    
    # Chart 7: User 5G
    chart = BarChart5G(
        dates,
        data_display['sum_en_dc_user_5g_wd'],
        'User 5G',
        'Users'
    )
    charts['user_5g'] = chart.create()
    
    # Chart 8: DL PRB Util
    chart = LineChart5G(
        dates,
        data_display['g5_dlprb_util'] * 100,
        'DL PRB Util',
        '%',
        ytick_format='{:.2f}%'
    )
    charts['prb_util'] = chart.create()
    
    # Chart 9: Inter esgNB
    chart = LineChart5G(
        dates,
        data_display['inter_esgnb'] * 100,
        'inter_esgnb_pscell_change',
        '%',
        ylim=(0, 120),
        ytick_format='{:.2f}%'
    )
    charts['inter_esgnb'] = chart.create()
    
    # Chart 10: Intra esgNB
    chart = LineChart5G(
        dates,
        data_display['intra_esgnb'] * 100,
        'intra_esgnb_pscell_change',
        '%',
        ylim=(99.80, 100.00),
        ytick_format='{:.2f}%'
    )
    charts['intra_esgnb'] = chart.create()
    
    # Chart 11: Intra sgNB intrafreq
    chart = LineChart5G(
        dates,
        data_display['intra_sgnb_intrafreq'] * 100,
        'intra_sgnb_intrafreq_pscell_change',
        '%',
        ylim=(99.80, 100.00),
        ytick_format='{:.2f}%'
    )
    charts['intra_sgnb'] = chart.create()
    
    # Chart 12: Inter sgNB intrafreq
    chart = LineChart5G(
        dates,
        data_display['inter_sgnb_intrafreq'] * 100,
        'inter_sgnb_intrafreq_pscell_change',
        '%',
        ylim=(99.0, 100.1),
        ytick_format='{:.2f}%'
    )
    charts['inter_sgnb'] = chart.create()
    
    return charts
