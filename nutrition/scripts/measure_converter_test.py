#!/usr/bin/env python3
"""Tests for measure_converter library."""

import unittest
import measure_converter


class TestFindFoodPortion(unittest.TestCase):
    """Tests for find_food_portion function."""

    def test_should_return_matching_portion_when_modifier_matches(self):
        """Test finding portion by exact modifier match."""
        # Precondition
        food_portions = [
            {
                "id": 123,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 2.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 123)
        self.assertEqual(weight, 488.0)

    def test_should_return_matching_portion_when_description_contains_unit(self):
        """Test finding portion by description match."""
        # Precondition
        food_portions = [
            {
                "id": 456,
                "modifier": "10205",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 456)
        self.assertEqual(weight, 244.0)

    def test_should_calculate_weight_based_on_quantity_when_base_amount_is_one(self):
        """Test weight calculation for base amount of 1."""
        # Precondition
        food_portions = [
            {
                "id": 789,
                "modifier": "tbsp",
                "gramWeight": 13.0,
                "portionDescription": "1 tablespoon",
            }
        ]
        quantity = 2.0
        unit = measure_converter.MeasureUnit.Tbsp

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(weight, 26.0)

    def test_should_calculate_weight_based_on_base_amount_when_description_has_number(self):
        """Test weight calculation when description has non-1 base amount."""
        # Precondition
        food_portions = [
            {
                "id": 999,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "2 cups",
            }
        ]
        quantity = 4.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(weight, 488.0)

    def test_should_use_base_amount_one_when_description_has_no_number(self):
        """Test weight calculation when description has no base amount."""
        # Precondition
        food_portions = [
            {
                "id": 111,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "cup",
            }
        ]
        quantity = 2.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(weight, 488.0)

    def test_should_prefer_modifier_match_over_description_match(self):
        """Test that modifier match has higher priority than description match."""
        # Precondition
        food_portions = [
            {
                "id": 200,
                "modifier": "tbsp",
                "gramWeight": 13.0,
                "portionDescription": "1 teaspoon",
            },
            {
                "id": 201,
                "modifier": "10205",
                "gramWeight": 15.0,
                "portionDescription": "1 tablespoon",
            },
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Tbsp

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 200)
        self.assertEqual(weight, 13.0)

    def test_should_prefer_description_start_match_over_contains_match(self):
        """Test that description starting with unit has higher priority."""
        # Precondition
        food_portions = [
            {
                "id": 300,
                "modifier": "xyz",
                "gramWeight": 20.0,
                "portionDescription": "cup of something",
            },
            {
                "id": 301,
                "modifier": "abc",
                "gramWeight": 10.0,
                "portionDescription": "something cup",
            },
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 300)
        self.assertEqual(weight, 20.0)

    def test_should_skip_portions_with_zero_gram_weight(self):
        """Test that portions with zero or negative gramWeight are skipped."""
        # Precondition
        food_portions = [
            {
                "id": 400,
                "modifier": "cup",
                "gramWeight": 0.0,
                "portionDescription": "1 cup",
            },
            {
                "id": 401,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            },
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 401)
        self.assertEqual(weight, 244.0)

    def test_should_raise_error_when_no_food_portions_provided(self):
        """Test error when food_portions list is empty."""
        # Precondition
        food_portions = []
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        with self.assertRaises(measure_converter.MeasureMatchError) as context:
            measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertIn("No foodPortions available", str(context.exception))

    def test_should_raise_error_when_no_matching_portion_found(self):
        """Test error when no portion matches the unit."""
        # Precondition
        food_portions = [
            {
                "id": 500,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Piece

        # Under test
        with self.assertRaises(measure_converter.MeasureMatchError) as context:
            measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertIn("Could not find matching foodPortion", str(context.exception))

    def test_should_raise_error_when_quantity_is_zero(self):
        """Test error when quantity is zero."""
        # Precondition
        food_portions = [
            {
                "id": 600,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 0.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        with self.assertRaises(ValueError) as context:
            measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertIn("must be greater than zero", str(context.exception))

    def test_should_raise_error_when_quantity_is_negative(self):
        """Test error when quantity is negative."""
        # Precondition
        food_portions = [
            {
                "id": 700,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = -1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        with self.assertRaises(ValueError) as context:
            measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertIn("must be greater than zero", str(context.exception))

    def test_should_match_case_insensitive_modifier(self):
        """Test that modifier matching is case-insensitive."""
        # Precondition
        food_portions = [
            {
                "id": 800,
                "modifier": "CUP",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 800)
        self.assertEqual(weight, 244.0)

    def test_should_match_unit_alias_in_modifier(self):
        """Test that unit aliases (like 'cups' plural) match correctly."""
        # Precondition
        food_portions = [
            {
                "id": 900,
                "modifier": "cups",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 1.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(portion["id"], 900)
        self.assertEqual(weight, 244.0)

    def test_should_handle_decimal_quantities(self):
        """Test that decimal quantities are handled correctly."""
        # Precondition
        food_portions = [
            {
                "id": 1000,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1 cup",
            }
        ]
        quantity = 0.5
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(weight, 122.0)

    def test_should_handle_decimal_base_amount_in_description(self):
        """Test that decimal base amounts in description are handled correctly."""
        # Precondition
        food_portions = [
            {
                "id": 1100,
                "modifier": "cup",
                "gramWeight": 244.0,
                "portionDescription": "1.5 cups",
            }
        ]
        quantity = 3.0
        unit = measure_converter.MeasureUnit.Cup

        # Under test
        portion, weight = measure_converter.find_food_portion(quantity, unit, food_portions)

        # Postcondition
        self.assertEqual(weight, 488.0)


if __name__ == "__main__":
    unittest.main()

