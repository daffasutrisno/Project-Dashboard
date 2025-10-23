"""
Configuration module
"""
from .database import DB_CONFIG
from .chart_styles import (
    apply_chart_styles, 
    COLORS, 
    CHART_SIZE, 
    BORDER_WIDTH, 
    LINE_WIDTH, 
    LINE_WIDTH_BOLD  # Add this
)

__all__ = [
    'DB_CONFIG', 
    'apply_chart_styles', 
    'COLORS', 
    'CHART_SIZE', 
    'BORDER_WIDTH', 
    'LINE_WIDTH', 
    'LINE_WIDTH_BOLD'  # Add this
]
