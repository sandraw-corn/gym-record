"""
Analysis metrics module for gym workout data.

This module provides functions to:
- Calculate 1RM (one-rep max) using various formulas
- Calculate training volume
- Detect progressive overload
- Analyze trends and progression
"""

import pandas as pd
import numpy as np
from typing import Literal, Dict, Any, Optional
from scipy import stats


# ============================================================================
# 1RM CALCULATIONS
# ============================================================================

def calculate_1rm(
    weight: float,
    reps: int,
    formula: Literal['epley', 'brzycki', 'lombardi'] = 'epley'
) -> float:
    """
    Calculate estimated 1RM (one-rep max) using standard formulas.

    Args:
        weight: Weight used in the set (kg or lbs)
        reps: Number of repetitions performed
        formula: Formula to use ('epley', 'brzycki', or 'lombardi')

    Returns:
        Estimated 1RM

    Raises:
        ValueError: If weight is negative, reps is zero/negative, or formula is invalid

    Notes:
        - Epley: 1RM = weight × (1 + reps/30)
        - Brzycki: 1RM = weight × 36 / (37 - reps)
        - Lombardi: 1RM = weight × reps^0.1
        - Formulas are most accurate for reps ≤ 12
        - For 1 rep, returns the weight itself
    """
    # Validation
    if weight <= 0:
        raise ValueError("Weight must be positive")

    if reps <= 0:
        raise ValueError("Reps must be greater than 0")

    # Special case: 1 rep = actual 1RM
    if reps == 1:
        return float(weight)

    # Calculate based on formula
    if formula == 'epley':
        return weight * (1 + reps / 30)

    elif formula == 'brzycki':
        if reps >= 37:
            # Brzycki formula breaks down for very high reps
            raise ValueError("Brzycki formula not valid for reps >= 37")
        return weight * 36 / (37 - reps)

    elif formula == 'lombardi':
        return weight * (reps ** 0.1)

    else:
        raise ValueError(f"Invalid formula: '{formula}'. Must be 'epley', 'brzycki', or 'lombardi'")


# ============================================================================
# VOLUME CALCULATIONS
# ============================================================================

def calculate_volume(sets: int, reps: int, weight: float) -> float:
    """
    Calculate total volume for a single exercise.

    Args:
        sets: Number of sets
        reps: Number of reps per set
        weight: Weight used (kg or lbs)

    Returns:
        Total volume (sets × reps × weight)
    """
    return float(sets * reps * weight)


def calculate_total_volume(data: pd.DataFrame) -> float:
    """
    Calculate total volume from a DataFrame.

    Args:
        data: DataFrame with 'sets', 'reps', 'weight' columns

    Returns:
        Total volume across all rows
    """
    data = data.copy()
    data['volume'] = data['sets'] * data['reps'] * data['weight']
    return float(data['volume'].sum())


def calculate_volume_by_exercise(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate total volume grouped by exercise.

    Args:
        data: DataFrame with 'exercise', 'sets', 'reps', 'weight' columns

    Returns:
        Dictionary mapping exercise name to total volume
    """
    data = data.copy()
    data['volume'] = data['sets'] * data['reps'] * data['weight']

    volume_by_exercise = data.groupby('exercise')['volume'].sum()
    return volume_by_exercise.to_dict()


def calculate_volume_over_time(
    data: pd.DataFrame,
    exercise: Optional[str] = None
) -> pd.Series:
    """
    Calculate volume over time (grouped by date).

    Args:
        data: DataFrame with 'date', 'sets', 'reps', 'weight' columns
        exercise: Optional exercise name to filter by

    Returns:
        Series with date index and volume values
    """
    df = data.copy()

    # Filter by exercise if specified
    if exercise:
        df = df[df['exercise'].str.lower() == exercise.lower()]

    # Calculate volume
    df['volume'] = df['sets'] * df['reps'] * df['weight']

    # Group by date and sum
    volume_over_time = df.groupby('date')['volume'].sum()

    return volume_over_time


# ============================================================================
# PROGRESSIVE OVERLOAD DETECTION
# ============================================================================

def detect_progressive_overload(
    data: pd.DataFrame,
    exercise: str
) -> Dict[str, Any]:
    """
    Detect if progressive overload is occurring for an exercise.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to analyze

    Returns:
        Dictionary with:
            - has_overload: bool indicating if overload detected
            - type: 'volume', 'intensity', or None
            - details: additional information
    """
    # Filter for specific exercise
    df = data[data['exercise'].str.lower() == exercise.lower()].copy()

    if len(df) < 2:
        return {
            'has_overload': False,
            'type': None,
            'details': 'Insufficient data (need at least 2 workouts)'
        }

    # Sort by date
    df = df.sort_values('date')

    # Calculate volume for each workout date
    df['volume'] = df['sets'] * df['reps'] * df['weight']
    volume_by_date = df.groupby('date').agg({
        'volume': 'sum',
        'weight': 'max'
    })

    # Check for volume progression
    volume_slope = np.polyfit(range(len(volume_by_date)), volume_by_date['volume'], 1)[0]

    # Check for intensity (weight) progression
    weight_slope = np.polyfit(range(len(volume_by_date)), volume_by_date['weight'], 1)[0]

    # Determine if overload is present
    if weight_slope > 0.5:  # Threshold for meaningful weight increase
        return {
            'has_overload': True,
            'type': 'intensity',
            'details': f'Weight increasing by ~{weight_slope:.2f} per workout'
        }
    elif volume_slope > 50:  # Threshold for meaningful volume increase
        return {
            'has_overload': True,
            'type': 'volume',
            'details': f'Volume increasing by ~{volume_slope:.2f} per workout'
        }
    else:
        return {
            'has_overload': False,
            'type': None,
            'details': 'No significant progression detected'
        }


# ============================================================================
# TREND ANALYSIS
# ============================================================================

def calculate_linear_trend(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate linear trend (regression) for time series data.

    Args:
        data: DataFrame with 'date' and 'value' columns

    Returns:
        Dictionary with:
            - slope: Rate of change
            - intercept: Y-intercept
            - r_squared: Coefficient of determination (0-1)
    """
    # Convert dates to numeric (days since first date)
    df = data.copy()
    df['days'] = (df['date'] - df['date'].min()).dt.days

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df['days'], df['value']
    )

    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'std_err': std_err
    }


def calculate_moving_average(
    data: pd.DataFrame,
    window: int = 3
) -> pd.Series:
    """
    Calculate moving average for smoothing trend data.

    Args:
        data: DataFrame with 'date' and 'value' columns
        window: Window size for moving average

    Returns:
        Series with moving average values
    """
    return data['value'].rolling(window=window, min_periods=1).mean()


def calculate_strength_progression(
    data: pd.DataFrame,
    exercise: str,
    formula: str = 'epley'
) -> pd.DataFrame:
    """
    Calculate strength progression over time for an exercise.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to analyze
        formula: 1RM formula to use

    Returns:
        DataFrame with date, weight, reps, and estimated_1rm columns
    """
    # Filter for specific exercise
    df = data[data['exercise'].str.lower() == exercise.lower()].copy()

    # Calculate estimated 1RM for each set
    df['estimated_1rm'] = df.apply(
        lambda row: calculate_1rm(row['weight'], row['reps'], formula),
        axis=1
    )

    # Group by date and take max estimated 1RM
    result = df.groupby('date').agg({
        'weight': 'max',
        'reps': lambda x: x.iloc[0],  # Take first value
        'estimated_1rm': 'max'
    }).reset_index()

    return result


# ============================================================================
# WORKOUT-SPECIFIC FUNCTIONS
# ============================================================================

def estimate_1rm_from_workout(
    data: pd.DataFrame,
    exercise: str,
    date: str,
    formula: str = 'epley'
) -> float:
    """
    Estimate 1RM from the best set in a specific workout.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name
        date: Date of the workout (YYYY-MM-DD format)
        formula: 1RM formula to use

    Returns:
        Highest estimated 1RM from all sets
    """
    # Filter for specific exercise and date
    df = data[
        (data['exercise'].str.lower() == exercise.lower()) &
        (data['date'] == pd.to_datetime(date))
    ].copy()

    if len(df) == 0:
        raise ValueError(f"No data found for {exercise} on {date}")

    # Calculate 1RM for each set
    df['estimated_1rm'] = df.apply(
        lambda row: calculate_1rm(row['weight'], row['reps'], formula),
        axis=1
    )

    # Return the highest estimated 1RM (best set)
    return float(df['estimated_1rm'].max())
