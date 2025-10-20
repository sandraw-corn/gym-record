"""
Unit tests for src.visualization.charts module.

Tests cover:
- Strength progression charts
- Volume tracking charts
- Multi-exercise comparison
- Chart components (title, labels, legend)
"""

import pytest
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class TestStrengthProgressionChart:
    """Test suite for strength progression chart generation."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_strength_chart_returns_figure(self, progressive_squat_data):
        """Test that create_strength_progression_chart returns a Figure."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')
        assert isinstance(fig, Figure)
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_strength_chart_has_title(self, progressive_squat_data):
        """Test that chart has appropriate title."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')
        ax = fig.axes[0]

        title = ax.get_title()
        assert 'Squat' in title
        assert 'Strength' in title or 'Progression' in title or '1RM' in title

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_strength_chart_has_labels(self, progressive_squat_data):
        """Test that chart has axis labels."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')
        ax = fig.axes[0]

        xlabel = ax.get_xlabel()
        ylabel = ax.get_ylabel()

        assert xlabel != ''  # Should have x-label
        assert ylabel != ''  # Should have y-label
        assert 'Date' in xlabel or 'Time' in xlabel
        assert '1RM' in ylabel or 'kg' in ylabel or 'Weight' in ylabel

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_strength_chart_has_data_points(self, progressive_squat_data):
        """Test that chart contains plotted data."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')
        ax = fig.axes[0]

        # Should have at least one line or scatter plot
        lines = ax.get_lines()
        collections = ax.collections

        assert len(lines) > 0 or len(collections) > 0

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_strength_chart_9_16_aspect(self, progressive_squat_data):
        """Test that chart uses 9:16 aspect ratio."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')
        width, height = fig.get_size_inches()

        aspect_ratio = width / height
        expected_ratio = 9 / 16

        assert abs(aspect_ratio - expected_ratio) < 0.1

        plt.close(fig)


class TestVolumeTrackingChart:
    """Test suite for volume tracking chart generation."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_volume_chart_returns_figure(self, progressive_squat_data):
        """Test that create_volume_chart returns a Figure."""
        from src.visualization.charts import create_volume_chart

        fig = create_volume_chart(progressive_squat_data, exercise='Squat')
        assert isinstance(fig, Figure)
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_volume_chart_has_title(self, progressive_squat_data):
        """Test that volume chart has appropriate title."""
        from src.visualization.charts import create_volume_chart

        fig = create_volume_chart(progressive_squat_data, exercise='Squat')
        ax = fig.axes[0]

        title = ax.get_title()
        assert 'Squat' in title
        assert 'Volume' in title

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_volume_chart_has_bars_or_lines(self, progressive_squat_data):
        """Test that volume chart has bars or lines."""
        from src.visualization.charts import create_volume_chart

        fig = create_volume_chart(progressive_squat_data, exercise='Squat')
        ax = fig.axes[0]

        # Should have bars, lines, or area plots
        has_bars = len(ax.patches) > 0
        has_lines = len(ax.get_lines()) > 0
        has_collections = len(ax.collections) > 0

        assert has_bars or has_lines or has_collections

        plt.close(fig)


class TestComparisonChart:
    """Test suite for multi-exercise comparison charts."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_comparison_chart_multiple_exercises(self, sample_workout_data):
        """Test creating comparison chart for multiple exercises."""
        from src.visualization.charts import create_comparison_chart

        exercises = ['Bench Press', 'Squat']
        fig = create_comparison_chart(sample_workout_data, exercises=exercises)

        assert isinstance(fig, Figure)
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_comparison_chart_has_legend(self, sample_workout_data):
        """Test that comparison chart has legend."""
        from src.visualization.charts import create_comparison_chart

        exercises = ['Bench Press', 'Squat']
        fig = create_comparison_chart(sample_workout_data, exercises=exercises)
        ax = fig.axes[0]

        legend = ax.get_legend()
        assert legend is not None

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_comparison_chart_different_colors(self, sample_workout_data):
        """Test that different exercises use different colors."""
        from src.visualization.charts import create_comparison_chart

        exercises = ['Bench Press', 'Squat', 'Deadlift']
        fig = create_comparison_chart(sample_workout_data, exercises=exercises)
        ax = fig.axes[0]

        lines = ax.get_lines()
        if len(lines) >= 2:
            # Check that lines have different colors
            colors = [line.get_color() for line in lines[:2]]
            assert colors[0] != colors[1]

        plt.close(fig)


class TestChartSaving:
    """Test suite for chart saving functionality."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_save_strength_chart_to_file(self, progressive_squat_data, tmp_path):
        """Test saving strength chart to PNG file."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')

        output_path = tmp_path / "squat_strength.png"
        fig.savefig(output_path, dpi=160, bbox_inches='tight')

        assert output_path.exists()
        assert output_path.stat().st_size > 10000  # Should be reasonably large

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_chart_output_correct_dimensions(self, progressive_squat_data, tmp_path):
        """Test that saved chart has correct pixel dimensions."""
        from src.visualization.charts import create_strength_progression_chart
        from PIL import Image

        fig = create_strength_progression_chart(progressive_squat_data, exercise='Squat')

        output_path = tmp_path / "squat_strength.png"
        fig.savefig(output_path, dpi=160, bbox_inches='tight')

        # Check image dimensions
        img = Image.open(output_path)
        width, height = img.size

        # Should be approximately 9:16 ratio (allowing for tight bbox adjustments)
        aspect_ratio = width / height
        expected_ratio = 9 / 16

        # More lenient check due to tight bbox
        assert abs(aspect_ratio - expected_ratio) < 0.3

        plt.close(fig)


class TestChartCustomization:
    """Test suite for chart customization options."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_strength_chart_custom_title(self, progressive_squat_data):
        """Test creating chart with custom title."""
        from src.visualization.charts import create_strength_progression_chart

        custom_title = "My Custom Squat Progress"
        fig = create_strength_progression_chart(
            progressive_squat_data,
            exercise='Squat',
            title=custom_title
        )
        ax = fig.axes[0]

        assert ax.get_title() == custom_title

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_chart_with_trend_line(self, progressive_squat_data):
        """Test creating chart with trend line overlay."""
        from src.visualization.charts import create_strength_progression_chart

        fig = create_strength_progression_chart(
            progressive_squat_data,
            exercise='Squat',
            show_trend=True
        )
        ax = fig.axes[0]

        # Should have at least 2 lines (data + trend)
        lines = ax.get_lines()
        assert len(lines) >= 2

        plt.close(fig)
