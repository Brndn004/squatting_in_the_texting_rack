# Instructions for Creating Recipes

## Recipe Source
- Recipe source will be provided as either:
  - A website URL with a recipe
  - A local file with recipe content
- Extract recipe name, serving size, ingredients, and instructions from the source
- Use the serving size exactly as specified in the source (do NOT adjust)

## Ingredient Lookup Rules

1. **Check Existing Ingredients First**
   - Always check `nutrition/ingredients/ingredient_lookup.json` before looking up new ingredients
   - Use existing ingredients when possible

2. **Prefer Basic Ingredients**
   - Choose simple, basic ingredients over complex branded/specific versions
   - Example: "Milk, whole" is preferred over "Milk, 3.25%, vitamin A and D added"
   - If you can't find a good enough match, make a note instead of choosing arbitrarily
   - User will help get the correct version if needed

3. **Ingredient Substitutions for Lifting-Focused Alternatives**
   - Replace fancy/plant-based ingredients with common lifting-related alternatives:
     - Plant-based milks → Use regular milk (whole/2%/skim) or whey protein
     - Plant-based yogurts → Use plain Greek yogurt
     - Plant-based protein powders → Use whey protein powder
     - Generic "berries" → Use a specific berry type (e.g., strawberries, blueberries)
     - Etc.
   - When in doubt, choose ingredients commonly used in lifting/nutrition contexts

## Recipe Structure

1. **Create Recipe JSON File**
   - File: `nutrition/recipes/<recipe_name>.json` (use lowercase with underscores)
   - Include: name, tags, ingredients, instructions, nutrition_facts (empty initially)

2. **Tags**
   - Prefer tags from the existing tag system (see `nutrition/tags.json` or `nutrition/scripts/recipe_tags.py`)
   - New tags can be created, but they should be generic taxonomy tags (e.g., "breakfast", "meal_prep", "simple")
   - Do NOT create recipe-specific tags (e.g., avoid "overnight_oats" - use generic tags like "breakfast" or "meal_prep" instead)
   - If creating a new tag, add it to `nutrition/scripts/recipe_tags.py` and use the `update_tags_database` MCP tool to update the tags database

3. **Ingredients**
   - Extract all ingredients from the recipe source
   - Each ingredient needs:
     - `fdc_id`: USDA FoodData Central ID (number)
     - `name`: Ingredient name (string)
     - `quantity`: Numeric quantity (e.g., `0.5`, `1.0`, `2.0`, `175.0`)
     - `measure_unit`: Unit string that matches exactly one of the `MeasureUnit` enum values from `nutrition/scripts/measure_converter.py`
     - Units must be capitalized exactly as shown (first letter capitalized, e.g., `"Cup"`, `"Tbsp"`, `"Tsp"`, `"Fl Oz"`, `"Oz"`, `"Gram"`, etc.)
   - Apply ingredient substitutions as specified above
   - Ensure all ingredients exist in `nutrition/ingredients/` directory before creating recipe

4. **Instructions**
   - Extract step-by-step instructions from the recipe source
   - Format as array of objects with `step_id` (starting from 1) and `text`

5. **Serving Size**
   - Match the source exactly (do NOT adjust serving size)
   - The recipe's `serving_size` field should reflect what the source specifies

## Workflow

1. Review recipe source (website or file) and extract:
   - Recipe name
   - Serving size
   - List of ingredients with quantities
   - Step-by-step instructions

2. Check `ingredient_lookup.json` for existing ingredients

3. Look up missing ingredients using MCP tools:
   - **Process ingredients ONE AT A TIME** (do not batch operations):
     - For each missing ingredient, complete the full cycle before moving to the next:
       1. **Before using `search_ingredient` tool:**
          - Verify ingredient is NOT in `ingredient_lookup.json`
          - Verify ingredient file does NOT exist in `nutrition/ingredients/` directory (as `<fdc_id>.json`)
          - Only search if both checks confirm the ingredient is missing
       2. Use the `search_ingredient` MCP tool to search for the ingredient by name
       3. Select the most basic/appropriate ingredient from results
       4. Use the `get_ingredient_details` MCP tool to retrieve full nutrition data for the selected ingredient
       5. Use the `save_ingredient` MCP tool to save the ingredient to the local database
       6. Only then proceed to the next ingredient
     - If no good match exists for an ingredient, note it for user assistance before moving on

4. Ensure all ingredients exist in `nutrition/ingredients/` directory (as `<fdc_id>.json` files)

5. Create recipe JSON file with:
   - Name
   - Tags (use existing tags or create new generic taxonomy tags if needed)
   - Ingredients (with fdc_id, name, quantity, and measure_unit)
   - Instructions (with step_id and text)
   - Empty `nutrition_facts: {}`
   - Empty `macros: {}`

6. Calculate nutrition facts:
   - **After** creating the recipe JSON file with all ingredients properly specified
   - Use the `calculate_recipe_nutrition` MCP tool with the recipe file path
   - The recipe path should be relative to the `nutrition/recipes/` directory (e.g., `"protein_overnight_oats.json"`)
   - The tool will:
     - Load all ingredient data by FDC ID from the `nutrition/ingredients/` directory
     - Convert ingredient amounts to grams using measure conversion
     - Scale nutrients based on gram weight for each ingredient
     - Sum all nutrients across all ingredients
     - Calculate per-serving nutrition facts (divided by `serving_size`)
     - Update the recipe file **in place** with calculated `nutrition_facts` and `macros` fields
   - The `nutrition_facts` object will contain all USDA nutrient data (protein, carbs, fats, vitamins, minerals, etc.)
   - The `macros` object will contain simplified protein, carbs, and fat breakdown with grams and percentages
   - If the calculation fails, report the error to the user immediately - do not attempt workarounds

7. Compare output with original source recipe:
   - **After** nutrition facts have been calculated, compare the final recipe with the original source
   - Extract the original recipe's nutrition information (calories, macros) if available from the source
   - Report the following to the user:
     - **Ingredient substitutions made**: List each substitution (original → substituted ingredient) with quantities
       - Example: "Soy Milk Protein Plus (⅔ cup) → Whole Milk (⅔ cup)"
     - **Calorie comparison**: 
       - Original calories (if available) vs calculated calories
       - Difference in calories (+/- X kcal)
       - Identify which ingredient substitutions contributed most to the difference
       - Explain the nutritional reasons (e.g., "Greek yogurt is denser and higher in fat/protein than plant-based yogurt")
     - **Macro differences**: Compare protein, carbs, and fat if original values are available
     - **Other notable differences**:
       - Serving size differences (if any)
       - Ingredient quantity differences (if any adjustments were made)
       - Any ingredients that couldn't be matched and were approximated
       - Any other significant nutritional or structural differences
   - Format the comparison clearly and concisely for the user
