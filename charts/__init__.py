"""
Charts module
"""
from .chart_5g import (
    AvailabilityChart5G,
    LineChart5G,
    AreaChart5G,
    BarChart5G,
    DualLineChart5G,
    StackedBarChart5G,
    CDRChart5G  # Add this
)
from .chart_4g import (
    AvailabilityChart4G,
    LineChart4G,
    AreaChart4G,
    BarChart4G,
    DualLineChart4G,
    StackedBarChart4G
)

__all__ = [
    'AvailabilityChart5G', 'LineChart5G', 'AreaChart5G', 'BarChart5G',
    'DualLineChart5G', 'StackedBarChart5G', 'CDRChart5G',  # Add CDRChart5G
    'AvailabilityChart4G', 'LineChart4G', 'AreaChart4G', 'BarChart4G',
    'DualLineChart4G', 'StackedBarChart4G'
]
