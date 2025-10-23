# KPI Monitoring Dashboard Generator

Auto-generate KPI Monitoring Dashboard PowerPoint presentations for 5G and 4G networks in East Java.

## Project Structure

```
Project/
├── config/                 # Configuration files
│   ├── __init__.py
│   ├── database.py        # Database credentials
│   └── chart_styles.py    # Chart styling
│
├── data/                   # Data layer
│   ├── __init__.py
│   └── data_fetcher.py    # Database queries
│
├── charts/                 # Chart components
│   ├── __init__.py
│   ├── base_chart.py      # Base chart class
│   ├── chart_5g.py        # 5G chart types
│   └── chart_4g.py        # 4G chart types
│
├── generators/             # Dashboard generators
│   ├── __init__.py
│   ├── dashboard_5g.py    # 5G dashboard
│   └── dashboard_4g.py    # 4G dashboard
│
├── presentation/           # PowerPoint builder
│   ├── __init__.py
│   └── ppt_builder.py     # PPT creation
│
├── utils/                  # Utilities
│   ├── __init__.py
│   └── data_processor.py  # Data processing
│
├── dashboard_monthly.py    # Main script (monthly)
├── dashboard_weekly.py     # Main script (weekly)
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Monthly Dashboard (35 days)

```bash
python dashboard_monthly.py
```

### Weekly Dashboard (7 days)

```bash
python dashboard_weekly.py
```

## Features

- ✅ Modular architecture
- ✅ Reusable chart components
- ✅ Smooth line interpolation
- ✅ Custom y-axis formatting
- ✅ Automatic data aggregation
- ✅ Border-wrapped charts
- ✅ 3x4 grid layout
- ✅ Two slides (5G & 4G)

## Chart Types

- Line charts (smooth interpolation)
- Area charts (traffic visualization)
- Bar charts (discrete values)
- Dual line charts (comparisons)
- Stacked bar charts (ratios)

## Customization

Edit configuration files in `config/` to customize:

- Database connection
- Chart colors
- Chart dimensions
- Font sizes
