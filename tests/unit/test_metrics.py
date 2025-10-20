"""
Unit tests for src.analysis.metrics module.

Tests cover:
- 1RM calculations (Epley, Brzycki, Lombardi formulas)
- Volume calculations
- Progressive overload detection
- Trend analysis
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestOneRepMaxCalculations:
    """Test suite for 1RM calculation formulas."""

    @pytest.mark.unit
    def test_calculate_1rm_epley_formula(self):
        """Test Epley formula: 1RM = weight × (1 + reps/30)."""
        from src.analysis.metrics import calculate_1rm

        # Test case: 100kg × 10 reps
        result = calculate_1rm(weight=100, reps=10, formula='epley')
        expected = 100 * (1 + 10/30)  # 133.33
        assert abs(result - expected) < 0.01

    @pytest.mark.unit
    def test_calculate_1rm_brzycki_formula(self):
        """Test Brzycki formula: 1RM = weight × 36 / (37 - reps)."""
        from src.analysis.metrics import calculate_1rm

        # Test case: 100kg × 10 reps
        result = calculate_1rm(weight=100, reps=10, formula='brzycki')
        expected = 100 * 36 / (37 - 10)  # 133.33
        assert abs(result - expected) < 0.01

    @pytest.mark.unit
    def test_calculate_1rm_lombardi_formula(self):
        """Test Lombardi formula: 1RM = weight × reps^0.1."""
        from src.analysis.metrics import calculate_1rm

        # Test case: 100kg × 10 reps
        result = calculate_1rm(weight=100, reps=10, formula='lombardi')
        expected = 100 * (10 ** 0.1)  # 125.89
        assert abs(result - expected) < 0.01

    @pytest.mark.unit
    def test_calculate_1rm_default_formula_is_epley(self):
        """Test that default formula is Epley."""
        from src.analysis.metrics import calculate_1rm

        result_default = calculate_1rm(weight=100, reps=10)
        result_epley = calculate_1rm(weight=100, reps=10, formula='epley')
        assert result_default == result_epley

    @pytest.mark.unit
    def test_calculate_1rm_one_rep_returns_weight(self):
        """Test that 1 rep returns the weight itself."""
        from src.analysis.metrics import calculate_1rm

        result = calculate_1rm(weight=100, reps=1)
        assert result == 100

    @pytest.mark.unit
    def test_calculate_1rm_invalid_formula_raises_error(self):
        """Test that invalid formula raises ValueError."""
        from src.analysis.metrics import calculate_1rm

        with pytest.raises(ValueError, match="Invalid formula"):
            calculate_1rm(weight=100, reps=10, formula='invalid')

    @pytest.mark.unit
    def test_calculate_1rm_high_reps_warning(self):
        """Test that high reps (>12) may be inaccurate."""
        from src.analysis.metrics import calculate_1rm

        # Should still calculate but formulas are less accurate
        result = calculate_1rm(weight=100, reps=15, formula='epley')
        assert result > 100  # Should be higher than base weight

    @pytest.mark.unit
    def test_calculate_1rm_zero_reps_raises_error(self):
        """Test that zero reps raises ValueError."""
        from src.analysis.metrics import calculate_1rm

        with pytest.raises(ValueError, match="Reps must be greater than 0"):
            calculate_1rm(weight=100, reps=0)

    @pytest.mark.unit
    def test_calculate_1rm_negative_weight_raises_error(self):
        """Test that negative weight raises ValueError."""
        from src.analysis.metrics import calculate_1rm

        with pytest.raises(ValueError, match="Weight must be positive"):
            calculate_1rm(weight=-100, reps=10)


class TestVolumeCalculations:
    """Test suite for volume calculations."""

    @pytest.mark.unit
    def test_calculate_volume_single_set(self):
        """Test volume calculation for a single set."""
        from src.analysis.metrics import calculate_volume

        # 3 sets × 10 reps × 100kg = 3000kg
        result = calculate_volume(sets=3, reps=10, weight=100)
        assert result == 3000

    @pytest.mark.unit
    def test_calculate_volume_zero_values(self):
        """Test that zero values return zero volume."""
        from src.analysis.metrics import calculate_volume

        assert calculate_volume(sets=0, reps=10, weight=100) == 0
        assert calculate_volume(sets=3, reps=0, weight=100) == 0
        assert calculate_volume(sets=3, reps=10, weight=0) == 0

    @pytest.mark.unit
    def test_calculate_volume_from_dataframe(self):
        """Test calculating total volume from a DataFrame."""
        from src.analysis.metrics import calculate_total_volume

        data = pd.DataFrame({
            'sets': [3, 4, 3],
            'reps': [10, 8, 12],
            'weight': [100, 120, 90]
        })

        result = calculate_total_volume(data)
        expected = (3*10*100) + (4*8*120) + (3*12*90)  # 3000 + 3840 + 3240 = 10080
        assert result == expected

    @pytest.mark.unit
    def test_calculate_volume_by_exercise(self):
        """Test calculating volume grouped by exercise."""
        from src.analysis.metrics import calculate_volume_by_exercise

        data = pd.DataFrame({
            'exercise': ['Squat', 'Squat', 'Bench'],
            'sets': [3, 4, 3],
            'reps': [10, 8, 10],
            'weight': [100, 120, 80]
        })

        result = calculate_volume_by_exercise(data)

        assert 'Squat' in result
        assert 'Bench' in result
        assert result['Squat'] == (3*10*100) + (4*8*120)  # 6840
        assert result['Bench'] == (3*10*80)  # 2400

    @pytest.mark.unit
    def test_calculate_volume_over_time(self):
        """Test calculating volume over time series."""
        from src.analysis.metrics import calculate_volume_over_time

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-08']),
            'exercise': ['Squat', 'Squat', 'Squat'],
            'sets': [3, 4, 3],
            'reps': [10, 8, 10],
            'weight': [100, 120, 110]
        })

        result = calculate_volume_over_time(data, exercise='Squat')

        assert len(result) == 2  # Two dates
        assert '2024-01-01' in result.index.astype(str)
        assert '2024-01-08' in result.index.astype(str)


class TestProgressiveOverload:
    """Test suite for progressive overload detection."""

    @pytest.mark.unit
    def test_detect_progressive_overload_volume_increase(self):
        """Test detecting progressive overload via volume increase."""
        from src.analysis.metrics import detect_progressive_overload

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15']),
            'exercise': ['Squat'] * 3,
            'sets': [3, 4, 4],
            'reps': [10, 10, 10],
            'weight': [100, 100, 100]
        })

        result = detect_progressive_overload(data, exercise='Squat')
        assert result['has_overload'] is True
        assert result['type'] == 'volume'

    @pytest.mark.unit
    def test_detect_progressive_overload_intensity_increase(self):
        """Test detecting progressive overload via weight increase."""
        from src.analysis.metrics import detect_progressive_overload

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15']),
            'exercise': ['Squat'] * 3,
            'sets': [3, 3, 3],
            'reps': [10, 10, 10],
            'weight': [100, 105, 110]
        })

        result = detect_progressive_overload(data, exercise='Squat')
        assert result['has_overload'] is True
        assert result['type'] == 'intensity'

    @pytest.mark.unit
    def test_detect_progressive_overload_no_progression(self):
        """Test that no progression is detected when data is flat."""
        from src.analysis.metrics import detect_progressive_overload

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15']),
            'exercise': ['Squat'] * 3,
            'sets': [3, 3, 3],
            'reps': [10, 10, 10],
            'weight': [100, 100, 100]
        })

        result = detect_progressive_overload(data, exercise='Squat')
        assert result['has_overload'] is False


class TestTrendAnalysis:
    """Test suite for statistical trend analysis."""

    @pytest.mark.unit
    def test_calculate_linear_trend_increasing(self):
        """Test linear regression for increasing trend."""
        from src.analysis.metrics import calculate_linear_trend

        # Increasing data
        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15', '2024-01-22']),
            'value': [100, 110, 120, 130]
        })

        result = calculate_linear_trend(data)

        assert result['slope'] > 0  # Positive slope
        assert result['r_squared'] > 0.95  # High correlation

    @pytest.mark.unit
    def test_calculate_linear_trend_decreasing(self):
        """Test linear regression for decreasing trend."""
        from src.analysis.metrics import calculate_linear_trend

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15', '2024-01-22']),
            'value': [130, 120, 110, 100]
        })

        result = calculate_linear_trend(data)

        assert result['slope'] < 0  # Negative slope
        assert result['r_squared'] > 0.95  # High correlation

    @pytest.mark.unit
    def test_calculate_moving_average(self):
        """Test moving average calculation."""
        from src.analysis.metrics import calculate_moving_average

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15', '2024-01-22']),
            'value': [100, 110, 120, 130]
        })

        result = calculate_moving_average(data, window=2)

        assert len(result) == len(data)
        assert pd.isna(result.iloc[0])  # First value is NaN
        assert result.iloc[1] == 105  # (100 + 110) / 2

    @pytest.mark.unit
    def test_calculate_strength_progression(self):
        """Test calculating strength progression over time."""
        from src.analysis.metrics import calculate_strength_progression

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-08', '2024-01-15']),
            'exercise': ['Squat'] * 3,
            'sets': [3, 3, 3],
            'reps': [10, 10, 10],
            'weight': [100, 105, 110]
        })

        result = calculate_strength_progression(data, exercise='Squat')

        assert 'estimated_1rm' in result.columns
        assert len(result) == 3
        assert result['estimated_1rm'].is_monotonic_increasing  # Should increase


class TestEstimated1RMFromDataFrame:
    """Test suite for estimating 1RM from workout data."""

    @pytest.mark.unit
    def test_estimate_1rm_from_workout_data(self):
        """Test estimating 1RM from actual workout sets."""
        from src.analysis.metrics import estimate_1rm_from_workout

        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-01']),
            'exercise': ['Squat'] * 3,
            'sets': [1, 1, 1],
            'reps': [10, 8, 6],
            'weight': [100, 110, 120]
        })

        result = estimate_1rm_from_workout(data, exercise='Squat', date='2024-01-01')

        # Should return the highest estimated 1RM from all sets
        assert result > 120  # Should be higher than max weight used
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_estimate_1rm_from_best_set(self):
        """Test that 1RM estimation uses the best set (highest estimated 1RM)."""
        from src.analysis.metrics import estimate_1rm_from_workout

        # Heavy weight, low reps vs light weight, high reps
        data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-01']),
            'exercise': ['Bench'] * 2,
            'sets': [1, 1],
            'reps': [3, 12],
            'weight': [100, 70]
        })

        result = estimate_1rm_from_workout(data, exercise='Bench', date='2024-01-01')

        # Heavy set (100kg × 3) should give higher 1RM estimate than (70kg × 12)
        heavy_1rm = 100 * (1 + 3/30)  # ~110
        light_1rm = 70 * (1 + 12/30)  # ~98

        assert abs(result - heavy_1rm) < 1  # Should use heavy set
