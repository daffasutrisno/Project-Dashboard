"""
Base chart class with border and common formatting
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from io import BytesIO
from scipy.interpolate import make_interp_spline
from config import COLORS, CHART_SIZE, BORDER_WIDTH, LINE_WIDTH_BOLD

class BaseChart:
    """Base class for all charts"""
    
    def __init__(self, dates, values, title, ylabel):
        self.dates = dates
        self.values = values
        self.title = title
        self.ylabel = ylabel
        self.fig = None
        self.ax = None
        
    def create_figure(self):
        """Create figure with border"""
        self.fig, self.ax = plt.subplots(figsize=CHART_SIZE)
        self.fig.patch.set_edgecolor(COLORS['border'])
        self.fig.patch.set_linewidth(BORDER_WIDTH)
        
    def format_common(self, date_format='%d/%m/%Y'):
        """Apply common formatting with transparent grid and thin ticks"""
        self.ax.set_title(self.title, fontweight='bold', pad=12, fontsize=10)
        self.ax.set_ylabel(self.ylabel, fontsize=9)
        
        # TRANSPARENT grid (LOWER zorder - behind data line)
        self.ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5, 
                    color='lightgray', zorder=1)
        
        # Use numeric index for x-axis to ensure equal spacing
        n_points = len(self.dates)
        x_positions = np.arange(n_points)
        
        # SHOW ALL DAYS with YEAR (format: dd/mm/yyyy)
        tick_positions = x_positions
        tick_labels = [self.dates.iloc[i].strftime(date_format) if hasattr(self.dates, 'iloc') 
                      else self.dates[i].strftime(date_format) for i in range(n_points)]
        
        self.ax.set_xticks(tick_positions)
        self.ax.set_xticklabels(tick_labels)
        
        # THIN and TRANSPARENT tick marks
        self.ax.tick_params(
            axis='both',
            which='both',
            width=0.5,
            length=3,
            color='gray',
            direction='out',
            pad=2
        )
        
        self.ax.tick_params(axis='x', rotation=45, labelsize=6)
        self.ax.tick_params(axis='y', labelsize=8)
        
        # Set x-axis limits
        self.ax.set_xlim(-0.5, n_points - 0.5)
        
        # Transparent labels
        for label in self.ax.get_xticklabels():
            label.set_horizontalalignment('right')
            label.set_alpha(0.8)
        
        for label in self.ax.get_yticklabels():
            label.set_alpha(0.8)
        
        # Transparent borders
        for spine in self.ax.spines.values():
            spine.set_edgecolor('gray')
            spine.set_linewidth(0.6)
            spine.set_alpha(0.4)
    
    def smooth_line(self, values, color, clip_min=None, clip_max=None):
        """
        Create BOLD smooth line using spline interpolation with HIGH zorder
        
        Args:
            values: Data values
            color: Line color
            clip_min: Minimum value for clipping (optional)
            clip_max: Maximum value for clipping (optional)
        """
        n_points = len(values)
        x_data = np.arange(n_points)
        
        if n_points > 3:
            x_smooth = np.linspace(0, n_points - 1, 300)
            try:
                spl = make_interp_spline(x_data, values, k=3)
                values_smooth = spl(x_smooth)
                
                # Apply clipping if specified
                if clip_min is not None:
                    values_smooth = np.maximum(values_smooth, clip_min)
                if clip_max is not None:
                    values_smooth = np.minimum(values_smooth, clip_max)
                
                # BOLD line with HIGH zorder (always on top)
                self.ax.plot(x_smooth, values_smooth, color=color, 
                           linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
            except:
                self.ax.plot(x_data, values, color=color, 
                           linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
        else:
            self.ax.plot(x_data, values, color=color, 
                       linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
    
    def save_to_stream(self):
        """Save chart to BytesIO stream"""
        plt.tight_layout()
        img_stream = BytesIO()
        plt.savefig(img_stream, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=COLORS['background'])
        img_stream.seek(0)
        plt.close()
        return img_stream
