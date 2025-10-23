"""
Data processing utilities
"""
import pandas as pd
import numpy as np

def aggregate_daily_data(df, metrics):
    """
    Aggregate data by date with max aggregation
    Only include days where at least one value > 0
    Returns ALL valid days (not skipping any)
    
    Args:
        df (pd.DataFrame): Raw data
        metrics (dict): Dictionary of column names and aggregation functions
        
    Returns:
        pd.DataFrame: Aggregated daily data (days with all zero values are excluded)
    """
    # First, aggregate by date
    daily_agg = df.groupby('date_column').agg(metrics).reset_index()
    
    # Filter out days where ALL metric values are 0 or NaN
    # Keep days where at least one metric has a value > 0
    metric_cols = list(metrics.keys())
    
    # Create mask: keep row if ANY column > 0
    mask = (daily_agg[metric_cols] > 0).any(axis=1)
    
    # Apply filter
    result = daily_agg[mask].copy()
    
    print(f"Daily aggregation: {len(daily_agg)} total days, {len(result)} days with valid data (non-zero)")
    
    return result

def aggregate_availability_data(df, avail_column, days_back=35):
    """
    Special aggregation for Availability chart
    Shows ALL dates in the range (max_date - days_back to max_date)
    Only includes days where availability > 0
    Returns EVERY valid day (no skipping)
    
    Args:
        df (pd.DataFrame): Raw data
        avail_column (str): Availability column name
        days_back (int): Number of days in range
        
    Returns:
        pd.DataFrame: Daily availability data with all valid dates in range
    """
    # Get max date
    max_date = df['date_column'].max()
    start_date = max_date - pd.Timedelta(days=days_back)
    
    # Aggregate availability by date (max value per day)
    daily_avail = df.groupby('date_column').agg({
        avail_column: 'max'
    }).reset_index()
    
    # Filter: only dates within range
    daily_avail = daily_avail[
        (daily_avail['date_column'] >= start_date) & 
        (daily_avail['date_column'] <= max_date)
    ].copy()
    
    # Filter: only keep days where availability > 0
    result = daily_avail[daily_avail[avail_column] > 0].copy()
    
    print(f"Availability data: {(max_date - start_date).days + 1} days in range, {len(result)} days with valid data (>0)")
    
    return result

def get_date_range_data(df, days_back=35):
    """
    Get data for specific date range (last N days from max date)
    
    Args:
        df (pd.DataFrame): Input dataframe with date_column
        days_back (int): Number of days to look back
        
    Returns:
        tuple: (filtered_df, start_date, end_date)
    """
    if len(df) == 0:
        return df, None, None
    
    # Get max date
    max_date = df['date_column'].max()
    
    # Calculate start date (max_date - days_back)
    start_date = max_date - pd.Timedelta(days=days_back)
    
    # Filter data within range
    filtered = df[df['date_column'] >= start_date].copy()
    
    return filtered, start_date, max_date

def interpolate_availability(data, column, threshold=0):
    """
    Interpolate missing availability values
    ONLY for visualization smoothing, not for data filtering
    
    Args:
        data (pd.DataFrame): Data with availability column
        column (str): Column name to interpolate
        threshold (float): Threshold below which values are considered missing
        
    Returns:
        pd.DataFrame: Data with interpolated values
    """
    result = data.copy()
    
    # Replace values <= threshold with NaN
    result.loc[result[column] <= threshold, column] = np.nan
    
    # Interpolate missing values (linear)
    result[column] = result[column].interpolate(method='linear')
    
    # Fill remaining NaN (at start/end)
    result[column] = result[column].fillna(method='ffill').fillna(method='bfill')
    
    return result

def get_every_nth_row(df, n=2):
    """
    Get every nth row from dataframe
    
    Args:
        df (pd.DataFrame): Input dataframe
        n (int): Take every nth row
        
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    return df.iloc[::n]

def validate_daily_data(df, metric_columns):
    """
    Validate that daily data has at least one non-zero value
    
    Args:
        df (pd.DataFrame): Daily aggregated data
        metric_columns (list): List of metric column names to check
        
    Returns:
        pd.DataFrame: Validated data with only valid days
    """
    # Create mask: keep row if ANY metric column > 0
    mask = (df[metric_columns] > 0).any(axis=1)
    
    valid_data = df[mask].copy()
    
    print(f"Data validation: {len(df)} days total, {len(valid_data)} days with valid data, {len(df) - len(valid_data)} days skipped")
    
    return valid_data

def aggregate_accessibility_data(df, access_column, days_back=35, interval=2):
    """
    Special aggregation for Accessibility chart
    Shows dates with EVERY 2nd DAY interval, counting from LAST date (newest)
    If a date is skipped (null/zero), the interval becomes 4 days
    
    Args:
        df (pd.DataFrame): Raw data
        access_column (str): Accessibility column name
        days_back (int): Number of days in range
        interval (int): Show every Nth day (default: 2)
        
    Returns:
        pd.DataFrame: Daily accessibility data with interval logic
    """
    # Get max date
    max_date = df['date_column'].max()
    start_date = max_date - pd.Timedelta(days=days_back)
    
    # Aggregate accessibility by date (max value per day)
    daily_access = df.groupby('date_column').agg({
        access_column: 'max'
    }).reset_index()
    
    # Filter: only dates within range
    daily_access = daily_access[
        (daily_access['date_column'] >= start_date) & 
        (daily_access['date_column'] <= max_date)
    ].copy()
    
    # Filter: only keep days where accessibility > 0
    valid_data = daily_access[daily_access[access_column] > 0].copy()
    
    if len(valid_data) == 0:
        print(f"Accessibility: No valid data in range")
        return valid_data
    
    # Apply interval logic: every 2 days, COUNT FROM END (newest data)
    result_indices = []
    current_idx = len(valid_data) - 1  # Start from LAST index
    
    while current_idx >= 0:
        result_indices.append(current_idx)
        
        # Try to jump by interval (2 days) BACKWARD
        next_idx = current_idx - interval
        
        # Check if next_idx exists
        if next_idx >= 0:
            # Check actual date difference
            current_date = valid_data.iloc[current_idx]['date_column']
            next_date = valid_data.iloc[next_idx]['date_column']
            days_diff = (current_date - next_date).days
            
            # If gap is larger than expected (means some days were skipped)
            # Jump further by interval (becomes 4 days total)
            if days_diff > interval * 1.5:  # Allow some tolerance
                # Data was skipped, jump by another interval
                next_idx = next_idx - interval
            
            current_idx = next_idx
        else:
            # No more data
            break
    
    # Reverse to get chronological order (oldest to newest)
    result_indices.reverse()
    result = valid_data.iloc[result_indices].copy()
    
    print(f"Accessibility data: {(max_date - start_date).days + 1} days in range")
    print(f"  - {len(valid_data)} days with valid data (>0)")
    print(f"  - {len(result)} days displayed (every 2 days from END)")
    
    return result

def aggregate_cdr_data(df, cdr_column, days_back=35, interval=2):
    """
    Special aggregation for Call Drop Rate chart
    Shows dates with EVERY 2nd DAY interval, counting from LAST date (newest)
    NO exception for zero values (zero is valid)
    Skip only if data is truly missing/null
    
    Args:
        df (pd.DataFrame): Raw data
        cdr_column (str): CDR column name
        days_back (int): Number of days in range
        interval (int): Show every Nth day (default: 2)
        
    Returns:
        pd.DataFrame: Daily CDR data with interval logic
    """
    # Get max date
    max_date = df['date_column'].max()
    start_date = max_date - pd.Timedelta(days=days_back)
    
    # Aggregate CDR by date (max value per day)
    daily_cdr = df.groupby('date_column').agg({
        cdr_column: 'max'
    }).reset_index()
    
    # Filter: only dates within range
    daily_cdr = daily_cdr[
        (daily_cdr['date_column'] >= start_date) & 
        (daily_cdr['date_column'] <= max_date)
    ].copy()
    
    # Filter: only keep days where CDR is NOT NULL (zero is OK!)
    valid_data = daily_cdr[
        (daily_cdr[cdr_column].notna()) & 
        (daily_cdr[cdr_column] >= 0)
    ].copy()
    
    if len(valid_data) == 0:
        print(f"CDR: No valid data in range")
        return valid_data
    
    # Apply interval logic: every 2 days, COUNT FROM END (newest data)
    # Simple: take every Nth row FROM THE END
    n_total = len(valid_data)
    
    # Calculate indices from end: n-1, n-3, n-5, ... (counting backward)
    result_indices = list(range(n_total - 1, -1, -interval))
    
    # Reverse to get chronological order
    result_indices.reverse()
    result = valid_data.iloc[result_indices].copy()
    
    print(f"CDR data: {(max_date - start_date).days + 1} days in range")
    print(f"  - {len(valid_data)} days with valid data (not null, >= 0)")
    print(f"  - {len(result)} days displayed (every {interval} days from END)")
    
    return result
