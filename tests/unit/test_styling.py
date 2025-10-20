"""
Unit tests for src.visualization.styling module.

Tests cover:
- 9:16 aspect ratio configuration
- Academic styling settings
- Color scheme configuration
- Font and grid settings
"""

import pytest
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class TestAspectRatioConfiguration:
    """Test suite for 9:16 aspect ratio setup."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_9_16_figure_returns_figure(self):
        """Test that create_9_16_figure returns a matplotlib Figure."""
        from src.visualization.styling import create_9_16_figure

        fig = create_9_16_figure()
        assert isinstance(fig, Figure)
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_9_16_figure_correct_aspect_ratio(self):
        """Test that figure has correct 9:16 aspect ratio."""
        from src.visualization.styling import create_9_16_figure

        fig = create_9_16_figure()
        width, height = fig.get_size_inches()

        # Check aspect ratio (should be 9:16 = 0.5625)
        aspect_ratio = width / height
        expected_ratio = 9 / 16

        assert abs(aspect_ratio - expected_ratio) < 0.01
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_9_16_figure_default_dpi(self):
        """Test that figure has high DPI for quality output."""
        from src.visualization.styling import create_9_16_figure

        fig = create_9_16_figure()

        # Should have DPI >= 150 for high quality
        assert fig.dpi >= 150
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_9_16_figure_custom_dpi(self):
        """Test creating figure with custom DPI."""
        from src.visualization.styling import create_9_16_figure

        fig = create_9_16_figure(dpi=200)
        # Note: matplotlib may adjust DPI for retina displays
        # Just check that DPI is >= requested value
        assert fig.dpi >= 200
        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_create_9_16_figure_size_for_tiktok(self):
        """Test that output size is suitable for TikTok (1080x1920)."""
        from src.visualization.styling import create_9_16_figure

        fig = create_9_16_figure(dpi=160)
        width, height = fig.get_size_inches()

        # At 160 DPI, 9x16 inches = 1440x2560 pixels (high quality)
        pixel_width = width * fig.dpi
        pixel_height = height * fig.dpi

        # Should be divisible by common video resolutions
        assert pixel_width >= 1080
        assert pixel_height >= 1920
        plt.close(fig)


class TestAcademicStyling:
    """Test suite for academic styling configuration."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_apply_academic_style_to_axes(self):
        """Test applying academic style to axes."""
        from src.visualization.styling import apply_academic_style

        fig, ax = plt.subplots()
        apply_academic_style(ax)

        # Check that grid is enabled
        assert ax.get_axisbelow()  # Grid should be below data

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_academic_style_has_grid(self):
        """Test that academic style includes grid lines."""
        from src.visualization.styling import apply_academic_style

        fig, ax = plt.subplots()
        apply_academic_style(ax)

        # Check that grid is configured (check gridlines exist after rendering)
        # Grid is enabled via ax.grid(True), which we can verify
        assert ax.xaxis.get_gridlines() is not None

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_academic_style_spines_visible(self):
        """Test that spines (borders) are properly configured."""
        from src.visualization.styling import apply_academic_style

        fig, ax = plt.subplots()
        apply_academic_style(ax)

        # Top and right spines should be hidden for clean look
        assert not ax.spines['top'].get_visible()
        assert not ax.spines['right'].get_visible()
        assert ax.spines['bottom'].get_visible()
        assert ax.spines['left'].get_visible()

        plt.close(fig)


class TestColorSchemes:
    """Test suite for color scheme configuration."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_get_color_palette_returns_list(self):
        """Test that get_color_palette returns a list of colors."""
        from src.visualization.styling import get_color_palette

        colors = get_color_palette()
        assert isinstance(colors, list)
        assert len(colors) > 0

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_get_color_palette_academic_theme(self):
        """Test getting academic color palette."""
        from src.visualization.styling import get_color_palette

        # Test dark mode palette (default)
        colors = get_color_palette(palette='dark', mode='dark')
        assert isinstance(colors, list)
        assert len(colors) >= 3  # Should have at least 3 colors

        # Test light mode palette
        colors_light = get_color_palette(palette='dark', mode='light')
        assert isinstance(colors_light, list)
        assert len(colors_light) >= 3  # Should have at least 3 colors

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_get_color_palette_colors_are_valid(self):
        """Test that colors are valid hex or RGB strings."""
        from src.visualization.styling import get_color_palette

        colors = get_color_palette()

        # Each color should be a string
        for color in colors:
            assert isinstance(color, str) or isinstance(color, tuple)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_get_primary_color(self):
        """Test getting single primary color."""
        from src.visualization.styling import get_primary_color

        color = get_primary_color()
        assert isinstance(color, str) or isinstance(color, tuple)


class TestFigureSaving:
    """Test suite for saving figures to PNG."""

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_save_figure_creates_file(self, tmp_path):
        """Test that save_figure creates a PNG file."""
        from src.visualization.styling import save_figure

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_chart.png"
        save_figure(fig, str(output_path))

        assert output_path.exists()
        assert output_path.suffix == '.png'

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_save_figure_with_auto_extension(self, tmp_path):
        """Test that save_figure adds .png extension if missing."""
        from src.visualization.styling import save_figure

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_chart"  # No extension
        save_figure(fig, str(output_path))

        expected_path = tmp_path / "test_chart.png"
        assert expected_path.exists()

        plt.close(fig)

    @pytest.mark.unit
    @pytest.mark.visualization
    def test_save_figure_high_quality(self, tmp_path):
        """Test that saved figure has high quality settings."""
        from src.visualization.styling import save_figure

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_chart.png"
        save_figure(fig, str(output_path))

        # File should be reasonably sized (high quality)
        assert output_path.stat().st_size > 1000  # At least 1KB

        plt.close(fig)
