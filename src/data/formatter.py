#!/usr/bin/env python3
"""
LLM-based workout log formatter
Converts messy Chinese training logs to structured JSON/CSV format
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Exercise name mapping: Chinese → English
EXERCISE_MAPPING = {
    # Legs
    "腿弯举": "Leg Curl",
    "坐姿腿弯举": "Seated Leg Curl",
    "俯卧腿弯举": "Lying Leg Curl",
    "硬拉": "Deadlift",
    "罗马尼亚硬拉": "Romanian Deadlift",
    "直腿硬拉": "Stiff-Legged Deadlift",
    "深蹲": "Squat",
    "史密斯深蹲": "Smith Squat",
    "杠铃深蹲": "Barbell Squat",
    "哑铃深蹲": "Dumbbell Squat",
    "前蹲": "Front Squat",
    "后蹲": "Back Squat",
    "坐姿蹬腿": "Leg Press",
    "倒蹬": "Leg Press",
    "腿举": "Leg Press",
    "腿屈伸": "Leg Extension",
    "坐姿腿屈伸": "Leg Extension",
    "髋外展": "Hip Abduction",
    "髋内收": "Hip Adduction",
    "臀桥": "Hip Thrust",
    "臀推": "Hip Thrust",
    "提踵": "Calf Raise",
    "站姿提踵": "Standing Calf Raise",
    "坐姿提踵": "Seated Calf Raise",

    # Back
    "引体向上": "Pull-up",
    "宽握引体": "Wide-Grip Pull-up",
    "窄握引体": "Close-Grip Pull-up",
    "高位下拉": "Lat Pulldown",
    "宽握下拉": "Wide-Grip Lat Pulldown",
    "窄握下拉": "Close-Grip Lat Pulldown",
    "坐姿划船": "Seated Cable Row",
    "杠铃划船": "Barbell Row",
    "哑铃划船": "Dumbbell Row",
    "单臂哑铃划船": "Single-Arm Dumbbell Row",
    "训练凳单边哑铃划船": "Single-Arm Dumbbell Row",
    "训练凳划船": "Dumbbell Row",
    "T杠划船": "T-Bar Row",
    "面拉": "Face Pull",

    # Chest
    "卧推": "Bench Press",
    "杠铃卧推": "Barbell Bench Press",
    "哑铃卧推": "Dumbbell Bench Press",
    "上斜卧推": "Incline Bench Press",
    "下斜卧推": "Decline Bench Press",
    "史密斯卧推": "Smith Bench Press",
    "飞鸟": "Dumbbell Fly",
    "哑铃飞鸟": "Dumbbell Fly",
    "夹胸": "Cable Fly",
    "龙门架夹胸": "Cable Fly",
    "俯卧撑": "Push-up",

    # Shoulders
    "推举": "Overhead Press",
    "肩推": "Shoulder Press",
    "杠铃推举": "Barbell Overhead Press",
    "哑铃推举": "Dumbbell Shoulder Press",
    "阿诺德推举": "Arnold Press",
    "侧平举": "Lateral Raise",
    "哑铃侧平举": "Dumbbell Lateral Raise",
    "前平举": "Front Raise",
    "后束飞鸟": "Reverse Fly",
    "俯身飞鸟": "Bent-Over Fly",
    "直立划船": "Upright Row",
    "耸肩": "Shrug",

    # Arms
    "弯举": "Curl",
    "二头弯举": "Bicep Curl",
    "杠铃弯举": "Barbell Curl",
    "哑铃弯举": "Dumbbell Curl",
    "锤式弯举": "Hammer Curl",
    "集中弯举": "Concentration Curl",
    "牧师凳弯举": "Preacher Curl",
    "三头下压": "Tricep Pushdown",
    "绳索下压": "Cable Pushdown",
    "臂屈伸": "Dip",
    "窄距卧推": "Close-Grip Bench Press",
    "颈后臂屈伸": "Overhead Tricep Extension",

    # Core
    "卷腹": "Crunch",
    "仰卧起坐": "Sit-up",
    "平板支撑": "Plank",
    "悬垂举腿": "Hanging Leg Raise",
    "俄罗斯转体": "Russian Twist",
}


class WorkoutLogFormatter:
    """Format raw Chinese workout logs to structured JSON/CSV"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize formatter with Gemini API

        Args:
            api_key: Gemini API key (if not provided, loads from GOOGLE_API_KEY env)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY in .env or pass api_key parameter."
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Model configuration
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.1'))
        self.max_output_tokens = int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', '8192'))

        self.model = genai.GenerativeModel(self.model_name)

        logger.info(f"Initialized WorkoutLogFormatter with model: {self.model_name}")

    def _build_prompt(self, raw_log: str, date: Optional[str] = None) -> str:
        """
        Build prompt for LLM to parse workout log

        Args:
            raw_log: Raw Chinese workout log text
            date: Optional date override (YYYY-MM-DD format)

        Returns:
            Formatted prompt string
        """
        exercise_list = "\n".join([f"  - {ch}: {en}" for ch, en in EXERCISE_MAPPING.items()])

        prompt = f"""You are a workout log parser. Convert the Chinese training log to structured JSON.

CRITICAL RULES:
1. Output ONLY valid JSON array, NO preamble, NO explanations
2. Bilateral exercises (先左后右, 左右交替, 单边): Count LEFT+RIGHT as ONE set
   - Example: "11 11, 11 12" with bilateral = 2 sets total (not 4)
3. Ignore ALL non-training content (emotions, diary entries, social notes)
4. Map Chinese exercise names to English using the mapping below
   - If exercise NOT in mapping: Keep Chinese name AND add "[UNMAPPED]" prefix
   - Example: "臀桥" not in mapping → "exercise": "[UNMAPPED] 臀桥"
5. Preserve individual set reps as arrays: [17, 15, 15]
6. Use null for missing RPE values
7. Extract rest times if present (optional field, can be null)
8. Notes field: ONLY form cues, equipment issues, relevant training notes

Exercise Name Mapping (Chinese → English):
{exercise_list}

Output Schema (JSON array):
[
  {{
    "date": "YYYY-MM-DD",
    "exercise": "Exercise Name (English)",
    "sets": 3,
    "reps": [17, 15, 15],
    "weight": 43,
    "unit": "kg",
    "rpe": 8.5,
    "rest_times": ["3:00", "3:15", "4:00"],
    "notes": "Brief relevant training notes only"
  }}
]

Date to use: {date or "extract from log or use today's date"}

Raw Training Log:
{raw_log}

Output ONLY the JSON array:"""

        return prompt

    def format_log(self,
                   raw_log: str,
                   date: Optional[str] = None,
                   validate: bool = True) -> Dict[str, Any]:
        """
        Format raw workout log to structured JSON

        Args:
            raw_log: Raw Chinese workout log text
            date: Optional date override (YYYY-MM-DD format)
            validate: Whether to validate output schema

        Returns:
            Dict with:
                - success: bool
                - data: List[Dict] if successful
                - raw_response: str (LLM output)
                - error: str if failed
        """
        logger.info("Starting workout log formatting...")

        try:
            # Build prompt
            prompt = self._build_prompt(raw_log, date)
            logger.debug(f"Prompt length: {len(prompt)} chars")

            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens
                }
            )

            raw_response = response.text
            logger.info(f"Received response: {len(raw_response)} chars")
            logger.debug(f"Raw response:\n{raw_response[:500]}...")

            # Parse JSON
            try:
                data = json.loads(raw_response)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {e}")
                return {
                    'success': False,
                    'error': f'Invalid JSON from LLM: {e}',
                    'raw_response': raw_response
                }

            # Validate if requested
            if validate:
                validation_result = self._validate_data(data)
                if not validation_result['valid']:
                    logger.error(f"Validation failed: {validation_result['errors']}")
                    return {
                        'success': False,
                        'error': 'Validation failed',
                        'validation_errors': validation_result['errors'],
                        'data': data,
                        'raw_response': raw_response
                    }

            logger.info(f"Successfully formatted {len(data)} exercises")
            return {
                'success': True,
                'data': data,
                'raw_response': raw_response
            }

        except Exception as e:
            logger.error(f"Formatting failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _validate_data(self, data: Any) -> Dict[str, Any]:
        """
        Validate parsed workout data

        Args:
            data: Parsed JSON data

        Returns:
            Dict with 'valid' (bool) and 'errors' (list)
        """
        errors = []

        # Must be a list
        if not isinstance(data, list):
            errors.append("Data must be a JSON array")
            return {'valid': False, 'errors': errors}

        # Validate each exercise entry
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                errors.append(f"Entry {i}: Must be an object")
                continue

            # Required fields
            required_fields = ['date', 'exercise', 'sets', 'reps', 'weight']
            for field in required_fields:
                if field not in entry:
                    errors.append(f"Entry {i}: Missing required field '{field}'")

            # Validate types
            if 'date' in entry:
                try:
                    datetime.strptime(entry['date'], '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Entry {i}: Invalid date format '{entry['date']}' (use YYYY-MM-DD)")

            if 'exercise' in entry and not isinstance(entry['exercise'], str):
                errors.append(f"Entry {i}: exercise must be string")

            if 'sets' in entry:
                if not isinstance(entry['sets'], int) or entry['sets'] <= 0:
                    errors.append(f"Entry {i}: sets must be positive integer")

            if 'reps' in entry:
                if not isinstance(entry['reps'], list):
                    errors.append(f"Entry {i}: reps must be array")
                elif 'sets' in entry and len(entry['reps']) != entry['sets']:
                    errors.append(f"Entry {i}: reps array length ({len(entry['reps'])}) must match sets count ({entry['sets']})")

            if 'weight' in entry:
                if not isinstance(entry['weight'], (int, float)) or entry['weight'] < 0:
                    errors.append(f"Entry {i}: weight must be non-negative number")

            if 'unit' in entry and entry['unit'] not in [None, 'kg', 'lbs', 'lb']:
                errors.append(f"Entry {i}: unit must be 'kg' or 'lbs' (got '{entry['unit']}')")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def format_to_csv_rows(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert formatted JSON to CSV-compatible row format

        Args:
            data: List of exercise dicts from format_log()

        Returns:
            List of dicts ready for CSV export (one row per set)
        """
        rows = []

        for exercise in data:
            # Expand each exercise into individual set rows
            for set_num in range(exercise['sets']):
                # Handle rest_times safely - may be shorter than sets count
                rest_time = None
                if exercise.get('rest_times') and isinstance(exercise['rest_times'], list):
                    if set_num < len(exercise['rest_times']):
                        rest_time = exercise['rest_times'][set_num]

                row = {
                    'date': exercise['date'],
                    'exercise': exercise['exercise'],
                    'set_number': set_num + 1,
                    'reps': exercise['reps'][set_num] if set_num < len(exercise['reps']) else exercise['reps'][-1],
                    'weight': exercise['weight'],
                    'unit': exercise.get('unit', 'kg'),
                    'rpe': exercise.get('rpe'),
                    'rest_time': rest_time,
                    'notes': exercise.get('notes')
                }
                rows.append(row)

        return rows

    def format_to_csv_aggregated(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert formatted JSON to aggregated CSV format (compatible with main branch)

        This format matches the schema expected by WorkoutDataLoader:
        date, exercise, sets, reps, weight, rpe, notes

        One row per exercise (not per set). If reps vary across sets, uses the average.

        Args:
            data: List of exercise dicts from format_log()

        Returns:
            List of dicts ready for CSV export (one row per exercise)
        """
        rows = []

        for exercise in data:
            # Calculate average reps if they vary
            reps_list = exercise['reps']
            avg_reps = sum(reps_list) / len(reps_list) if reps_list else 0

            # Use integer if all reps are the same, otherwise use average
            if len(set(reps_list)) == 1:
                reps_value = reps_list[0]
            else:
                reps_value = int(round(avg_reps))

            row = {
                'date': exercise['date'],
                'exercise': exercise['exercise'],
                'sets': exercise['sets'],
                'reps': reps_value,
                'weight': exercise['weight'],
                'rpe': exercise.get('rpe', ''),  # Empty string instead of None for CSV
                'notes': exercise.get('notes', '')
            }
            rows.append(row)

        return rows


# Convenience function
def format_workout_log(raw_log: str,
                       date: Optional[str] = None,
                       api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to format a workout log

    Args:
        raw_log: Raw Chinese workout log text
        date: Optional date override (YYYY-MM-DD format)
        api_key: Optional API key (defaults to GOOGLE_API_KEY env var)

    Returns:
        Result dict from WorkoutLogFormatter.format_log()
    """
    formatter = WorkoutLogFormatter(api_key=api_key)
    return formatter.format_log(raw_log, date=date)


if __name__ == "__main__":
    # Quick test
    test_log = """
    今天练腿！

    腿弯举 3组
    43公斤 x 17, 15, 15次
    组间休息3分钟

    硬拉 5组 x 5次
    100公斤
    RPE 8.5

    感觉很累但是很爽
    """

    result = format_workout_log(test_log, date="2024-01-15")

    if result['success']:
        print("✅ Formatting successful!")
        print(json.dumps(result['data'], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Formatting failed: {result['error']}")
