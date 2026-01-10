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
     - `fdc_id`: USDA FoodData Central ID
     - `amount`: Human-readable amount in format `"<quantity> <Unit>"` (e.g., `"0.5 Cup"`, `"1 Tbsp"`, `"2 Tsp"`)
     - The unit must match exactly one of the `MeasureUnit` enum values from `nutrition/scripts/measure_converter.py`
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
   - Use the `search_ingredient` MCP tool to search for ingredients by name
   - Use the `get_ingredient_details` MCP tool to retrieve full nutrition data for selected ingredients
   - Use the `save_ingredient` MCP tool to save ingredients to the local database
   - Select the most basic/appropriate ingredient from results
   - If no good match exists, note it for user assistance

4. Ensure all ingredients exist in `nutrition/ingredients/` directory (as `<fdc_id>.json` files)

5. Create recipe JSON file with:
   - Name
   - Tags (use existing tags or create new generic taxonomy tags if needed)
   - Ingredients (with fdc_id and amount)
   - Instructions (with step_id and text)
   - Empty `nutrition_facts: {}`

6. Calculate nutrition facts:
   - Use the `calculate_recipe_nutrition` MCP tool with the recipe file path
   - This will automatically populate the `nutrition_facts` and `macros` fields in the recipe file
