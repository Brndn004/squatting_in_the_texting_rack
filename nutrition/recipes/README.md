# Recipes

This folder contains recipe JSON files. Each recipe defines ingredients, instructions, tags, and calculated nutrition facts.

## Recipe Structure

Each recipe JSON file contains the following fields:

- **`name`** (string): Recipe name (e.g., "Warm Milk")
- **`tags`** (array of strings): Recipe tags from the `RecipeTag` enum (e.g., `["drink", "warm", "simple"]`)
- **`ingredients`** (array of objects): List of ingredients, each with:
  - `fdc_id` (integer): USDA FoodData Central ID for the ingredient
  - `amount` (string): Human-readable amount (e.g., "1 Cup", "0.25 Tsp")
    - Format: `"<quantity> <Unit>"` where quantity is a decimal number and Unit matches `MeasureUnit` enum exactly
    - Examples: "1 Cup", "2 Tbsp", "0.5 Tsp", "3 Oz"
- **`instructions`** (array of objects): Step-by-step instructions, each with:
  - `step_id` (integer): Sequential step number starting from 1
  - `text` (string): Instruction text
- **`nutrition_facts`** (object): Calculated nutrition facts (automatically generated)
  - Keys: Nutrient names with units (e.g., "Energy (kcal)", "Protein (g)")
  - Values: Calculated amounts

## Creating a New Recipe

### Step 1: Ensure Ingredients Exist

All ingredients must exist in the `nutrition/ingredients/` folder. To add a new ingredient:

```bash
python nutrition/scripts/usda_lookup.py <ingredient name>
```

Select the correct ingredient from the search results. The ingredient will be saved as `<FDC_ID>.json`.

### Step 2: Create Recipe JSON File

Create a new JSON file named `<recipe_name>.json` (use lowercase with underscores, e.g., `warm_milk.json`).

Start with this template:

```json
{
  "name": "Recipe Name",
  "tags": [],
  "ingredients": [],
  "instructions": [],
  "nutrition_facts": {}
}
```

### Step 3: Add Recipe Name

Set the `name` field to a human-readable recipe name.

### Step 4: Add Tags

Add tags from the `RecipeTag` enum. Valid tags are defined in `nutrition/scripts/recipe_tags.py`.

To see all available tags:
```bash
python nutrition/scripts/tag_management.py
```

### Step 5: Add Ingredients

For each ingredient, add an object with:
- `fdc_id`: The USDA FDC ID (found in the ingredient filename or via `ingredient_management.py`)
- `amount`: Human-readable amount in strict format

**Finding FDC IDs:**
```bash
python nutrition/scripts/ingredient_management.py
```
Search for the ingredient name to find its FDC ID.

**Amount Format Rules:**
- Quantity must be a decimal number (e.g., `1`, `0.25`, `2.5`)
- Unit must match `MeasureUnit` enum exactly (capitalized first letter)
- Format: `"<quantity> <Unit>"` with a space between
- Examples: `"1 Cup"`, `"0.25 Tsp"`, `"2 Tbsp"`, `"3 Oz"`

**Valid Units:**
- Volume: `Cup`, `Tbsp`, `Tsp`, `Fl Oz`, `Pint`, `Quart`, `Gallon`, `Ml`, `Liter`
- Weight: `Oz`, `Lb`, `Gram`, `Kg`
- Count: `Piece`, `Whole`, `Slice`, `Clove`, `Head`, `Stalk`, `Bunch`

### Step 6: Add Instructions

Add instruction objects with sequential `step_id` values starting from 1:

```json
"instructions": [
  {
    "step_id": 1,
    "text": "First step instruction."
  },
  {
    "step_id": 2,
    "text": "Second step instruction."
  }
]
```

### Step 7: Calculate Nutrition Facts

Run the nutrition calculation script to automatically compute nutrition facts:

```bash
python nutrition/scripts/calculate_recipe_nutrition.py
```

This script:
1. Parses ingredient amounts
2. Converts amounts to grams using USDA foodPortions
3. Scales nutrients from per-100g to actual gram weights
4. Sums all nutrients across ingredients
5. Updates the recipe's `nutrition_facts` field

The script processes all recipes, so you can run it anytime to recalculate nutrition facts based on ingredient data in the database.

## Maintaining Recipes

### Update Tags Database

After adding new tags to `nutrition/scripts/recipe_tags.py`, update the tags database:

```bash
python nutrition/scripts/tag_management.py
```

This updates `nutrition/tags.json` with all tags from the enum.

### Validate Recipe Tags

Validate that all recipes use valid tags:

```bash
python nutrition/scripts/validate_recipes.py
```

### Recalculate Nutrition Facts

Whenever ingredient data is updated, recalculate all recipe nutrition facts:

```bash
python nutrition/scripts/calculate_recipe_nutrition.py
```

This ensures all recipes reflect the ingredient nutrition data in the database.

### List All Recipes

To see all recipes in the database:

```bash
ls nutrition/recipes/*.json
```

### View Recipe Details

Open any recipe JSON file to view its full structure and nutrition facts.

## Example Recipe

See `warm_milk.json` for a complete example recipe with:
- Multiple ingredients with different units
- Step-by-step instructions
- Calculated nutrition facts

