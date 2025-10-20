#!/usr/bin/env python3
"""
Workout data validator
Validates JSON output from LLM formatter against expected schema
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# JSON Schema for workout data
WORKOUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["date", "exercise", "sets", "reps", "weight"],
        "properties": {
            "date": {
                "type": "string",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                "description": "Date in YYYY-MM-DD format"
            },
            "exercise": {
                "type": "string",
                "minLength": 1,
                "description": "Exercise name in English"
            },
            "sets": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of sets performed"
            },
            "reps": {
                "type": "array",
                "items": {
                    "type": "integer",
                    "minimum": 1
                },
                "minItems": 1,
                "description": "Reps per set as an array"
            },
            "weight": {
                "type": "number",
                "minimum": 0,
                "description": "Weight used (can be 0 for bodyweight)"
            },
            "unit": {
                "type": ["string", "null"],
                "enum": ["kg", "lbs", "lb", None],
                "description": "Weight unit"
            },
            "rpe": {
                "type": ["number", "null"],
                "minimum": 1,
                "maximum": 10,
                "description": "Rate of Perceived Exertion (1-10 scale)"
            },
            "rest_times": {
                "type": ["array", "null"],
                "items": {
                    "type": ["string", "null"],
                    "pattern": "^\\d+:\\d{2}$|^null$"
                },
                "description": "Rest times between sets (MM:SS format)"
            },
            "notes": {
                "type": ["string", "null"],
                "description": "Training notes, form cues, etc."
            }
        },
        "additionalProperties": False
    }
}


class WorkoutDataValidator:
    """Validates workout data against schema and business rules"""

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize validator

        Args:
            schema: Optional custom JSON schema (defaults to WORKOUT_SCHEMA)
        """
        self.schema = schema or WORKOUT_SCHEMA

    def validate(self, data: Any, strict: bool = True) -> Dict[str, Any]:
        """
        Validate workout data

        Args:
            data: Data to validate (should be list of workout dicts)
            strict: If True, apply strict business rules (reps count must match sets, etc.)

        Returns:
            Dict with:
                - valid: bool
                - errors: List[str] (validation errors)
                - warnings: List[str] (non-critical issues)
        """
        errors = []
        warnings = []

        # Schema validation
        try:
            validate(instance=data, schema=self.schema)
            logger.debug("JSON schema validation passed")
        except ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            logger.error(f"Schema validation error: {e.message}")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }

        # Business rule validation
        if not isinstance(data, list):
            errors.append("Data must be a list")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

        for i, entry in enumerate(data):
            # Cross-field validation: reps array length must match sets count
            if strict and 'reps' in entry and 'sets' in entry:
                if len(entry['reps']) != entry['sets']:
                    errors.append(
                        f"Entry {i} ({entry.get('exercise')}): "
                        f"reps array length ({len(entry['reps'])}) must match sets ({entry['sets']})"
                    )

            # Date validation: must be valid date
            if 'date' in entry:
                try:
                    datetime.strptime(entry['date'], '%Y-%m-%d')
                except ValueError:
                    errors.append(
                        f"Entry {i} ({entry.get('exercise')}): "
                        f"Invalid date '{entry['date']}' (use YYYY-MM-DD)"
                    )

            # Rest times validation: if present, length should match sets-1 or sets
            if 'rest_times' in entry and entry['rest_times'] is not None:
                rest_count = len(entry['rest_times'])
                sets = entry.get('sets', 0)
                if rest_count not in [sets - 1, sets]:
                    warnings.append(
                        f"Entry {i} ({entry.get('exercise')}): "
                        f"rest_times count ({rest_count}) unusual for {sets} sets"
                    )

            # Weight validation: warn if 0 weight (might be bodyweight)
            if entry.get('weight') == 0:
                warnings.append(
                    f"Entry {i} ({entry.get('exercise')}): "
                    f"weight is 0 (bodyweight exercise?)"
                )

            # RPE validation: warn if outside typical range
            if 'rpe' in entry and entry['rpe'] is not None:
                if entry['rpe'] < 5:
                    warnings.append(
                        f"Entry {i} ({entry.get('exercise')}): "
                        f"RPE {entry['rpe']} is very low (typical range 6-10)"
                    )

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def validate_and_fix(self, data: Any) -> Dict[str, Any]:
        """
        Validate and attempt to auto-fix common issues

        Args:
            data: Data to validate and fix

        Returns:
            Dict with:
                - valid: bool
                - data: Fixed data (if fixable)
                - errors: List[str]
                - warnings: List[str]
                - fixes_applied: List[str]
        """
        errors = []
        warnings = []
        fixes_applied = []

        if not isinstance(data, list):
            return {
                'valid': False,
                'errors': ["Data must be a list"],
                'warnings': [],
                'fixes_applied': []
            }

        fixed_data = []

        for i, entry in enumerate(data):
            entry = dict(entry)  # Copy to avoid modifying original

            # Fix: Normalize unit (lb → lbs)
            if entry.get('unit') == 'lb':
                entry['unit'] = 'lbs'
                fixes_applied.append(f"Entry {i}: Normalized unit 'lb' → 'lbs'")

            # Fix: Add default unit if missing
            if 'unit' not in entry or entry['unit'] is None:
                entry['unit'] = 'kg'
                fixes_applied.append(f"Entry {i}: Added default unit 'kg'")

            # Fix: Extend reps array if too short
            if 'reps' in entry and 'sets' in entry:
                if len(entry['reps']) < entry['sets']:
                    # Pad with last value
                    last_rep = entry['reps'][-1] if entry['reps'] else 0
                    while len(entry['reps']) < entry['sets']:
                        entry['reps'].append(last_rep)
                    fixes_applied.append(
                        f"Entry {i}: Extended reps array to match {entry['sets']} sets"
                    )
                elif len(entry['reps']) > entry['sets']:
                    # Truncate
                    entry['reps'] = entry['reps'][:entry['sets']]
                    fixes_applied.append(
                        f"Entry {i}: Truncated reps array to match {entry['sets']} sets"
                    )

            # Fix: Remove empty notes
            if 'notes' in entry and entry['notes'] == '':
                entry['notes'] = None
                fixes_applied.append(f"Entry {i}: Converted empty notes to null")

            fixed_data.append(entry)

        # Validate fixed data
        validation_result = self.validate(fixed_data, strict=True)

        return {
            'valid': validation_result['valid'],
            'data': fixed_data,
            'errors': validation_result['errors'],
            'warnings': validation_result['warnings'],
            'fixes_applied': fixes_applied
        }


# Convenience function
def validate_workout_data(data: Any, strict: bool = True) -> Dict[str, Any]:
    """
    Validate workout data

    Args:
        data: Data to validate
        strict: If True, apply strict business rules

    Returns:
        Validation result dict
    """
    validator = WorkoutDataValidator()
    return validator.validate(data, strict=strict)


if __name__ == "__main__":
    # Quick test
    test_data = [
        {
            "date": "2024-01-15",
            "exercise": "Leg Curl",
            "sets": 3,
            "reps": [17, 15, 15],
            "weight": 43,
            "unit": "kg",
            "rpe": 8.5,
            "rest_times": ["3:00", "3:00", "3:00"],
            "notes": None
        }
    ]

    validator = WorkoutDataValidator()
    result = validator.validate(test_data)

    if result['valid']:
        print("✅ Validation passed!")
        if result['warnings']:
            print(f"⚠️  Warnings: {result['warnings']}")
    else:
        print(f"❌ Validation failed!")
        print(f"Errors: {result['errors']}")
