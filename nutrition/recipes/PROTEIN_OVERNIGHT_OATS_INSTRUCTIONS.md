# Instructions for Creating Protein Overnight Oats Recipe

## Recipe Source
- Website: https://www.theconsciousplantkitchen.com/protein-overnight-oats/
- Recipe Name: Protein Overnight Oats
- Serving Size: 1 jar (as specified on website)

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
     - "Soy Milk Protein Plus" → Use regular milk (whole/2%/skim) or whey protein
     - "Plant-Based Yogurt" → Use plain Greek yogurt
     - "Vanilla Protein Powder" → Use whey protein powder (vanilla flavor if available, otherwise plain)

4. **Berry Type**
   - Use strawberries as the berry type (not generic berries)

## Recipe Structure

1. **Create Recipe JSON File** (not a meal)
   - File: `nutrition/recipes/protein_overnight_oats.json`
   - Include: name, tags, ingredients, instructions, nutrition_facts (empty initially)

2. **Tags**
   - Do NOT add "overnight_oats" tag
   - Add appropriate tags from existing tag system (e.g., "breakfast", "high_protein", etc.)

3. **Ingredients from Recipe**
   - ½ cup Old-Fashioned Rolled Oats
   - 1 tablespoon Chia Seeds
   - ⅔ cup Soy Milk Protein Plus → Substitute with regular milk or whey protein
   - 2 teaspoons Maple Syrup
   - 2 tablespoons Vanilla Protein Powder → Substitute with whey protein powder
   - ½ cup Plant-Based Yogurt → Substitute with plain Greek yogurt
   - ½ cup Berries → Use strawberries

4. **Instructions**
   - Follow the recipe instructions from the website

5. **Serving Size**
   - Match website exactly: 1 serving (1 jar)
   - Do NOT adjust serving size

## Workflow

1. Check `ingredient_lookup.json` for existing ingredients
2. Look up missing ingredients using `usda_lookup.py`
3. Ensure all ingredients exist in `nutrition/ingredients/` directory
4. Create recipe JSON file with all ingredients and instructions
5. Run `calculate_recipe_nutrition.py` to calculate nutrition facts
6. Do NOT create a meal file (this is a recipe, not a meal)

