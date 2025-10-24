"""
Auto-generate KPI Monitoring Dashboard PowerPoint
Slide 1: 5G East Java
Slide 2: 4G East Java
Data: Per minggu terbaru (7 hari)
"""

from config import apply_chart_styles
from data import get_data_from_db
from generators import generate_5g_charts, generate_4g_charts
from presentation import PPTBuilder

def create_weekly_dashboard(days_back=7):
    """
    Create weekly KPI monitoring dashboard
    
    Args:
        days_back (int): Number of days to fetch from database
        
    Returns:
        str: Output filename
    """
    # Apply chart styling
    apply_chart_styles()
    
    # Fetch data
    print("Fetching data from database...")
    df = get_data_from_db(days_back=days_back)
    print(f"Data fetched: {len(df)} records")
    print(f"Date range: {df['date_column'].min()} to {df['date_column'].max()}")
    
    # Generate charts (USING SAME GENERATORS AS MONTHLY)
    print("\nGenerating 5G charts...")
    charts_5g = generate_5g_charts(df)
    
    print("Generating 4G charts...")
    charts_4g = generate_4g_charts(df)
    
    # Create presentation
    print("\nCreating PowerPoint presentation...")
    ppt = PPTBuilder()
    ppt.create_5g_slide(charts_5g, title='KPI MONITORING 5G EAST JAVA (WEEKLY)')
    ppt.create_4g_slide(charts_4g, title='KPI MONITORING 4G EAST JAVA (WEEKLY)')
    
    output_file = ppt.save(prefix='Weekly')
    print(f"\n✓ Presentation saved as: {output_file}")
    
    return output_file

if __name__ == "__main__":
    try:
        create_weekly_dashboard()
        print("\n✓ Dashboard generated successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
