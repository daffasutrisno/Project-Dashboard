# SUMMARY - Chart Implementation Status

## ✅ Completed & LOCKED Charts (DO NOT MODIFY)

### 1. Availability Chart - PERFECT ✓ 🔒

**Status:** LOCKED - No modifications allowed

**Formula:**

- Range: 35 hari terakhir dari MAX date
- Aggregation: MAX value per hari
- Filter: Skip hari dengan data = 0 atau null
- Display: **SETIAP HARI** yang valid
- Index: Hari pertama dalam range dengan data > 0

**Visual Style:**

- Y-axis: 99.00% - 100.20%, interval 0.20%, hide 100.20%
- X-axis: dd/mm/yyyy format
- Line: **Bold (3.5)**, zorder 20
- Grid: **Transparent (alpha 0.15)**, zorder 1
- Tick marks: **Thin (0.5)**, gray
- Border: **Transparent (alpha 0.4)**, gray

---

### 2. Accessibility Chart - PERFECT ✓ 🔒

**Status:** LOCKED - No modifications allowed

**Formula:**

- Range: 35 hari terakhir dari MAX date
- Aggregation: MAX value per hari
- Filter: Skip hari dengan data = 0 atau null
- Display: **SETIAP 2 HARI** (atau 4 jika gap), **count from END**
- Gap Detection: Ya, jump to 4 days if data missing
- Index: Dari data terakhir (newest) mundur

**Visual Style:**

- Y-axis: 96.00% - 101.00%, interval 1.0%, hide 101%
- X-axis: dd/mm/yyyy format
- Line: **Bold (3.5)**, zorder 20
- Grid: **Transparent (alpha 0.15)**, zorder 1
- Tick marks: **Thin (0.5)**, gray
- Border: **Transparent (alpha 0.4)**, gray

---

### 3. Call Drop Rate (CDR) Chart - PERFECT ✓ 🔒

**Status:** LOCKED - No modifications allowed

**Formula:**

- Range: 35 hari terakhir dari MAX date
- Aggregation: MAX value per hari
- Filter: Skip hanya jika null atau negative (**zero is VALID**)
- Display: **SETIAP 2 HARI**, simple, **count from END**
- Gap Detection: **No** (simple interval)
- Index: Dari data terakhir (newest) mundur

**Visual Style:**

- Y-axis: 0.000% - 0.016%, interval 0.002%, hide 0.016%
- X-axis: dd/mm/yyyy format
- Line: **Bold (3.5)**, zorder 20, **clip to min 0**
- Grid: **Transparent (alpha 0.15)**, zorder 1
- Horizontal line at y=0 (alpha 0.2)
- Tick marks: **Thin (0.5)**, gray
- Border: **Transparent (alpha 0.4)**, gray

---

## 📐 Standard Visual Style for ALL Line Charts

**Apply to all charts dengan tipe line (existing & future):**

| Element            | Standard Setting           |
| ------------------ | -------------------------- |
| **Line Width**     | 3.5 (bold)                 |
| **Line Zorder**    | 20 (always on top)         |
| **Line Cap**       | round                      |
| **Grid Alpha**     | 0.15 (very transparent)    |
| **Grid Color**     | lightgray                  |
| **Grid Linewidth** | 0.5                        |
| **Grid Zorder**    | 1 (behind line)            |
| **Tick Width**     | 0.5 (thin)                 |
| **Tick Length**    | 3 (short)                  |
| **Tick Color**     | gray                       |
| **Border Alpha**   | 0.4 (transparent)          |
| **Border Color**   | gray                       |
| **Border Width**   | 0.6                        |
| **Label Alpha**    | 0.8 (slightly transparent) |
| **Date Format**    | dd/mm/yyyy                 |

---

## 🔧 Charts Pending Optimization

| Chart                | Status     | Formula | Padding | Zero Handling |
| -------------------- | ---------- | ------- | ------- | ------------- |
| Sgnb addition SR     | ⏳ Pending | TBD     | TBD     | TBD           |
| Total Traffic        | ⏳ Pending | TBD     | TBD     | TBD           |
| EUT vs DL User Thp   | ⏳ Pending | TBD     | TBD     | TBD           |
| User 5G              | ⏳ Pending | TBD     | TBD     | TBD           |
| DL PRB Util          | ⏳ Pending | TBD     | TBD     | TBD           |
| Inter esgNB          | ⏳ Pending | TBD     | TBD     | TBD           |
| Intra esgNB          | ⏳ Pending | TBD     | TBD     | TBD           |
| Intra sgNB intrafreq | ⏳ Pending | TBD     | TBD     | TBD           |
| Inter sgNB intrafreq | ⏳ Pending | TBD     | TBD     | TBD           |

**Note:** All line charts will automatically use standard visual style (bold line, transparent grid, thin ticks)

---

## 🔒 Protection Rules

### LOCKED Functions - DO NOT MODIFY:

```python
# In utils/data_processor.py
aggregate_availability_data()     # 🔒 Availability
aggregate_accessibility_data()    # 🔒 Accessibility
aggregate_cdr_data()              # 🔒 Call Drop Rate

# In charts/chart_5g.py
AvailabilityChart5G              # 🔒 Availability
LineChart5G (for Accessibility)   # 🔒 Accessibility
CDRChart5G                        # 🔒 Call Drop Rate

# In generators/dashboard_5g.py
# Chart 1 - Availability section   # 🔒
# Chart 2 - Accessibility section   # 🔒
# Chart 3 - CDR section             # 🔒

# In charts/base_chart.py
smooth_line()                     # ✓ Visual style (OK to use)
format_common()                   # ✓ Visual style (OK to use)
```

### Safe to Modify:

```python
# In utils/data_processor.py
aggregate_daily_data()            # ✓ For other charts
# Add new aggregate functions       # ✓ For new charts

# In charts/chart_5g.py
# Other chart classes               # ✓ Can modify
# Add new chart classes             # ✓ Can create

# In generators/dashboard_5g.py
# Chart 4 onwards                   # ✓ Can modify
```

---

## 📋 Checklist for New Chart Optimization

When optimizing a new chart:

- [ ] Tentukan formula (range, aggregation, filter, display interval)
- [ ] Tentukan zero handling (skip atau keep?)
- [ ] Tentukan padding (top/bottom)
- [ ] Create test script di `tests/test_{chart_name}.py`
- [ ] Apply standard visual style (bold line, transparent grid)
- [ ] Test & verify
- [ ] Update SUMMARY.md
- [ ] Lock chart setelah perfect

**Standard visual style akan otomatis diterapkan untuk semua line charts!**

---

**Last Updated:** 2025-01-XX  
**Completed Charts:** 3/12  
**Charts Remaining:** 9/12

**Status: AVAILABILITY, ACCESSIBILITY, CDR LOCKED ✓**
