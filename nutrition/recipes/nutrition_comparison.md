# Nutrition Comparison: Chipotle Steak and Pepper Bowls

## Comparison Table

| Nutrient | Website Value | JSON Value | Difference | Website % | JSON % |
|----------|---------------|------------|------------|-----------|--------|
| **Calories** | 497 kcal | 556.27 kcal | +59.27 kcal (+11.9%) | 100% | 100% |
| **Protein** | 38 g | 34.1 g | -3.9 g (-10.3%) | 30.6%* | 24.2% |
| **Carbohydrates** | 57 g | 58.1 g | +1.1 g (+1.9%) | 45.9%* | 41.3% |
| **Fat** | 13 g | 21.6 g | +8.6 g (+66.2%) | 23.5%* | 34.5% |
| **Fiber** | 4.5 g | 2.98 g | -1.52 g (-33.8%) | - | - |

*Website percentages calculated: Protein (38g × 4 kcal/g = 152 kcal ÷ 497 = 30.6%), Carbs (57g × 4 = 228 kcal ÷ 497 = 45.9%), Fat (13g × 9 = 117 kcal ÷ 497 = 23.5%)

## Key Differences

1. **Calories**: JSON shows 59 kcal more (+11.9%)
2. **Fat**: Largest difference - JSON shows 8.6g more fat (+66.2%)
3. **Protein**: Website shows 3.9g more protein (-10.3%)
4. **Fiber**: Website shows 1.52g more fiber (-33.8%)
5. **Carbohydrates**: Very close, only 1.1g difference (+1.9%)

## Possible Reasons for Differences

### 1. **Fat Content Discrepancy (Most Significant)**
   - **Olive oil usage**: The recipe uses olive oil multiple times (1 Tbsp for marinade, 1 Tbsp for steak, 2 tsp for vegetables). The JSON may be accounting for all oil used, while the website might be estimating less oil absorbed during cooking or using different assumptions about oil retention.
   - **Meat fat content**: The flank steak (1.5 lbs raw) may have different fat content assumptions. Raw meat loses fat during cooking, but the JSON might be using raw nutrition data while the website accounts for cooked weight/fat loss.
   - **Ingredient variations**: Different brands of ingredients (especially chipotle peppers in adobo sauce, which can vary in oil content) could contribute to fat differences.

### 2. **Protein Content Discrepancy**
   - **Cooking method**: Raw flank steak (1.5 lbs) loses weight during cooking (~25-30% shrinkage). The website might be calculating based on cooked weight, while the JSON uses raw ingredient weights.
   - **Meat grade/cut**: "Choice" grade flank steak can vary in protein content. The USDA database entry might differ from the specific cut used in the website's calculation.
   - **Ingredient rounding**: The website may be rounding or using different USDA entries for some ingredients.

### 3. **Calorie Difference**
   - The higher fat content in the JSON (21.6g vs 13g) contributes significantly: 8.6g × 9 kcal/g = 77.4 kcal difference from fat alone.
   - Combined with other minor differences in protein and carbs, this explains most of the 59 kcal difference.

### 4. **Fiber Content Discrepancy**
   - **Rice type**: Different rice varieties have different fiber content. The JSON uses "Rice, white, cooked, as ingredient" which may have different fiber than what the website calculated.
   - **Vegetable measurements**: The bell peppers and onions might be measured differently (raw vs cooked, different sizes).
   - **Corn**: Frozen corn fiber content can vary by brand and processing method.

### 5. **Methodological Differences**
   - **USDA database entries**: The JSON uses specific FDC IDs from USDA FoodData Central, which may differ from entries used by the website's nutrition calculator.
   - **Cooking losses**: The website might account for nutrient losses during cooking (especially water-soluble vitamins and some minerals), while the JSON sums raw ingredient values.
   - **Serving size**: The recipe makes 5 servings, but the website might be calculating per serving differently or using different assumptions about yield.

### 6. **Measurement Assumptions**
   - **Volume to weight conversions**: The recipe uses volume measurements (cups, tablespoons) which require conversion to grams. Different conversion factors or assumptions about ingredient density could cause variations.
   - **Ingredient substitutions**: The website might assume different brands or forms of ingredients (e.g., low-sodium soy sauce, different chipotle pepper brands).

## Recommendations

To align the values more closely:
1. Verify the actual cooked weight of the steak after cooking
2. Measure actual oil usage/retention during cooking
3. Use cooked ingredient weights where applicable
4. Verify specific USDA entries match the exact ingredients used
5. Consider accounting for cooking losses if precision is critical

