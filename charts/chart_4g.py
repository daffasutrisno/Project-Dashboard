"""
4G specific charts (same structure as 5G)
"""
from .chart_5g import (
    AvailabilityChart5G as AvailabilityChart4G,
    LineChart5G as LineChart4G,
    AreaChart5G as AreaChart4G,
    BarChart5G as BarChart4G,
    DualLineChart5G as DualLineChart4G,
    StackedBarChart5G as StackedBarChart4G
)

# 4G charts use the same implementation as 5G
# Can be customized here if needed
