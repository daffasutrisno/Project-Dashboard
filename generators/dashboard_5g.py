"""
5G Dashboard generator
"""
from utils import (
    aggregate_daily_data, 
    aggregate_availability_data,
    aggregate_accessibility_data,
    aggregate_cdr_data,
    aggregate_sgnb_sr_data,
    aggregate_traffic_data,
    aggregate_eut_thp_data,
    aggregate_user5g_data,
    aggregate_prb_util_data,
    aggregate_inter_esgnb_data,
    aggregate_intra_esgnb_data,
    aggregate_intra_sgnb_data,
    aggregate_inter_sgnb_intrafreq_data,  # FIXED NAME
    interpolate_availability, 
    validate_daily_data
)
from charts import (
    AvailabilityChart5G, LineChart5G, AreaChart5G, 
    BarChart5G, DualLineChart5G, CDRChart5G, SgnbSRChart5G, 
    TrafficChart5G, EUTThpChart5G, User5GChart, PRBUtilChart5G  # ADD PRBUtilChart5G
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
    
    # Chart 4: Sgnb addition SR - EVERY 2 DAYS from END with GAP DETECTION (like Accessibility)
    sgnb_data = aggregate_sgnb_sr_data(df, 'sgnb_addition_sr', days_back=35, interval=2)
    
    chart = SgnbSRChart5G(
        sgnb_data['date_column'],
        sgnb_data['sgnb_addition_sr'],
        'Sgnb addition SR',
        '%'
    )
    charts['sgnb_sr'] = chart.create()
    
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
    
    # Chart 5: Total Traffic - EVERY 2 DAYS from END with GAP DETECTION (like Accessibility)
    # Zero is VALID (not skipped)
    traffic_data = aggregate_traffic_data(df, 'traffic_5g', days_back=35, interval=2)
    
    chart = TrafficChart5G(
        traffic_data['date_column'],
        traffic_data['traffic_5g'],
        'Total Traffic (GB)',
        'GB'
    )
    charts['traffic'] = chart.create()
    
    # Chart 6: EUT vs DL User Thp - Thp as PRIMARY index (like Availability)
    # Every day based on thp data, EUT follows
    eut_thp_data = aggregate_eut_thp_data(df, 'g5_eut_bhv', 'g5_userdl_thp', days_back=35)
    
    chart = EUTThpChart5G(
        eut_thp_data['date_column'],
        eut_thp_data['g5_eut_bhv'].values,  # Line 1: EUT (follows)
        eut_thp_data['g5_userdl_thp'].values,  # Line 2: Thp (primary)
        'EUT vs DL User Thp',
        'Value'
    )
    charts['eut_thp'] = chart.create()
    
    # Chart 7: User 5G - EVERY 2 DAYS from END (simple, like CDR)
    # Zero is VALID (not skipped), skip only if null
    user5g_data = aggregate_user5g_data(df, 'sum_en_dc_user_5g_wd', days_back=35, interval=2)
    
    chart = User5GChart(
        user5g_data['date_column'],
        user5g_data['sum_en_dc_user_5g_wd'],
        'User 5G',
        'Users'
    )
    charts['user_5g'] = chart.create()
    
    # Chart 8: DL PRB Util - EVERY 2 DAYS from END with GAP DETECTION (dual Y-axis)
    prb_data = aggregate_prb_util_data(
        df, 'g5_dlprb_util', 'dl_prb_util_5g_count_gt_085', 
        days_back=35, interval=2
    )
    
    chart = PRBUtilChart5G(
        prb_data['date_column'],
        prb_data['g5_dlprb_util'].values,
        prb_data['dl_prb_util_5g_count_gt_085'].values,
        'DL PRB Util',
        'PRB Util (%)',
        '#Cells PRB>85%'
    )
    charts['prb_util'] = chart.create()
    
    # Chart 9: Inter esgNB - EVERY 2 DAYS from END (simple, like CDR)
    inter_esgnb_data = aggregate_inter_esgnb_data(df, 'inter_esgnb', days_back=35, interval=2)
    
    chart = LineChart5G(
        inter_esgnb_data['date_column'],
        inter_esgnb_data['inter_esgnb'] * 100,
        'inter_esgnb_pscell_change',
        '%',
        ylim=(0, 120),
        ytick_format='{:.2f}%',
        hide_top_label=True
    )
    charts['inter_esgnb'] = chart.create()
    
    # Chart 10: Intra esgNB - EVERY 2 DAYS from END with GAP DETECTION
    intra_esgnb_data = aggregate_intra_esgnb_data(df, 'intra_esgnb', days_back=35, interval=2)
    
    chart = LineChart5G(
        intra_esgnb_data['date_column'],
        intra_esgnb_data['intra_esgnb'] * 100,
        'intra_esgnb_pscell_change',
        '%',
        ylim=(99.80, 100.02),
        ytick_format='{:.2f}%',
        hide_top_label=True
    )
    charts['intra_esgnb'] = chart.create()
    
    # Chart 11: Intra sgNB intrafreq - EVERY 2 DAYS from END with GAP DETECTION
    # SAME configuration as Intra esgNB
    intra_sgnb_data = aggregate_intra_sgnb_data(df, 'intra_sgnb_intrafreq', days_back=35, interval=2)
    
    chart = LineChart5G(
        intra_sgnb_data['date_column'],
        intra_sgnb_data['intra_sgnb_intrafreq'] * 100,
        'intra_sgnb_intrafreq_pscell_change',
        '%',
        ylim=(99.80, 100.02),
        ytick_format='{:.2f}%',
        hide_top_label=True
    )
    charts['intra_sgnb'] = chart.create()
    
    # Chart 12: Inter sgNB intrafreq - EVERY 2 DAYS from END with GAP DETECTION
    inter_sgnb_data = aggregate_inter_sgnb_intrafreq_data(df, 'inter_sgnb_intrafreq', days_back=35, interval=2)
    
    chart = LineChart5G(
        inter_sgnb_data['date_column'],
        inter_sgnb_data['inter_sgnb_intrafreq'] * 100,
        'inter_sgnb_intrafreq_pscell_change',
        '%',
        ylim=(99.0, 100.1),
        ytick_format='{:.1f}%',
        hide_top_label=True
    )
    charts['inter_sgnb'] = chart.create()
    
    return charts
