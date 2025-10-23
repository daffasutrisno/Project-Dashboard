"""
5G specific charts
"""
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import make_interp_spline
from .base_chart import BaseChart
from config import COLORS, LINE_WIDTH_BOLD

# ========== LOCKED CHARTS (DO NOT MODIFY) ==========

class AvailabilityChart5G(BaseChart):
    """Availability chart for 5G - LOCKED 🔒"""
    
    def create(self):
        """Create availability chart - NO FORMULA CHANGES, only visual style"""
        self.create_figure()
        
        values_chart = self.values * 100
        
        # Plot BOLD smooth line (style update only)
        self.smooth_line(values_chart, COLORS['primary'])
        
        # Custom y-axis: 99.00 to 100.20 with interval 0.20 - UNCHANGED
        self.ax.set_ylim(99.00, 100.20)
        yticks = np.arange(99.00, 100.21, 0.20)
        self.ax.set_yticks(yticks)
        yticklabels = [f'{y:.2f}%' if abs(y - 100.20) > 0.01 else '' for y in yticks]
        self.ax.set_yticklabels(yticklabels)
        
        self.format_common()
        return self.save_to_stream()

class CDRChart5G(BaseChart):
    """Call Drop Rate chart for 5G - LOCKED 🔒"""
    
    def create(self):
        """Create CDR chart"""
        self.create_figure()
        
        values_chart = self.values * 100
        
        # Plot BOLD smooth line with clipping to min=0
        self.smooth_line(values_chart, COLORS['primary'], clip_min=0)
        
        # Custom y-axis: 0.000% to 0.016% with interval 0.002%
        self.ax.set_ylim(0, 0.016)
        yticks = np.arange(0, 0.017, 0.002)
        self.ax.set_yticks(yticks)
        
        # Hide top label (0.016%)
        yticklabels = [f'{y:.3f}%' if abs(y - 0.016) > 0.0001 else '' for y in yticks]
        self.ax.set_yticklabels(yticklabels)
        
        # Subtle horizontal line at y=0 (LOWER zorder)
        self.ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-', 
                       alpha=0.2, zorder=2)
        
        self.format_common()
        return self.save_to_stream()

# ========== STANDARD CHARTS (Safe to modify) ==========

class LineChart5G(BaseChart):
    """Standard line chart for 5G metrics - applies to Accessibility and others"""
    
    def __init__(self, dates, values, title, ylabel, ylim=None, ytick_format=None, 
                 color=None, hide_top_label=False):
        super().__init__(dates, values, title, ylabel)
        self.ylim = ylim
        self.ytick_format = ytick_format
        self.color = color or COLORS['primary']
        self.hide_top_label = hide_top_label
    
    def create(self):
        """Create BOLD line chart with standard visual style"""
        self.create_figure()
        
        # Plot BOLD smooth line (standard style)
        self.smooth_line(self.values, self.color)
        
        if self.ylim:
            self.ax.set_ylim(self.ylim)
            
            if self.hide_top_label:
                yticks = self.ax.get_yticks()
                max_tick = yticks[-1]
                
                if self.ytick_format:
                    from matplotlib.ticker import FuncFormatter
                    def format_func(y, _):
                        if abs(y - max_tick) < 0.01:
                            return ''
                        return self.ytick_format.format(y)
                    self.ax.yaxis.set_major_formatter(FuncFormatter(format_func))
                else:
                    yticklabels = ['' if abs(y - max_tick) < 0.01 else f'{y:.2f}' for y in yticks]
                    self.ax.set_yticklabels(yticklabels)
        
        elif self.ytick_format:
            from matplotlib.ticker import FuncFormatter
            self.ax.yaxis.set_major_formatter(
                FuncFormatter(lambda y, _: self.ytick_format.format(y))
            )
        
        self.format_common()
        return self.save_to_stream()

class AreaChart5G(BaseChart):
    """Area chart for traffic visualization"""
    
    def __init__(self, dates, values, title, ylabel, color=None):
        super().__init__(dates, values, title, ylabel)
        self.color = color or COLORS['area']
    
    def create(self):
        """Create area chart"""
        self.create_figure()
        
        # Use numeric x-axis
        n_points = len(self.values)
        x_data = np.arange(n_points)
        
        self.ax.fill_between(x_data, self.values, alpha=0.7, color=self.color, zorder=10)
        self.ax.plot(x_data, self.values, color=self.color, linewidth=LINE_WIDTH_BOLD, zorder=20)
        
        self.format_common()
        return self.save_to_stream()

class BarChart5G(BaseChart):
    """Bar chart for discrete values"""
    
    def __init__(self, dates, values, title, ylabel, color=None):
        super().__init__(dates, values, title, ylabel)
        self.color = color or COLORS['primary']
    
    def create(self):
        """Create bar chart"""
        self.create_figure()
        
        n_points = len(self.values)
        x_data = np.arange(n_points)
        
        self.ax.bar(x_data, self.values, color=self.color, width=0.8, zorder=10)
        
        self.format_common()
        return self.save_to_stream()

class DualLineChart5G(BaseChart):
    """Dual line chart for comparison"""
    
    def __init__(self, dates, values1, values2, title, ylabel, label1, label2, 
                 color1=None, color2=None):
        super().__init__(dates, values1, title, ylabel)
        self.values2 = values2
        self.label1 = label1
        self.label2 = label2
        self.color1 = color1 or COLORS['primary']
        self.color2 = color2 or COLORS['secondary']
    
    def create(self):
        """Create BOLD dual line chart"""
        self.create_figure()
        
        # Smooth both lines with BOLD width
        self.smooth_line(self.values, self.color1)
        self.ax.plot([], [], color=self.color1, linewidth=LINE_WIDTH_BOLD, label=self.label1)
        
        # Second line
        n_points = len(self.values2)
        x_data = np.arange(n_points)
        
        if n_points > 3:
            x_smooth = np.linspace(0, n_points - 1, 300)
            try:
                spl = make_interp_spline(x_data, self.values2, k=3)
                values_smooth = spl(x_smooth)
                self.ax.plot(x_smooth, values_smooth, color=self.color2, 
                           linewidth=LINE_WIDTH_BOLD, zorder=20)
            except:
                self.ax.plot(x_data, self.values2, color=self.color2, 
                           linewidth=LINE_WIDTH_BOLD, zorder=20)
        else:
            self.ax.plot(x_data, self.values2, color=self.color2, 
                       linewidth=LINE_WIDTH_BOLD, zorder=20)
        
        self.ax.plot([], [], color=self.color2, linewidth=LINE_WIDTH_BOLD, label=self.label2)
        
        self.ax.legend(loc='upper left', fontsize=7)
        self.format_common()
        return self.save_to_stream()

class StackedBarChart5G(BaseChart):
    """Stacked bar chart"""
    
    def __init__(self, dates, values1, values2, title, ylabel, label1, label2,
                 color1=None, color2=None):
        super().__init__(dates, values1, title, ylabel)
        self.values2 = values2
        self.label1 = label1
        self.label2 = label2
        self.color1 = color1 or COLORS['primary']
        self.color2 = color2 or COLORS['secondary']
    
    def create(self):
        """Create stacked bar chart"""
        self.create_figure()
        
        n_points = len(self.values)
        x_data = np.arange(n_points)
        
        self.ax.bar(x_data, self.values, color=self.color1, 
                   label=self.label1, width=0.8, zorder=10)
        self.ax.bar(x_data, self.values2, bottom=self.values, 
                   color=self.color2, label=self.label2, width=0.8, zorder=10)
        
        self.ax.legend(loc='upper left', fontsize=7)
        self.format_common()
        return self.save_to_stream()