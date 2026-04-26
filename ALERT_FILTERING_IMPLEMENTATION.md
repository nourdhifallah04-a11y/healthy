# Alert Filtering Implementation - Complete Guide

## 📋 Overview

A comprehensive multi-filter system has been implemented for the alerts dashboard, enabling filtering by:
- **Client** (searchable combobox)
- **Plat** (searchable combobox)
- **Nutritional Values** (range-based):
  - Calories (kcal)
  - Protéines (g)
  - Glucides (g)
  - Lipides (g)
  - Fibres (g)
- **Client Profile** (range-based):
  - IMC (Body Mass Index)

**Filter Logic**: AND-based (all active filters must match an alert)

---

## 🔧 Implementation Details

### Phase 1: Backend - Alert Context Enrichment

#### Modified: `myapp/score_monitoring.py`

**New Method**: `_enrich_context_with_nutritional_data(context, client_id, plat_id)`
- Fetches `Plat` object and extracts nutritional data when `plat_id` provided
- Stores in context as: `context['plat']['calories']`, `context['plat']['proteines']`, etc.
- Calculates client IMC from `ProfilNutritionnel` model and stores in: `context['client']['imc']`
- Graceful error handling: continues if plat/client not found

**Updated**: `record()` method
- Now calls `_enrich_context_with_nutritional_data()` before recording scores
- All alert emissions use enriched_context instead of raw context

#### Data Captured in Alert Context

```python
alert.context = {
  'plat': {
    'id': int,
    'nom': str,
    'calories': float,
    'proteines': float,
    'glucides': float,
    'lipides': float,
    'fibres': float,
  },
  'client': {
    'id': int,
    'age': int,
    'imc': float,  # Calculated from height/weight
  },
  # ... existing context fields
}
```

---

### Phase 2: Backend - Filtering Infrastructure

#### New Method: `_matches_nutritional_filters()`
- Implements AND-logic filtering for all nutritional ranges
- Checks if alert context contains plat/client data before comparing ranges
- Returns `True` only if alert matches ALL active filters

#### Extended Method: `get_alerts()`
**New Parameters**:
- `plat_id`: Filter by plat ID
- `calorie_min/max`: Calorie range (kcal)
- `proteines_min/max`: Protein range (g)
- `glucides_min/max`: Carbs range (g)
- `lipides_min/max`: Fat range (g)
- `fibres_min/max`: Fiber range (g)
- `imc_min/max`: Client IMC range

**Behavior**:
- Applies level filter → client_id filter → nutritional filters (AND logic)
- Returns JSON-safe alert dictionaries

---

### Phase 3: Backend - API Endpoints

#### Modified: `score_dashboard_api()` in `myapp/views_monitoring.py`

**New GET Parameters** (all optional):
```
?plat_id=5&calorie_min=100&calorie_max=500&proteines_min=10&proteines_max=30&...&imc_min=18&imc_max=25&limit=50
```

**Parsing**:
- Converts numeric parameters to float (with error handling)
- Passes all filters to `score_monitor.get_alerts()`

#### New Endpoint: `score_dashboard_filters_data()`
**URL**: `/monitoring/scores/filters-data/`
**Method**: GET (staff_member_required)
**Response**:
```json
{
  "clients": {
    "42": "John Doe (ID: 42)",
    "15": "Jane Smith (ID: 15)",
    ...
  },
  "plats": {
    "1": "Salade César",
    "5": "Steak Frites",
    ...
  },
  "nutritional_ranges": {
    "calories": {"min": 50, "max": 2000},
    "proteines": {"min": 2, "max": 80},
    "glucides": {"min": 5, "max": 150},
    "lipides": {"min": 1, "max": 100},
    "fibres": {"min": 0, "max": 50}
  }
}
```

**Purpose**: Populates datalists and suggests reasonable filter ranges

#### URL Configuration: `myapp/urls.py`
Added route:
```python
path("monitoring/scores/filters-data/", views_monitoring.score_dashboard_filters_data, name="monitoring_filters_data"),
```

---

### Phase 4: Frontend - UI Components

#### Modified: `templates/monitoring/score_dashboard.html`

**New CSS Styles**:
- `.advanced-filters`: Main filter container
- `.filters-grid`: Responsive grid layout (auto-fit columns)
- `.filter-group`: Input grouping for label + input
- `.filter-row`: Side-by-side min/max inputs
- `.filter-actions`: Button container
- `.active-filters-badge`: Counter showing active filters

**New HTML Elements**:
- **Datalist inputs** for Client and Plat (with `<datalist>` for autocomplete)
- **Range input pairs** for each nutritional value and IMC
- **Apply Filters button** (green, calls `applyNutritionalFilters()`)
- **Reset Filters button** (gray, calls `resetNutritionalFilters()`)
- **Active filters badge** (shows count of active filters)

**Filter Bar Layout** (responsive):
```
[🔍 Filtres avancés] [Active: 3]

[Client ▼] [Plat ▼] [Calories Min] [Calories Max] [Proteins Min] [Proteins Max]
[Carbs Min] [Carbs Max] [Fats Min] [Fats Max] [Fiber Min] [Fiber Max]
[IMC Min] [IMC Max]

[✓ Appliquer filtres] [↻ Réinitialiser]
```

---

### Phase 5: Frontend - JavaScript Filter Logic

#### New Functions:

**`populateFilterDatalists()`**
- Fetches `/monitoring/scores/filters-data/` on page load
- Populates `<datalist>` elements with available clients and plats
- Sets input `min/max` attributes from nutritional ranges

**`applyNutritionalFilters()`**
- Collects all filter input values
- Removes null/empty values
- Builds query string with filter parameters
- Calls `refreshWithFilters()`
- Updates active filters badge

**`refreshWithFilters(queryString)`**
- Makes AJAX fetch to API with filter parameters
- Handles response with filtered alerts
- Reloads page to display filtered results (simplified approach)

**`resetNutritionalFilters()`**
- Clears all filter input values
- Resets `nutritionalFilters` object
- Updates badge
- Reloads page

**`updateActiveFiltersCount()`**
- Counts active filters
- Updates badge with count
- Hides badge if no filters active

#### Global State:
```javascript
let nutritionalFilters = {};  // Stores current filter values
```

---

## 🎯 Usage Examples

### Example 1: Filter by Client and Calorie Range
```
Dashboard → Filter bar
[Client: John Doe ▼] [Calories Min: 200] [Calories Max: 500]
Click "Appliquer filtres"
→ Shows only alerts for John Doe with meals 200-500 kcal
```

### Example 2: Filter by Nutritional Profile
```
[Proteines Min: 25] [Proteines Max: 40]
[Glucides Min: 30] [Glucides Max: 60]
[Lipides Min: 10] [Lipides Max: 25]
Click "Appliquer filtres"
→ Shows alerts for meals in this macro range
```

### Example 3: Filter by Client IMC
```
[IMC Min: 18.5] [IMC Max: 24.9]  (Normal weight range)
Click "Appliquer filtres"
→ Shows alerts only for clients in normal BMI range
```

### Example 4: Combined Filters (AND Logic)
```
[Client: Jane] [Plat: Salmon]
[Calories Min: 300] [Calories Max: 600]
[Proteines Min: 30] [Proteines Max: 50]
Click "Appliquer filtres"
→ Shows alerts for Jane's Salmon dishes with 300-600 kcal AND 30-50g protein
```

---

## 🔍 How It Works

### Data Flow: Recording Score

```
score_monitor.record(
  score_type='simple',
  value=75.5,
  client_id=42,
  plat_id=5
)
    ↓
_enrich_context_with_nutritional_data(context, 42, 5)
    ↓
[Fetch Plat(5) → extract calories, proteins, etc.]
[Fetch ProfilNutritionnel(42) → calculate IMC]
    ↓
context = {
  'plat': {'calories': 350, 'proteines': 25, ...},
  'client': {'imc': 22.5, ...},
  ...
}
    ↓
Alert created with enriched context
```

### Data Flow: Filtering Alerts

```
User clicks "Appliquer filtres"
    ↓
applyNutritionalFilters()
    ↓
Build query: ?client_id=42&calorie_min=200&calorie_max=500&...
    ↓
GET /monitoring/scores/api/?client_id=42&calorie_min=200&...
    ↓
score_dashboard_api() view
    ↓
score_monitor.get_alerts(
  client_id=42,
  calorie_min=200,
  calorie_max=500,
  ...
)
    ↓
For each alert in self._alerts:
  - Check level? ✓
  - Check client_id? ✓
  - _matches_nutritional_filters()? ✓
    ↓
Return only alerts matching ALL filters
    ↓
JSONResponse with filtered alerts
```

---

## ⚙️ Configuration & Limits

### Input Constraints
- **Calories**: 0 to max_plat_calories (dynamic from DB)
- **Proteins**: 0 to 100g
- **Carbs**: 0 to 100g
- **Fats**: 0 to 100g
- **Fiber**: 0 to 100g
- **IMC**: 10 to 50 (typical adult range)

### Performance Considerations
- Filters applied in-memory (alert deque)
- Limit default: 50 alerts per fetch
- Database queries for datalist population: 1 query (filtered in Python)
- No new database indexes needed

### Error Handling
- Invalid numeric input: Ignored (treated as null)
- Missing client/plat: Alert still shown if ID matches
- Missing nutritional data in context: Filter skipped for that value
- Graceful degradation: System continues working even if enrichment fails

---

## 📊 Models Involved

### Plat Model
```python
calorie: float          # kcal
proteine: float         # g
glucides: float         # g
lipides: float          # g
fibres: float           # g
```

### ProfilNutritionnel Model
```python
taille: DecimalField    # cm
poids: DecimalField     # kg
# (IMC calculated from these)
```

### Alert Model (in score_monitoring.py)
```python
context: Dict[str, Any]  # Now contains plat + client data
client_id: Optional[int]
plat_id: Optional[int]
```

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Record score with plat_id → verify nutritional data in context
- [ ] Record score with client_id → verify IMC in context
- [ ] Filter by plat_id alone
- [ ] Filter by nutritional range (single)
- [ ] Filter by multiple nutritional ranges (AND logic)
- [ ] Filter by IMC range
- [ ] Filter with non-existent IDs (should return empty)
- [ ] Filter with invalid numeric input (should be ignored)

### Frontend Tests
- [ ] Datalists populate on page load
- [ ] Input ranges reflect database min/max
- [ ] Apply filters button builds correct query
- [ ] Reset filters clears all inputs
- [ ] Active filters badge shows/hides correctly
- [ ] Alerts update after applying filters
- [ ] Range inputs enforce min/max constraints

### Integration Tests
- [ ] End-to-end: Record score → Load dashboard → Apply filter → See filtered alert
- [ ] Multiple simultaneous filters work with AND logic
- [ ] Page reload preserves filter state (via URL params)

---

## 📁 Modified Files Summary

| File | Changes |
|------|---------|
| `myapp/score_monitoring.py` | Added `_enrich_context_with_nutritional_data()`, extended `get_alerts()` with nutritional params, added `_matches_nutritional_filters()` |
| `myapp/views_monitoring.py` | Extended `score_dashboard_api()` with filter params, added `score_dashboard_filters_data()` endpoint |
| `myapp/urls.py` | Added route for `score_dashboard_filters_data` |
| `templates/monitoring/score_dashboard.html` | Added filter UI, CSS styles, JavaScript functions |

---

## 🚀 Next Steps (Optional Enhancements)

1. **Saved Filter Presets**: Save filter configurations for quick reuse
2. **Export Filtered Alerts**: CSV/PDF export of filtered results
3. **Filter History**: Show recently used filter combinations
4. **Advanced Ranges**: Predefined ranges (e.g., "High Protein", "Low Carb")
5. **Real-time Updates**: WebSocket connection for live alert filtering
6. **Filter Analytics**: Show most common filter combinations
7. **Conditional Alerts**: Create rules like "Alert if (Calories > 800 AND Protein < 20)"

---

## 📞 Support

**Issues with filtering?**
1. Check browser console for JavaScript errors
2. Verify nutritional data populated in `/monitoring/scores/filters-data/`
3. Check database for missing ProfilNutritionnel records
4. Test API endpoint directly: `/monitoring/scores/api/?calorie_min=100`

**Performance too slow?**
- Reduce `limit` parameter in API calls
- Add database index on `Alert.client_id` if using database persistence

---

**Implementation Date**: April 22, 2026
**Version**: 1.0
**Status**: ✅ Complete & Ready for Testing
