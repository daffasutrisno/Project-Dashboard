# Checklist untuk Optimisasi Chart Berikutnya

## ✅ Visual Style Sudah Otomatis Diterapkan

**Tidak perlu setting lagi untuk setiap chart:**

- ✅ Line width: 3.5 (bold)
- ✅ Grid alpha: 0.15 (transparent)
- ✅ Grid color: lightgray
- ✅ Tick marks: thin (0.5), gray
- ✅ Border: transparent (0.4), gray
- ✅ Date format: dd/mm/yyyy
- ✅ Line zorder: 20 (always on top)

## 🎯 Yang Perlu Ditentukan Per Chart

### 1. Formula Requirements

- [ ] **Column database**: Nama column yang digunakan
- [ ] **Aggregation**: max / min / sum / avg
- [ ] **Display interval**: Every day? Every 2 days? Other?
- [ ] **Count direction**: From start or from end?
- [ ] **Gap detection**: Yes or No?

### 2. Data Handling

- [ ] **Zero handling**: Skip atau keep?
- [ ] **Null handling**: Skip (standard)
- [ ] **Negative values**: Skip atau keep?

### 3. Y-axis Configuration

- [ ] **Y-axis range**: Min and max values
- [ ] **Y-axis interval**: Step size
- [ ] **Top padding**: Hide top label? Value?
- [ ] **Bottom padding**: Negative padding? Value?
- [ ] **Format**: Decimal places, percentage symbol

### 4. Special Features

- [ ] **Clipping**: Clip to min/max?
- [ ] **Horizontal line**: At y=0 or other value?
- [ ] **Custom markers**: For special values?

## 🔒 Protected Charts (Already Perfect)

1. ✅ Availability
2. ✅ Accessibility
3. ✅ Call Drop Rate

**Visual style untuk chart baru akan otomatis sama dengan 3 chart ini!**

## 📝 Implementation Steps

1. Determine requirements (checklist di atas)
2. Create test script: `tests/test_{chart_name}.py`
3. Create aggregate function (jika perlu): `utils/data_processor.py`
4. Update generator: `generators/dashboard_5g.py`
5. Test & verify
6. Lock & document

**Visual style tidak perlu di-set manual lagi!** ✓
