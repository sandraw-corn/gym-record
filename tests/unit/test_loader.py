"""
Unit tests for src.data.loader module.

Tests cover:
- CSV loading and validation
- Data cleaning and processing
- Filtering functions
- Error handling
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime


# Import will fail until we implement the module (TDD approach)
# from src.data.loader import WorkoutDataLoader, load_workout_data


class TestWorkoutDataLoader:
    """Test suite for WorkoutDataLoader class."""

    @pytest.mark.unit
    def test_init_with_default_path(self):
        """Test initialization with default data path."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader()
        assert loader.data_path == Path('data')
        assert loader.data is None

    @pytest.mark.unit
    def test_init_with_custom_path(self):
        """Test initialization with custom data path."""
        from src.data.loader import WorkoutDataLoader

        custom_path = '/custom/path'
        loader = WorkoutDataLoader(custom_path)
        assert loader.data_path == Path(custom_path)
        assert loader.data is None

    @pytest.mark.unit
    @pytest.mark.data
    def test_load_csv_success(self, temp_data_dir):
        """Test successful CSV loading."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        df = loader.load_csv('sample_workout.csv')

        # Verify data is loaded
        assert df is not None
        assert len(df) == 8
        assert loader.data is not None

        # Verify columns
        expected_columns = ['date', 'exercise', 'sets', 'reps', 'weight', 'rpe', 'notes']
        assert list(df.columns) == expected_columns

        # Verify date parsing
        assert df['date'].dtype == 'datetime64[ns]'

        # Verify data types
        assert df['sets'].dtype == 'int64'
        assert df['reps'].dtype == 'int64'
        assert df['weight'].dtype == 'float64'

    @pytest.mark.unit
    def test_load_csv_file_not_found(self):
        """Test loading non-existent file raises FileNotFoundError."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_csv('nonexistent.csv')

    @pytest.mark.unit
    @pytest.mark.data
    def test_load_csv_missing_required_columns(self, temp_data_dir, invalid_csv_content):
        """Test loading CSV with missing required columns raises ValueError."""
        from src.data.loader import WorkoutDataLoader

        # Write invalid CSV
        invalid_file = temp_data_dir / 'invalid.csv'
        invalid_file.write_text(invalid_csv_content)

        loader = WorkoutDataLoader(str(temp_data_dir))
        with pytest.raises(ValueError, match="Missing required columns"):
            loader.load_csv('invalid.csv')

    @pytest.mark.unit
    @pytest.mark.data
    def test_data_cleaning_removes_critical_nulls(self, temp_data_dir):
        """Test that rows with null critical values are removed."""
        from src.data.loader import WorkoutDataLoader

        # CSV with missing critical data
        csv_content = """date,exercise,sets,reps,weight,rpe,notes
2024-01-15,Bench Press,3,8,185,8.5,Good
2024-01-17,,4,6,275,9.0,Missing exercise
2024-01-19,Squat,4,5,,8.0,Missing weight
"""
        csv_file = temp_data_dir / 'test.csv'
        csv_file.write_text(csv_content)

        loader = WorkoutDataLoader(str(temp_data_dir))
        df = loader.load_csv('test.csv')

        # Should only have 1 valid row
        assert len(df) == 1
        assert df.iloc[0]['exercise'] == 'Bench Press'

    @pytest.mark.unit
    @pytest.mark.data
    def test_data_sorted_by_date(self, temp_data_dir):
        """Test that loaded data is sorted by date."""
        from src.data.loader import WorkoutDataLoader

        # CSV with unsorted dates
        csv_content = """date,exercise,sets,reps,weight,rpe,notes
2024-01-19,Bench Press,3,8,190,8.5,
2024-01-15,Squat,4,6,275,9.0,
2024-01-17,Deadlift,3,5,315,8.0,
"""
        csv_file = temp_data_dir / 'test.csv'
        csv_file.write_text(csv_content)

        loader = WorkoutDataLoader(str(temp_data_dir))
        df = loader.load_csv('test.csv')

        # Check dates are sorted
        dates = df['date'].tolist()
        assert dates == sorted(dates)

    @pytest.mark.unit
    def test_filter_by_exercise(self, temp_data_dir, sample_csv_content):
        """Test filtering data by exercise name."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        # Filter for Bench Press
        bench_data = loader.filter_by_exercise('Bench Press')
        assert len(bench_data) == 3
        assert all(bench_data['exercise'] == 'Bench Press')

    @pytest.mark.unit
    def test_filter_by_exercise_case_insensitive(self, temp_data_dir, sample_csv_content):
        """Test that exercise filtering is case-insensitive."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        # Try different cases
        upper = loader.filter_by_exercise('BENCH PRESS')
        lower = loader.filter_by_exercise('bench press')
        mixed = loader.filter_by_exercise('Bench Press')

        assert len(upper) == len(lower) == len(mixed) == 3

    @pytest.mark.unit
    def test_filter_by_exercise_no_data_loaded(self):
        """Test filtering without loading data raises ValueError."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader()
        with pytest.raises(ValueError, match="No data loaded"):
            loader.filter_by_exercise('Bench Press')

    @pytest.mark.unit
    def test_filter_by_date_range_start_only(self, temp_data_dir, sample_csv_content):
        """Test filtering with only start date."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        filtered = loader.filter_by_date_range(start_date='2024-01-17')
        assert len(filtered) > 0
        assert all(filtered['date'] >= pd.to_datetime('2024-01-17'))

    @pytest.mark.unit
    def test_filter_by_date_range_end_only(self, temp_data_dir, sample_csv_content):
        """Test filtering with only end date."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        filtered = loader.filter_by_date_range(end_date='2024-01-17')
        assert len(filtered) > 0
        assert all(filtered['date'] <= pd.to_datetime('2024-01-17'))

    @pytest.mark.unit
    def test_filter_by_date_range_both(self, temp_data_dir, sample_csv_content):
        """Test filtering with both start and end dates."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        filtered = loader.filter_by_date_range(
            start_date='2024-01-16',
            end_date='2024-01-18'
        )
        assert len(filtered) > 0
        assert all(filtered['date'] >= pd.to_datetime('2024-01-16'))
        assert all(filtered['date'] <= pd.to_datetime('2024-01-18'))

    @pytest.mark.unit
    def test_filter_by_rep_range_min_only(self, temp_data_dir, sample_csv_content):
        """Test filtering with minimum reps only."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        filtered = loader.filter_by_rep_range(min_reps=8)
        assert len(filtered) > 0
        assert all(filtered['reps'] >= 8)

    @pytest.mark.unit
    def test_filter_by_rep_range_max_only(self, temp_data_dir, sample_csv_content):
        """Test filtering with maximum reps only."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        filtered = loader.filter_by_rep_range(max_reps=6)
        assert len(filtered) > 0
        assert all(filtered['reps'] <= 6)

    @pytest.mark.unit
    def test_filter_by_rep_range_both(self, temp_data_dir, sample_csv_content):
        """Test filtering with both min and max reps."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        filtered = loader.filter_by_rep_range(min_reps=5, max_reps=8)
        assert len(filtered) > 0
        assert all(filtered['reps'] >= 5)
        assert all(filtered['reps'] <= 8)

    @pytest.mark.unit
    def test_get_unique_exercises(self, temp_data_dir, sample_csv_content):
        """Test getting list of unique exercises."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        exercises = loader.get_unique_exercises()
        assert isinstance(exercises, list)
        assert len(exercises) == 4  # Bench, Squat, Deadlift, OHP
        assert 'Bench Press' in exercises
        assert 'Squat' in exercises
        assert exercises == sorted(exercises)  # Should be sorted

    @pytest.mark.unit
    def test_get_date_range(self, temp_data_dir, sample_csv_content):
        """Test getting date range of loaded data."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        start, end = loader.get_date_range()
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start <= end
        assert start.strftime('%Y-%m-%d') == '2024-01-15'
        assert end.strftime('%Y-%m-%d') == '2024-01-19'

    @pytest.mark.unit
    def test_get_summary(self, temp_data_dir, sample_csv_content):
        """Test getting data summary."""
        from src.data.loader import WorkoutDataLoader

        loader = WorkoutDataLoader(str(temp_data_dir))
        loader.load_csv('sample_workout.csv')

        summary = loader.get_summary()

        assert 'total_records' in summary
        assert 'unique_exercises' in summary
        assert 'exercises' in summary
        assert 'date_range' in summary
        assert 'total_days' in summary

        assert summary['total_records'] == 8
        assert summary['unique_exercises'] == 4
        assert isinstance(summary['exercises'], list)
        assert isinstance(summary['date_range'], tuple)


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    @pytest.mark.unit
    @pytest.mark.data
    def test_load_workout_data(self, temp_data_dir):
        """Test the convenience function load_workout_data."""
        from src.data.loader import load_workout_data

        df = load_workout_data('sample_workout.csv', str(temp_data_dir))

        assert df is not None
        assert len(df) > 0
        assert 'date' in df.columns
        assert 'exercise' in df.columns
