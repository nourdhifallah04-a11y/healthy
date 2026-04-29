# Quick Start Guide - Comparer Feature

## For Users

### Step 1: Find the Compare Button
On any menu card, you'll see two buttons at the bottom:
- **"Ajouter"** (green) - Add to cart
- **"Comparer"** (orange) - Compare with other menus

### Step 2: Click "Comparer"
Click the orange **"Comparer"** button to open the comparison modal.

### Step 3: Select Menus
- Check the checkboxes for **2-3 menus** you want to compare
- Selected menus will be highlighted in green
- You'll see a counter showing how many menus are selected

### Step 4: View Comparison
Once you select 2+ menus, the comparison will automatically appear:

**Comparison Table**
- Shows all nutritional metrics (calories, proteins, etc.)
- Visual bars compare values relative to each other

**Charts**
- 4 bar charts show calories, proteins, carbs, and fats
- Easy visual comparison of key nutrients

**Recommendations**
- AI-generated insights comparing the menus
- Highlights best options for different needs

### Step 5: Reset or Close
- Click **"↺ Réinitialiser"** to clear selections
- Click the **X** button to close the modal

---

## For Developers

### Adding the Feature to Your Project

The feature is already integrated! No additional setup needed beyond what's already done.

### Key Files to Review
```
templates/menu/menu.html          # Modal HTML
static/menu/menu.js               # Comparison logic
static/menu/menu.css              # Styling
docs/features/COMPARER_FEATURE.md # Full documentation
```

### Main Functions

```javascript
// Open the comparison modal
openCompareModal()

// Select/deselect a menu for comparison
toggleMenuSelection(menuId, name, calories, protein, carbs, fat, fiber, score)

// Reset all selections
resetComparison()

// Close the modal
closeCompareModal()
```

### Example: Accessing Selected Menus

```javascript
// Get all selected menus
Array.from(comparisonState.selectedMenus.values())

// Check number of selected menus
comparisonState.selectedMenus.size

// Get a specific menu
comparisonState.selectedMenus.get(menuId)
```

### Customizing Behavior

To change the maximum number of menus that can be compared:
```javascript
// In menu.js, find:
const comparisonState = {
    selectedMenus: new Map(),
    maxMenusToCompare: 3  // Change this number
};
```

To modify recommendation logic, edit the `displayComparisonRecommendation()` function.

### Styling Customization

All colors use CSS variables defined at the top of `menu.css`:
```css
:root {
    --vert-sauge: #9BBF8F;        /* Primary green */
    --accent-miel: #D9B48B;       /* Compare button color */
    --beige-pale: #FDF7ED;        /* Background */
    /* ... more colors ... */
}
```

---

## Common Use Cases

### Use Case 1: Comparing Similar Menus
A user might want to compare two "High Protein" menus to see which one has better nutrition.

**Result**: The table clearly shows protein content side-by-side, and the recommendation highlights which is better.

### Use Case 2: Finding the Lowest Calorie Option
A user wants to compare 3 menus to find the lowest calorie one.

**Result**: The calories chart and recommendation clearly identify which menu has the fewest calories.

### Use Case 3: Balanced Nutrition Selection
A user wants to find a menu with good balance across all nutrients.

**Result**: The comparison shows the nutritional profile and highlights which menu has the best overall score.

---

## Troubleshooting

### "Compare button doesn't appear on menu cards"
- Make sure `menu.js` is fully loaded
- Check browser console for errors (F12 → Console)
- Hard refresh the page (Ctrl+Shift+R)

### "Comparison table doesn't show"
- You need to select **at least 2 menus** to see the comparison
- Check that checkboxes are actually checked

### "Charts look wrong"
- Try refreshing the page
- Clear browser cache
- Check if CSS file loaded properly (F12 → Network tab)

### "Recommendations don't make sense"
- Recommendations compare specific metrics
- For 2 menus: compares each nutrient
- For 3 menus: shows best in each category

---

## Tips & Tricks

### Pro Tip 1: Mobile Usage
On mobile, the buttons stack vertically. The Compare button is below the "Add" button for easier access.

### Pro Tip 2: Keyboard Navigation
- Tab to navigate between menus
- Space to check/uncheck a menu
- All buttons are keyboard accessible

### Pro Tip 3: Visual Comparison
The visual bars make it easy to spot which menu is "best" for a particular nutrient at a glance.

### Pro Tip 4: Share Insights
While there's no built-in sharing yet, you can take a screenshot of the comparison to share with friends!

---

## Feature Roadmap

### Already Implemented (v1.0)
✅ Side-by-side comparison table
✅ Visual comparison charts
✅ Intelligent recommendations
✅ Up to 3 menu comparison
✅ Responsive design
✅ Keyboard accessible

### Planned for Future Versions
⏳ Export to PDF/Image
⏳ Share comparison via URL
⏳ Save favorite comparisons
⏳ Advanced filtering options
⏳ Historical tracking
⏳ More detailed analytics

---

## Support & Feedback

- **Report Bugs**: Contact development team
- **Feature Requests**: Suggest new comparison metrics
- **Questions**: See [COMPARER_FEATURE.md](./COMPARER_FEATURE.md) for technical details

---

**Last Updated**: April 29, 2025
