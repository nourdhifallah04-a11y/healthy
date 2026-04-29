# Comparer Feature - Side-by-Side Nutritional Comparison

## Overview

The **Comparer** feature allows users to select and compare up to 3 menus side-by-side, displaying their nutritional values, visual comparisons, and personalized recommendations.

## Features

### 1. Menu Selection Interface
- **Modal-based selection** for comparing menus
- **Checkbox selection** for up to 3 menus maximum
- **Visual feedback** when menus are selected
- **Real-time counter** showing number of selected menus

### 2. Comparison Table
- **Detailed nutritional metrics:**
  - Calories (kcal)
  - Proteins (g)
  - Carbohydrates (g)
  - Fats (g)
  - Fiber (g)
  - Nutritional score (/100)
- **Visual bars** showing relative values
- **Responsive design** that adapts to screen size

### 3. Comparison Charts
- **Four visual charts:**
  - Calories comparison
  - Protein comparison
  - Carbohydrates comparison
  - Fats comparison
- **Bar graph visualization** with labels
- **Value tooltips** on hover
- **Responsive grid layout**

### 4. Intelligent Recommendations
- **Automatic analysis** based on selected menus
- **Personalized insights** for 2-3 menu comparisons
- **Highlights** best protein, lowest calories, and best nutritional score
- **Natural language recommendations** in French

## User Interface

### Accessing the Comparer
1. Click the **"Comparer"** button on any menu card
2. The comparison modal opens with all available menus listed

### Selecting Menus
1. Check the **checkbox** for each menu to compare
2. Maximum **3 menus** can be selected at once
3. Selected menus are highlighted with a green background
4. Counter shows "X menu(s) sélectionné(s)"

### Viewing Comparison
1. Once **2 or more menus** are selected:
   - The comparison table appears
   - Visual charts display automatically
   - Recommendations are generated
2. **Reset button** allows clearing all selections

## Technical Implementation

### File Structure
```
static/menu/
├── menu.js          # Comparison logic and event handlers
├── menu.css         # Comparison styling
└── unified-browse.css

templates/menu/
└── menu.html        # Comparison modal HTML structure
```

### Key Functions

#### `openCompareModal()`
- Opens the comparison modal
- Populates the menu selection list

#### `closeCompareModal()`
- Closes the comparison modal
- Doesn't reset selections

#### `toggleMenuSelection(menuId, ...)`
- Adds or removes menu from comparison
- Updates UI and displays comparison if 2+ menus selected

#### `updateComparisonUI()`
- Updates menu counter
- Shows/hides comparison table
- Updates selected menu highlighting

#### `displayComparisonTable()`
- Generates nutritional comparison table
- Updates table headers with menu names
- Creates visual bars for each metric
- Calls chart and recommendation functions

#### `displayComparisonCharts(selectedMenus)`
- Generates bar charts for key nutrients
- Calculates percentages based on max values
- Displays value labels

#### `displayComparisonRecommendation(selectedMenus)`
- Generates personalized recommendations
- Compares nutritional profiles
- Highlights best options for each metric

#### `resetComparison()`
- Clears all selections
- Resets UI to initial state
- Hides comparison table

### Data Flow

```
User clicks "Comparer" button
    ↓
openCompareModal() opens
    ↓
populateCompareMenusList() displays all menus
    ↓
User selects 1-3 menus
    ↓
toggleMenuSelection() for each selection
    ↓
updateComparisonUI() updates display
    ↓
displayComparisonTable() shows metrics
    ↓
displayComparisonCharts() shows visualizations
    ↓
displayComparisonRecommendation() shows insights
```

## CSS Classes

### Modal Classes
- `.compare-modal` - Modal container styling
- `.compare-modal-content` - Modal content wrapper
- `.compare-header` - Header with title and counter
- `.compare-body` - Main content area

### Selection Classes
- `.compare-selector` - Menu selection section
- `.compare-menus-list` - Grid of selectable menus
- `.compare-menu-item` - Individual menu item
- `.compare-menu-item.selected` - Selected menu styling

### Comparison Table Classes
- `.comparison-table` - Main table element
- `.metric-col` - Metric name column
- `.menu-col` - Menu data columns
- `.nutrient-value` - Nutritional value display
- `.nutrient-bar` - Visual bar for comparison
- `.nutrient-bar-fill` - Filled portion of bar

### Chart Classes
- `.compare-charts` - Charts container
- `.chart-container` - Individual chart wrapper
- `.comparison-chart` - Chart content area
- `.chart-bar` - Individual bar in chart
- `.chart-bar-fill` - Bar fill animation
- `.chart-bar-label` - Bar label below
- `.chart-bar-value` - Value tooltip

### Recommendation Classes
- `.compare-recommendation` - Recommendation box
- `.difference-badge` - Difference highlight

## Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `--vert-sauge` (#9BBF8F) | Headers, active states |
| Secondary | `--vert-feuille` (#5A7D5C) | Text, borders |
| Accent | `--accent-miel` (#D9B48B) | Compare button, highlights |
| Background | `--beige-pale` (#FDF7ED) | Modal background |
| Disabled | `--beige-moyen` (#E8DCC6) | Inactive elements |

## Responsive Design

### Desktop (1024px+)
- Full table width with horizontal scroll if needed
- Multi-column chart grid
- Side-by-side menu selection

### Tablet (768px - 1023px)
- Adjusted chart grid to 2 columns
- Reduced font sizes for tables
- Optimized spacing

### Mobile (<768px)
- Full-width comparison table
- Single column chart grid
- Stacked buttons in footer
- Vertical menu selection

## State Management

### `comparisonState` Object
```javascript
{
    selectedMenus: Map {
        menuId1 -> {id, name, calories, protein, carbs, fat, fiber, score},
        menuId2 -> {...},
        ...
    },
    maxMenusToCompare: 3
}
```

## Integration Points

### Menu Cards
- "Compare" button added to each menu card footer
- Button opens modal with pre-populated menu list
- Button styling matches design system

### API Integration
- Uses existing menu data from `transformerMenuEnMeal()`
- No new API calls required
- Data already available in `meals` global array

## Browser Compatibility

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

- ✅ Keyboard navigation support
- ✅ ARIA labels on interactive elements
- ✅ High contrast mode compatible
- ✅ Screen reader friendly labels
- ✅ Focus indicators on buttons

## Performance Considerations

- **No additional API calls** - uses existing menu data
- **Lightweight calculations** - JavaScript only
- **Efficient DOM updates** - targeted selectors
- **CSS animations** - GPU-accelerated where possible
- **Memory efficient** - clears selections on reset

## Future Enhancements

### Potential Improvements
1. **Export functionality** - Save/print comparison
2. **URL sharing** - Share comparison link
3. **Dietary filters** - Filter by dietary category
4. **Custom metrics** - User-selected nutrients to compare
5. **Historical tracking** - Save favorite comparisons
6. **Advanced analytics** - Macronutrient ratios charts
7. **Allergen comparison** - Side-by-side allergen info
8. **Price per calorie** - Value for money comparison

### Possible API Enhancements
1. POST endpoint to save comparisons
2. GET endpoint to retrieve saved comparisons
3. Comparison history tracking

## Testing Checklist

- [ ] Compare with 2 menus
- [ ] Compare with 3 menus
- [ ] Reset comparison
- [ ] Test responsive design on mobile
- [ ] Test keyboard navigation
- [ ] Verify charts display correctly
- [ ] Test recommendations logic
- [ ] Verify calculations accuracy
- [ ] Test modal open/close
- [ ] Test checkbox disabled state when max reached

## Troubleshooting

### Common Issues

**Problem:** Comparison table not showing
- **Solution:** Ensure at least 2 menus are selected

**Problem:** Charts not displaying
- **Solution:** Check browser console for JavaScript errors

**Problem:** Styling looks broken
- **Solution:** Clear browser cache and hard refresh (Ctrl+Shift+R)

**Problem:** Buttons text overlapping
- **Solution:** This is handled by responsive CSS; check if font-size has been overridden

## Related Documentation

- [Menu System Architecture](./NAVBAR_GUIDE.html)
- [Nutritional Score Calculation](../guides/IMPLEMENTATION_SUMMARY.md)
- [Frontend Components](./NAVBAR_IMPROVEMENTS.md)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-04-29 | Initial implementation |
| | | - Side-by-side comparison table |
| | | - Visual charts (4 nutrients) |
| | | - Intelligent recommendations |
| | | - Responsive design |
| | | - Up to 3 menu comparison |

## Support

For issues or feature requests related to the Comparer feature, please contact the development team or create an issue in the project repository.

---

**Last Updated:** April 29, 2025
