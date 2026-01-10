# Ingredients Missing Volume Information

This file tracks ingredients that **cannot be converted by `measure_converter.py`** for volume units (Cup, Tbsp, Tsp, Fl Oz). These ingredients lack foodPortions that match volume units, making volume conversions impossible.

**Important:** 
- This file identifies ingredients that **cannot be converted by `measure_converter.py`** for volume units (Cup, Tbsp, Tsp, Fl Oz)
- Weight units (Gram, Oz, Lb, Kg) do NOT need volume info - they convert directly to grams
- Ingredients listed here lack foodPortions that match volume units, making volume conversions impossible

**Last Updated:** 2025-01-10

## Summary

- **Total ingredients:** 27
- **Ingredients WITH volume unit support:** 17
- **Ingredients MISSING ALL volume unit support:** 10

## Ingredients Missing ALL Volume Unit Support

These ingredients have NO foodPortions that match Cup, Tbsp, Tsp, or Fl Oz. They cannot be converted by `measure_converter.py` for any volume unit.

### High Priority

1. **FDC 2346396**: Oats, whole grain, rolled, old fashioned
   - Current portions: RACC only (40g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Cup (typically 1 cup = ~80g)
   - **Command:** `python3 add_volume_to_ingredient.py 2346396 1.0 Cup 80.0`

2. **FDC 2710819**: Chia seeds, dry, raw
   - Current portions: RACC only (45g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Tbsp (typically 1 Tbsp = ~15g)
   - **Command:** `python3 add_volume_to_ingredient.py 2710819 1.0 Tbsp 15.0`

3. **FDC 2259794**: Yogurt, Greek, plain, whole milk
   - Current portions: RACC only (170g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Cup (typically 1 cup = ~245g)
   - **Command:** `python3 add_volume_to_ingredient.py 2259794 1.0 Cup 245.0`

4. **FDC 2346384**: Cottage cheese, full fat, large or small curd
   - Current portions: RACC only (110g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Cup (typically 1 cup = ~226g)
   - **Command:** `python3 add_volume_to_ingredient.py 2346384 1.0 Cup 226.0`

5. **FDC 2346411**: Blueberries, raw
   - Current portions: RACC only (140g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Cup (typically 1 cup = ~148g)
   - **Command:** `python3 add_volume_to_ingredient.py 2346411 1.0 Cup 148.0`

6. **FDC 748608**: Oil, olive, extra virgin
   - Current portions: RACC only (90.7g for 100ml)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Tbsp (typically 1 Tbsp = ~13.5g), Tsp (typically 1 Tsp = ~4.5g)
   - **Commands:**
     - `python3 add_volume_to_ingredient.py 748608 1.0 Tbsp 13.5`
     - `python3 add_volume_to_ingredient.py 748608 1.0 Tsp 4.5`

7. **FDC 328637**: Cheese, cheddar
   - Current portions: shredded (105g), RACC (17g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Cup shredded (typically 1 cup shredded = ~113g)
   - **Command:** `python3 add_volume_to_ingredient.py 328637 1.0 Cup 113.0`

8. **FDC 790646**: Onions, yellow, raw
   - Current portions: Edible portion (143g), RACC (85g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Cup chopped (typically 1 cup chopped = ~160g)
   - **Command:** `python3 add_volume_to_ingredient.py 790646 1.0 Cup 160.0`

9. **FDC 173177**: Beverages, Whey protein powder isolate
   - Current portions: scoop (86g for 3 scoops)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Recommended:** Tbsp (typically 1 Tbsp = ~15g, or 1 scoop ≈ 2 Tbsp = ~30g)
   - **Command:** `python3 add_volume_to_ingredient.py 173177 1.0 Tbsp 15.0`

### Lower Priority (Typically Measured by Weight)

10. **FDC 2646171**: Chicken, thigh, boneless, skinless, raw
   - Current portions: RACC only (114g)
   - **Missing:** All volume units (Cup, Tbsp, Tsp, Fl Oz)
   - **Note:** Typically measured by weight (Oz, Gram), not volume.

## Ingredients with Partial Volume Unit Support

These ingredients have SOME volume unit support but are missing others. They can handle some volume conversions but not all.

- **FDC 2705385**: Milk, whole
  - **Has:** Cup, Fl Oz, Tsp
  - **Missing:** Tbsp

- **FDC 2705386**: Milk, reduced fat (2%)
  - **Has:** Cup, Fl Oz, Tsp
  - **Missing:** Tbsp

- **FDC 169736**: Pasta, dry, enriched
  - **Has:** Cup, Tsp
  - **Missing:** Tbsp, Fl Oz

- **FDC 2709796**: Parsley, raw
  - **Has:** Cup, Tsp
  - **Missing:** Tbsp, Fl Oz

- **FDC 2709898**: Cauliflower, frozen, cooked, no added fat
  - **Has:** Cup, Tsp
  - **Missing:** Tbsp, Fl Oz

- **FDC 2709977**: Peppers, red, cooked
  - **Has:** Cup, Tsp
  - **Missing:** Tbsp, Fl Oz

- **FDC 2710793**: Carrots, cooked, as ingredient
  - **Has:** Cup, Fl Oz, Tsp
  - **Missing:** Tbsp

- **FDC 167914**: Pork, cured, bacon, cooked, baked
  - **Has:** Cup
  - **Missing:** Tbsp, Tsp, Fl Oz

- **FDC 169661**: Syrups, maple
  - **Has:** Cup, Tbsp, Tsp
  - **Missing:** Fl Oz

- **FDC 170931**: Spices, pepper, black
  - **Has:** Tbsp, Tsp
  - **Missing:** Cup, Fl Oz

- **FDC 171325**: Spices, garlic powder
  - **Has:** Tbsp, Tsp
  - **Missing:** Cup, Fl Oz

- **FDC 171327**: Spices, onion powder
  - **Has:** Tbsp, Tsp
  - **Missing:** Cup, Fl Oz

- **FDC 171329**: Spices, paprika
  - **Has:** Tbsp, Tsp
  - **Missing:** Cup, Fl Oz

- **FDC 173468**: Salt, table
  - **Has:** Cup, Tbsp, Tsp
  - **Missing:** Fl Oz

- **FDC 173471**: Vanilla extract
  - **Has:** Cup, Tbsp, Tsp
  - **Missing:** Fl Oz

- **FDC 2710168**: Ghee, clarified butter
  - **Has:** Cup, Tbsp, Tsp
  - **Missing:** Fl Oz

## Notes

- **What this file tracks:**
  - Ingredients that lack foodPortions matching volume units (Cup, Tbsp, Tsp, Fl Oz)
  - These ingredients cannot be converted by `measure_converter.py` for volume units
  - Weight units (Gram, Oz, Lb, Kg) convert directly to grams and never need volume info
- Volume conversions are approximate and may vary based on ingredient density, packing, and preparation method
- When adding volume information, verify conversions using reliable sources or kitchen scales
- Some ingredients (like chicken and bacon) are typically measured by weight or count, not volume
- RACC = Reference Amount Customarily Consumed (regulatory serving size in grams)

## Adding Volume Information

To add volume information to any ingredient, use:

```bash
python3 add_volume_to_ingredient.py <fdc_id> <amount> <unit> <grams>
```

**Example:**
```bash
# Add 1 cup = 80g for oats
python3 add_volume_to_ingredient.py 2346396 1.0 Cup 80.0
```

**Arguments:**
- `fdc_id`: USDA FoodData Central ID
- `amount`: Base quantity for the unit (e.g., 1.0 for "1 cup")
- `unit`: MeasureUnit enum value (e.g., "Cup", "Tbsp", "Tsp")
- `grams`: Weight in grams for that volume amount
