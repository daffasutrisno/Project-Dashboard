"""
5G specific charts
"""
import matplotlib.dates as mdates
import numpy as np
import pandas as pd  # ADD THIS IMPORT
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

class SgnbSRChart5G(BaseChart):
    """Sgnb addition SR chart for 5G - Y-axis SAME AS Availability"""
    
    def create(self):
        """Create Sgnb SR chart with Y-axis EXACTLY like Availability"""
        self.create_figure()
        
        values_chart = self.values * 100
        
        # Plot BOLD smooth line
        self.smooth_line(values_chart, COLORS['primary'])
        
        # Custom y-axis: 99.00% to 100.20% with interval 0.20% (SAME AS AVAILABILITY)
        self.ax.set_ylim(99.00, 100.20)
        yticks = np.arange(99.00, 100.21, 0.20)
        self.ax.set_yticks(yticks)
        
        # Hide top label (100.20%) - SAME AS AVAILABILITY
        yticklabels = [f'{y:.2f}%' if abs(y - 100.20) > 0.01 else '' for y in yticks]
        self.ax.set_yticklabels(yticklabels)
        
        self.format_common()
        return self.save_to_stream()

# ========== STANDARD CHARTS (Safe to modify) ==========

class LineChart5G(BaseChart):
    """Standard line chart for 5G metrics"""
    
    def __init__(self, dates, values, title, ylabel, ylim=None, ytick_format=None, 
                 color=None, hide_top_label=False):
        super().__init__(dates, values, title, ylabel)
        self.ylim = ylim
        self.ytick_format = ytick_format
        self.color = color or COLORS['primary']
        self.hide_top_label = hide_top_label
    
    def create(self):
        """Create BOLD line chart with optional clipping"""
        self.create_figure()
        
        # Plot BOLD smooth line with clipping if ylim is set
        if self.ylim:
            self.smooth_line(self.values, self.color, 
                           clip_min=self.ylim[0], clip_max=self.ylim[1])
        else:
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

class TrafficChart5G(BaseChart):
    """Traffic chart for 5G (Area Chart) with fixed Y-axis"""
    
    def create(self):
        """Create Traffic area chart with Y-axis 0-50,000 GB, hide 50K label"""
        self.create_figure()
        
        # Use numeric x-axis
        n_points = len(self.values)
        x_data = np.arange(n_points)
        
        # Plot AREA CHART with fill
        self.ax.fill_between(x_data, self.values, alpha=0.7, 
                            color='#17516d', zorder=10)
        self.ax.plot(x_data, self.values, color='#17516d', 
                    linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
        
        # Set y-axis: 0 to 50,000 GB with interval 5,000
        self.ax.set_ylim(0, 50000)
        yticks = np.arange(0, 51000, 5000)
        self.ax.set_yticks(yticks)
        
        # Format y-axis labels: HIDE 50,000 (top padding)
        from matplotlib.ticker import FuncFormatter
        def format_y_axis(y, _):
            if abs(y - 50000) < 100:  # Hide 50,000
                return ''
            return f'{int(y):,}'
        
        self.ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))
        
        self.format_common()
        return self.save_to_stream()

class EUTThpChart5G(BaseChart):
    """EUT vs DL User Thp chart for 5G (Dual Line)"""
    
    def __init__(self, dates, eut_values, thp_values, title, ylabel):
        super().__init__(dates, eut_values, title, ylabel)
        self.thp_values = thp_values
    
    def create(self):
        """Create dual line chart for EUT vs Thp"""
        self.create_figure()
        
        n_points = len(self.dates)
        x_data = np.arange(n_points)
        
        # Line 2 (Thp - PRIMARY, orange) - plot first so it's behind
        if n_points > 3:
            x_smooth = np.linspace(0, n_points - 1, 300)
            try:
                from scipy.interpolate import make_interp_spline
                spl2 = make_interp_spline(x_data, self.thp_values, k=3)
                values_smooth2 = spl2(x_smooth)
                self.ax.plot(x_smooth, values_smooth2, color='#ff7f0e', 
                           linewidth=LINE_WIDTH_BOLD, zorder=19, solid_capstyle='round')
            except:
                self.ax.plot(x_data, self.thp_values, color='#ff7f0e', 
                           linewidth=LINE_WIDTH_BOLD, zorder=19, solid_capstyle='round')
        else:
            self.ax.plot(x_data, self.thp_values, color='#ff7f0e', 
                       linewidth=LINE_WIDTH_BOLD, zorder=19, solid_capstyle='round')
        
        # Line 1 (EUT - FOLLOWS index, blue) - only where data exists
        # Mask for valid EUT data
        eut_mask = (pd.Series(self.values).notna()) & (pd.Series(self.values) > 0)
        eut_indices = np.where(eut_mask)[0]
        
        if len(eut_indices) > 0:
            eut_x = x_data[eut_indices]
            eut_y = self.values[eut_indices]
            
            if len(eut_indices) > 3:
                x_smooth_eut = np.linspace(eut_x.min(), eut_x.max(), 300)
                try:
                    spl1 = make_interp_spline(eut_x, eut_y, k=3)
                    values_smooth1 = spl1(x_smooth_eut)
                    self.ax.plot(x_smooth_eut, values_smooth1, color='#1f77b4', 
                               linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
                except:
                    self.ax.plot(eut_x, eut_y, color='#1f77b4', 
                               linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
            else:
                self.ax.plot(eut_x, eut_y, color='#1f77b4', 
                           linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
        
        # Legend
        self.ax.plot([], [], color='#1f77b4', linewidth=LINE_WIDTH_BOLD, label='g5_eut_bhv')
        self.ax.plot([], [], color='#ff7f0e', linewidth=LINE_WIDTH_BOLD, label='g5_userdl_thp')
        self.ax.legend(loc='upper left', fontsize=7)
        
        # Y-axis: 0 to 120 with interval 20, hide 120
        self.ax.set_ylim(0, 120)
        yticks = np.arange(0, 121, 20)
        self.ax.set_yticks(yticks)
        
        # Hide top label (120) - padding
        yticklabels = [f'{int(y)}' if abs(y - 120) > 0.1 else '' for y in yticks]
        self.ax.set_yticklabels(yticklabels)
        
        self.format_common()
        return self.save_to_stream()

class User5GChart(BaseChart):
    """User 5G chart (Bar Chart) with fixed Y-axis"""
    
    def create(self):
        """Create User 5G bar chart with Y-axis 0-400,000"""
        self.create_figure()
        
        # Use numeric x-axis
        n_points = len(self.values)
        x_data = np.arange(n_points)
        
        # Plot BAR CHART
        self.ax.bar(x_data, self.values, color='#1f77b4', width=0.8, zorder=10)
        
        # Y-axis: 0 to 400,000 with interval 50,000, hide 400,000
        self.ax.set_ylim(0, 400000)
        yticks = np.arange(0, 401000, 50000)
        self.ax.set_yticks(yticks)
        
        # Format y-axis labels: HIDE 400,000 (top padding)
        from matplotlib.ticker import FuncFormatter
        def format_y_axis(y, _):
            if abs(y - 400000) < 100:  # Hide 400,000
                return ''
            return f'{int(y/1000)}K'  # Format as K (thousands)
        
        self.ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))
        
        self.format_common()
        return self.save_to_stream()

class PRBUtilChart5G(BaseChart):
    """PRB Util chart for 5G (Line + Bar with Dual Y-Axis)"""
    
    def __init__(self, dates, prb_util_values, cells_count_values, title, ylabel_left, ylabel_right):
        super().__init__(dates, prb_util_values, title, ylabel_left)
        self.cells_count_values = cells_count_values
        self.ylabel_right = ylabel_right
    
    def create(self):
        """Create dual Y-axis chart (Line + Bar overlay)"""
        self.create_figure()
        
        # Create second y-axis
        ax2 = self.ax.twinx()
        
        n_points = len(self.dates)
        x_data = np.arange(n_points)
        
        # LEFT Y-AXIS: Line chart (PRB Util %)
        values_line = self.values * 100
        
        # Plot BOLD smooth line on left Y-axis
        if n_points > 3:
            x_smooth = np.linspace(0, n_points - 1, 300)
            try:
                from scipy.interpolate import make_interp_spline
                spl = make_interp_spline(x_data, values_line, k=3)
                values_smooth = spl(x_smooth)
                self.ax.plot(x_smooth, values_smooth, color='#1f77b4', 
                           linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
            except:
                self.ax.plot(x_data, values_line, color='#1f77b4', 
                           linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
        else:
            self.ax.plot(x_data, values_line, color='#1f77b4', 
                       linewidth=LINE_WIDTH_BOLD, zorder=20, solid_capstyle='round')
        
        # RIGHT Y-AXIS: Bar chart (Cells count) - VERY TRANSPARENT
        bar_mask = (pd.Series(self.cells_count_values).notna()) & (pd.Series(self.cells_count_values) > 0)
        bar_indices = np.where(bar_mask)[0]
        
        if len(bar_indices) > 0:
            ax2.bar(bar_indices, self.cells_count_values[bar_indices], 
                   color='#ff7f0e', width=0.8, alpha=0.3, zorder=10)
        
        # Configure LEFT Y-AXIS: 0-50% with interval 5%, hide 50%
        self.ax.set_ylim(0, 50)
        yticks_left = np.arange(0, 51, 5)
        self.ax.set_yticks(yticks_left)
        
        # Hide top label (50%)
        yticklabels_left = [f'{int(y)}%' if abs(y - 50) > 0.1 else '' for y in yticks_left]
        self.ax.set_yticklabels(yticklabels_left)
        
        self.ax.set_ylabel(self.ylabel, fontsize=9, color='#1f77b4')
        self.ax.tick_params(axis='y', labelcolor='#1f77b4', labelsize=8)
        
        # Configure RIGHT Y-AXIS: 0-10 with interval 1, hide 10
        ax2.set_ylim(0, 10)
        yticks_right = np.arange(0, 11, 1)
        ax2.set_yticks(yticks_right)
        
        # Hide top label (10), show 9
        yticklabels_right = [f'{int(y)}' if abs(y - 10) > 0.1 else '' for y in yticks_right]
        ax2.set_yticklabels(yticklabels_right)
        
        ax2.set_ylabel(self.ylabel_right, fontsize=9, color='#ff7f0e')
        ax2.tick_params(axis='y', labelcolor='#ff7f0e', labelsize=8)
        
        # Transparent grid (only on ax1)
        self.ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5, 
                    color='lightgray', zorder=1)
        
        # Transparent borders for both axes
        for spine in self.ax.spines.values():
            spine.set_edgecolor('gray')
            spine.set_linewidth(0.6)
            spine.set_alpha(0.4)
        
        for spine in ax2.spines.values():
            spine.set_edgecolor('gray')
            spine.set_linewidth(0.6)
            spine.set_alpha(0.4)
        
        # Thin tick marks
        self.ax.tick_params(axis='both', which='both', width=0.5, length=3, 
                          color='gray', direction='out', pad=2)
        ax2.tick_params(axis='y', which='both', width=0.5, length=3, 
                       color='gray', direction='out', pad=2)
        
        # Add dummy lines for legend
        self.ax.plot([], [], color='#1f77b4', linewidth=LINE_WIDTH_BOLD, label='5G_DL_PRB_UTIL (%)')
        ax2.bar([], [], color='#ff7f0e', alpha=0.3, label='#Cells_DL PRB>85%')
        
        # Combined legend
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=7)
        
        self.format_common()
        return self.save_to_stream()