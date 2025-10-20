"""
Integration tests for CLI commands.

Tests cover:
- End-to-end workflow: load data → analyze → visualize → save
- CLI command execution
- File generation and validation
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
import os


class TestCLIVisualizeCommand:
    """Test suite for CLI visualize command."""

    @pytest.mark.integration
    def test_visualize_command_creates_chart(self, tmp_path):
        """Test that visualize command creates output file."""
        from cli.gym_cli import cli

        runner = CliRunner()
        output_file = tmp_path / "squat_strength.png"

        result = runner.invoke(cli, [
            'visualize',
            '--exercise', 'Squat',
            '--metric', 'strength',
            '--output', str(output_file),
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0
        assert output_file.exists()

    @pytest.mark.integration
    def test_visualize_command_with_period(self, tmp_path):
        """Test visualize command with time period filter."""
        from cli.gym_cli import cli

        runner = CliRunner()
        output_file = tmp_path / "squat_recent.png"

        result = runner.invoke(cli, [
            'visualize',
            '--exercise', 'Squat',
            '--metric', 'strength',
            '--output', str(output_file),
            '--period', '2weeks',
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0

    @pytest.mark.integration
    def test_visualize_volume_metric(self, tmp_path):
        """Test visualize command with volume metric."""
        from cli.gym_cli import cli

        runner = CliRunner()
        output_file = tmp_path / "squat_volume.png"

        result = runner.invoke(cli, [
            'visualize',
            '--exercise', 'Squat',
            '--metric', 'volume',
            '--output', str(output_file),
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0
        assert output_file.exists()

    @pytest.mark.integration
    def test_visualize_nonexistent_exercise(self):
        """Test that nonexistent exercise gives helpful error."""
        from cli.gym_cli import cli

        runner = CliRunner()

        result = runner.invoke(cli, [
            'visualize',
            '--exercise', 'NonexistentExercise',
            '--metric', 'strength',
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code != 0
        assert 'No data found' in result.output or 'error' in result.output.lower()


class TestCLIAnalyzeCommand:
    """Test suite for CLI analyze command."""

    @pytest.mark.integration
    def test_analyze_command_strength_focus(self):
        """Test analyze command with strength focus."""
        from cli.gym_cli import cli

        runner = CliRunner()

        result = runner.invoke(cli, [
            'analyze',
            '--focus', 'strength',
            '--period', '4weeks',
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0
        assert 'strength' in result.output.lower() or '1rm' in result.output.lower()

    @pytest.mark.integration
    def test_analyze_command_volume_focus(self):
        """Test analyze command with volume focus."""
        from cli.gym_cli import cli

        runner = CliRunner()

        result = runner.invoke(cli, [
            'analyze',
            '--focus', 'volume',
            '--period', '4weeks',
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0
        assert 'volume' in result.output.lower()

    @pytest.mark.integration
    def test_analyze_command_hypertrophy_focus(self):
        """Test analyze command with hypertrophy focus."""
        from cli.gym_cli import cli

        runner = CliRunner()

        result = runner.invoke(cli, [
            'analyze',
            '--focus', 'hypertrophy',
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0


class TestCLICompareCommand:
    """Test suite for CLI compare command."""

    @pytest.mark.integration
    def test_compare_multiple_exercises(self, tmp_path):
        """Test compare command with multiple exercises."""
        from cli.gym_cli import cli

        runner = CliRunner()
        output_file = tmp_path / "comparison.png"

        result = runner.invoke(cli, [
            'compare',
            '--exercises', 'Bench Press,Squat,Deadlift',
            '--metric', 'strength',
            '--output', str(output_file),
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0
        assert output_file.exists()

    @pytest.mark.integration
    def test_compare_volume_metric(self, tmp_path):
        """Test compare command with volume metric."""
        from cli.gym_cli import cli

        runner = CliRunner()
        output_file = tmp_path / "volume_comparison.png"

        result = runner.invoke(cli, [
            'compare',
            '--exercises', 'Bench Press,Squat',
            '--metric', 'volume',
            '--output', str(output_file),
            '--data', 'data/sample_workout.csv'
        ])

        assert result.exit_code == 0
        assert output_file.exists()


class TestCLIListDataCommand:
    """Test suite for CLI list-data command."""

    @pytest.mark.integration
    def test_list_data_shows_files(self):
        """Test that list-data shows available data files."""
        from cli.gym_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['list-data'])

        assert result.exit_code == 0
        assert 'sample_workout.csv' in result.output

    @pytest.mark.integration
    def test_list_data_shows_file_count(self):
        """Test that list-data shows file count."""
        from cli.gym_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['list-data'])

        assert result.exit_code == 0
        assert 'Total:' in result.output or 'file' in result.output.lower()


class TestEndToEndWorkflow:
    """Test suite for complete end-to-end workflows."""

    @pytest.mark.integration
    def test_complete_strength_analysis_workflow(self, tmp_path):
        """Test complete workflow: load → analyze → visualize."""
        from cli.gym_cli import cli

        runner = CliRunner()

        # Step 1: Analyze strength
        result_analyze = runner.invoke(cli, [
            'analyze',
            '--focus', 'strength',
            '--data', 'data/sample_workout.csv'
        ])
        assert result_analyze.exit_code == 0

        # Step 2: Visualize strength progression
        output_file = tmp_path / "strength.png"
        result_viz = runner.invoke(cli, [
            'visualize',
            '--exercise', 'Squat',
            '--metric', 'strength',
            '--output', str(output_file),
            '--data', 'data/sample_workout.csv'
        ])
        assert result_viz.exit_code == 0
        assert output_file.exists()

        # Verify output is valid PNG
        assert output_file.stat().st_size > 10000  # Should be reasonably large

    @pytest.mark.integration
    def test_volume_tracking_workflow(self, tmp_path):
        """Test volume tracking workflow."""
        from cli.gym_cli import cli

        runner = CliRunner()

        # Analyze volume
        result_analyze = runner.invoke(cli, [
            'analyze',
            '--focus', 'volume',
            '--data', 'data/sample_workout.csv'
        ])
        assert result_analyze.exit_code == 0

        # Visualize volume
        output_file = tmp_path / "volume.png"
        result_viz = runner.invoke(cli, [
            'visualize',
            '--exercise', 'Bench Press',
            '--metric', 'volume',
            '--output', str(output_file),
            '--data', 'data/sample_workout.csv'
        ])
        assert result_viz.exit_code == 0
        assert output_file.exists()
