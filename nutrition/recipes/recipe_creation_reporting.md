# Recipe Creation Reporting Instructions

## Compare Output with Original Source Recipe

**After** nutrition facts have been calculated, compare the final recipe with the original source and report directly to the user.

**IMPORTANT: Do NOT create any new files. Present the comparison directly to the user in your response.**

### Steps

1. **Extract original nutrition information** (if available from the source):
   - Calories
   - Macros (protein, carbs, fat)
   - Any other nutrition information provided

2. **Report the following to the user:**

   - **Nutrition Comparison Table**: Show a table comparing calories and macros (protein, carbs, fat) with percentage differences
     - Include columns: Metric | Original | Calculated | Difference | % Change
     - Example format:
       ```
       | Metric | Original | Calculated | Difference | % Change |
       |--------|----------|------------|------------|----------|
       | Calories | 484 kcal | 525.4 kcal | +41.4 kcal | +8.6% |
       | Protein | 40.0 g | 39.8 g | -0.2 g | -0.5% |
       | Carbs | 36.0 g | 42.6 g | +6.6 g | +18.3% |
       | Fat | 20.0 g | 22.4 g | +2.4 g | +12.0% |
       ```
     - Identify which ingredient substitutions contributed most to the differences
     - Explain the nutritional reasons (e.g., "Greek yogurt is denser and higher in fat/protein than plant-based yogurt")

   - **Other notable differences**:
     - Serving size differences (if any)
     - Ingredient quantity differences (if any adjustments were made)
     - Any ingredients that couldn't be matched and were approximated
     - Any other significant nutritional or structural differences

3. **Format the comparison clearly and concisely for the user**
   - Use clear headings and bullet points
   - Include the nutrition comparison table prominently
   - Highlight significant differences
   - Provide context for why differences might exist

