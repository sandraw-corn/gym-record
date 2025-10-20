"""
Pytest configuration and shared fixtures for gym-record tests.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_workout_data():
    """
    Fixture providing sample workout data as a DataFrame.

    Returns:
        pd.DataFrame: Sample workout records
    """
    data = {
        'date': [
            '2024-01-15', '2024-01-15', '2024-01-15',
            '2024-01-17', '2024-01-17', '2024-01-17',
            '2024-01-19', '2024-01-19',
        ],
        'exercise': [
            'Bench Press', 'Squat', 'Deadlift',
            'Bench Press', 'Squat', 'Overhead Press',
            'Bench Press', 'Squat',
        ],
        'sets': [3, 4, 3, 4, 4, 3, 3, 4],
        'reps': [8, 6, 5, 8, 6, 10, 8, 5],
        'weight': [185, 275, 315, 185, 280, 95, 190, 285],
        'rpe': [8.5, 9.0, 8.0, 8.0, 9.0, 7.5, 8.5, 9.5],
        'notes': [
            'Felt strong', 'Depth was good', '',
            '', 'Added 5lbs', '',
            'PR attempt', 'Heavy day'
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_content():
    """
    Fixture providing sample CSV content as a string.

    Returns:
        str: CSV formatted workout data
    """
    return """date,exercise,sets,reps,weight,rpe,notes
2024-01-15,Bench Press,3,8,185,8.5,Felt strong
2024-01-15,Squat,4,6,275,9.0,Depth was good
2024-01-15,Deadlift,3,5,315,8.0,
2024-01-17,Bench Press,4,8,185,8.0,
2024-01-17,Squat,4,6,280,9.0,Added 5lbs
2024-01-17,Overhead Press,3,10,95,7.5,
2024-01-19,Bench Press,3,8,190,8.5,PR attempt
2024-01-19,Squat,4,5,285,9.5,Heavy day
"""


@pytest.fixture
def temp_data_dir(sample_csv_content):
    """
    Fixture providing a temporary directory with sample CSV data.

    Args:
        sample_csv_content: CSV content fixture

    Yields:
        Path: Path to temporary data directory

    Cleanup:
        Removes the temporary directory after test
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Write sample CSV file
    csv_file = temp_path / 'sample_workout.csv'
    csv_file.write_text(sample_csv_content)

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def invalid_csv_content():
    """
    Fixture providing invalid CSV content (missing required columns).

    Returns:
        str: Invalid CSV data
    """
    return """date,exercise,weight
2024-01-15,Bench Press,185
2024-01-17,Squat,275
"""


@pytest.fixture
def malformed_csv_content():
    """
    Fixture providing malformed CSV content (inconsistent columns).

    Returns:
        str: Malformed CSV data
    """
    return """date,exercise,sets,reps,weight
2024-01-15,Bench Press,3,8,185
2024-01-17,Squat,4,6
2024-01-19,Deadlift,3,5,315,extra,columns
"""


@pytest.fixture
def empty_csv_content():
    """
    Fixture providing empty CSV (headers only).

    Returns:
        str: Empty CSV with headers
    """
    return """date,exercise,sets,reps,weight,rpe,notes
"""


@pytest.fixture
def bench_press_data():
    """
    Fixture providing only Bench Press workout data.

    Returns:
        pd.DataFrame: Bench Press records only
    """
    data = {
        'date': ['2024-01-15', '2024-01-17', '2024-01-19', '2024-01-22'],
        'exercise': ['Bench Press'] * 4,
        'sets': [3, 4, 3, 4],
        'reps': [8, 8, 8, 8],
        'weight': [185, 185, 190, 187.5],
        'rpe': [8.5, 8.0, 8.5, 8.0],
        'notes': ['Felt strong', '', 'PR attempt', '']
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df
