"""
Database data fetching
"""
import psycopg2
import pandas as pd
from config.database import DB_CONFIG

def get_data_from_db(days_back=35):
    """
    Fetch data from database for last N days
    
    The date range is calculated from the maximum date in the database,
    going back N days. Days with no data are automatically excluded.
    
    Args:
        days_back (int): Number of days to fetch from most recent date
        
    Returns:
        pd.DataFrame: Raw data from database
    """
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Query: get last N days from max date
    # This ensures we always get data from (max_date - N days) to max_date
    # Even if some days in between have no data
    query = f"""
    SELECT *
    FROM cluster_5g 
    WHERE date_column >= (SELECT MAX(date_column)::date - INTERVAL '{days_back} days' FROM cluster_5g)
    ORDER BY date_column ASC, nc_5g
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    df['date_column'] = pd.to_datetime(df['date_column'])
    
    print(f"Date range in database: {df['date_column'].min()} to {df['date_column'].max()}")
    print(f"Total records fetched: {len(df)}")
    print(f"Unique dates: {df['date_column'].nunique()}")
    
    return df
