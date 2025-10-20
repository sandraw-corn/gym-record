"""
Data loading and processing module for gym workout records.

This module provides functions to:
- Load workout data from CSV files
- Validate data integrity
- Filter and query workout records
- Handle missing values and data cleaning
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class WorkoutDataLoader:
    """Load and process gym workout data from CSV files."""

    REQUIRED_COLUMNS = ['date', 'exercise', 'sets', 'reps', 'weight']
    OPTIONAL_COLUMNS = ['rpe', 'notes']

    def __init__(self, data_path: str = 'data'):
        """
        Initialize the data loader.

        Args:
            data_path: Path to the directory containing workout data files
        """
        self.data_path = Path(data_path)
        self.data: Optional[pd.DataFrame] = None

    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        Load workout data from a CSV file.

        Args:
            filename: Name of the CSV file (e.g., 'sample_workout.csv')

        Returns:
            DataFrame containing workout records

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If required columns are missing
        """
        file_path = self.data_path / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        # Load CSV
        df = pd.read_csv(file_path)

        # Validate columns
        self._validate_columns(df)

        # Parse dates
        df['date'] = pd.to_datetime(df['date'])

        # Clean data
        df = self._clean_data(df)

        self.data = df
        return df

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """
        Validate that required columns are present.

        Args:
            df: DataFrame to validate

        Raises:
            ValueError: If required columns are missing
        """
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and process the data.

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid SettingWithCopyWarning
        df = df.copy()

        # Remove rows with missing critical values
        df = df.dropna(subset=['date', 'exercise', 'weight'])

        # Ensure proper data types
        df['sets'] = df['sets'].fillna(0).astype(int)
        df['reps'] = df['reps'].fillna(0).astype(int)
        df['weight'] = df['weight'].astype(float)  # Ensure float64

        # Fill missing RPE with None
        if 'rpe' in df.columns:
            df['rpe'] = df['rpe'].fillna(0)

        # Fill missing notes with empty string
        if 'notes' in df.columns:
            df['notes'] = df['notes'].fillna('')

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        return df

    def filter_by_exercise(self, exercise: str) -> pd.DataFrame:
        """
        Filter data for a specific exercise.

        Args:
            exercise: Exercise name (case-insensitive)

        Returns:
            Filtered DataFrame

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        # Case-insensitive match
        mask = self.data['exercise'].str.lower() == exercise.lower()
        return self.data[mask].copy()

    def filter_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter data by date range.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Filtered DataFrame

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        df = self.data.copy()

        if start_date:
            start = pd.to_datetime(start_date)
            df = df[df['date'] >= start]

        if end_date:
            end = pd.to_datetime(end_date)
            df = df[df['date'] <= end]

        return df

    def filter_by_rep_range(
        self,
        min_reps: Optional[int] = None,
        max_reps: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Filter data by rep range.

        Args:
            min_reps: Minimum reps (inclusive)
            max_reps: Maximum reps (inclusive)

        Returns:
            Filtered DataFrame

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        df = self.data.copy()

        if min_reps is not None:
            df = df[df['reps'] >= min_reps]

        if max_reps is not None:
            df = df[df['reps'] <= max_reps]

        return df

    def get_unique_exercises(self) -> List[str]:
        """
        Get list of unique exercises in the dataset.

        Returns:
            Sorted list of exercise names

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        return sorted(self.data['exercise'].unique().tolist())

    def get_date_range(self) -> tuple[datetime, datetime]:
        """
        Get the date range of the loaded data.

        Returns:
            Tuple of (earliest_date, latest_date)

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        return (
            self.data['date'].min().to_pydatetime(),
            self.data['date'].max().to_pydatetime()
        )

    def get_summary(self) -> dict:
        """
        Get summary statistics of the loaded data.

        Returns:
            Dictionary with summary information

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        start_date, end_date = self.get_date_range()

        return {
            'total_records': len(self.data),
            'unique_exercises': len(self.get_unique_exercises()),
            'exercises': self.get_unique_exercises(),
            'date_range': (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
            'total_days': (end_date - start_date).days + 1,
        }


def load_workout_data(filename: str = 'sample_workout.csv', data_path: str = 'data') -> pd.DataFrame:
    """
    Convenience function to quickly load workout data.

    Args:
        filename: CSV file name
        data_path: Path to data directory

    Returns:
        DataFrame with workout data
    """
    loader = WorkoutDataLoader(data_path)
    return loader.load_csv(filename)
