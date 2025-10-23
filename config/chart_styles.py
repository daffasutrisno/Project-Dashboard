"""
Chart styling configuration
"""
import matplotlib.pyplot as plt

def apply_chart_styles():
    """Apply global matplotlib styling with transparent grid and bold lines"""
    plt.rcParams['font.size'] = 9
    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['xtick.labelsize'] = 7
    plt.rcParams['ytick.labelsize'] = 7
    plt.rcParams['legend.fontsize'] = 7
    plt.rcParams['figure.autolayout'] = False
    
    # TRANSPARENT grid for better line visibility
    plt.rcParams['grid.alpha'] = 0.15  # Very transparent
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.color'] = 'lightgray'
    
    # THIN and TRANSPARENT tick marks
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['ytick.major.width'] = 0.5
    plt.rcParams['xtick.minor.width'] = 0.4
    plt.rcParams['ytick.minor.width'] = 0.4
    plt.rcParams['xtick.major.size'] = 3
    plt.rcParams['ytick.major.size'] = 3
    plt.rcParams['xtick.color'] = 'gray'
    plt.rcParams['ytick.color'] = 'gray'
    plt.rcParams['xtick.direction'] = 'out'
    plt.rcParams['ytick.direction'] = 'out'
    
    # Backgrounds
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['savefig.facecolor'] = 'white'
    plt.rcParams['savefig.transparent'] = False
    
    # Transparent axes
    plt.rcParams['axes.edgecolor'] = 'gray'
    plt.rcParams['axes.linewidth'] = 0.6

# Chart colors
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'area': '#17516d',
    'background': 'white',
    'border': 'black'
}

# Chart dimensions
CHART_SIZE = (5, 3.5)
BORDER_WIDTH = 1
LINE_WIDTH = 2  # Standard
LINE_WIDTH_BOLD = 3.5  # Bold for better visibility

__all__ = ['apply_chart_styles', 'COLORS', 'CHART_SIZE', 'BORDER_WIDTH', 'LINE_WIDTH', 'LINE_WIDTH_BOLD']
