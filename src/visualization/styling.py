"""
Visualization styling module for academic-quality 9:16 charts.

This module provides:
- 9:16 aspect ratio figure creation (TikTok/Xiaohongshu optimized)
- Academic styling configuration
- Color palettes
- Figure saving utilities
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from pathlib import Path
from typing import List, Union, Tuple, Optional


# ============================================================================
# 9:16 ASPECT RATIO CONFIGURATION
# ============================================================================

def create_9_16_figure(dpi: int = 160) -> Figure:
    """
    Create a matplotlib figure with 9:16 aspect ratio for vertical display.

    Args:
        dpi: Dots per inch for figure resolution (default: 160)
             - 160 DPI: 1440x2560 pixels (high quality for social media)
             - 120 DPI: 1080x1920 pixels (standard TikTok size)
             - 180 DPI: 1620x2880 pixels (extra high quality)

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Notes:
        - Optimized for TikTok, Instagram Reels, Xiaohongshu vertical format
        - Figure size is 9x16 inches at specified DPI
        - Recommended DPI range: 120-180 for balance of quality and file size
    """
    # Calculate figure size in inches (9:16 ratio)
    width = 9  # inches
    height = 16  # inches

    # Create figure with specified DPI
    fig = plt.figure(figsize=(width, height), dpi=dpi)

    return fig


# ============================================================================
# ACADEMIC STYLING
# ============================================================================

def apply_academic_style(ax: plt.Axes) -> None:
    """
    Apply academic styling to matplotlib axes for publication-quality plots.

    Args:
        ax: Matplotlib axes object to style

    Styling includes:
        - Clean grid lines (below data)
        - Minimal spines (remove top and right)
        - Professional fonts
        - High contrast for readability
    """
    # Enable grid with subtle styling
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)  # Grid below data points

    # Remove top and right spines for clean look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Make left and bottom spines slightly bolder
    ax.spines['bottom'].set_linewidth(1.2)
    ax.spines['left'].set_linewidth(1.2)

    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=10, length=6, width=1.2)


def configure_academic_defaults() -> None:
    """
    Configure matplotlib defaults for academic-quality visualizations.

    Sets global style parameters for consistent, professional appearance.
    """
    # Font settings
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    mpl.rcParams['font.size'] = 11

    # Figure settings
    mpl.rcParams['figure.facecolor'] = 'white'
    mpl.rcParams['axes.facecolor'] = 'white'

    # Line and marker settings
    mpl.rcParams['lines.linewidth'] = 2.0
    mpl.rcParams['lines.markersize'] = 8

    # Legend settings
    mpl.rcParams['legend.frameon'] = True
    mpl.rcParams['legend.framealpha'] = 0.9
    mpl.rcParams['legend.fancybox'] = False
    mpl.rcParams['legend.edgecolor'] = 'gray'


# ============================================================================
# COLOR SCHEMES
# ============================================================================

def get_color_palette(theme: str = 'academic') -> List[str]:
    """
    Get color palette for visualizations.

    Args:
        theme: Color theme name ('academic', 'vibrant', 'monochrome')

    Returns:
        List of color codes (hex or RGB tuples)

    Themes:
        - academic: Professional, muted colors suitable for publications
        - vibrant: High-contrast colors for social media
        - monochrome: Grayscale palette
    """
    palettes = {
        'academic': [
            '#2E86AB',  # Blue (primary)
            '#A23B72',  # Purple
            '#F18F01',  # Orange
            '#C73E1D',  # Red
            '#6A994E',  # Green
        ],
        'vibrant': [
            '#FF6B6B',  # Coral red
            '#4ECDC4',  # Turquoise
            '#FFE66D',  # Yellow
            '#95E1D3',  # Mint
            '#F38181',  # Pink
        ],
        'monochrome': [
            '#2D3142',  # Dark gray
            '#4F5D75',  # Medium gray
            '#BFC0C0',  # Light gray
            '#FFFFFF',  # White
            '#EF8354',  # Accent orange
        ]
    }

    return palettes.get(theme, palettes['academic'])


def get_primary_color() -> str:
    """
    Get the primary color for single-series charts.

    Returns:
        Primary color code (hex)
    """
    return '#2E86AB'  # Professional blue


# ============================================================================
# FIGURE SAVING
# ============================================================================

def save_figure(
    fig: Figure,
    output_path: Union[str, Path],
    dpi: Optional[int] = None,
    **kwargs
) -> None:
    """
    Save matplotlib figure to PNG with optimal settings.

    Args:
        fig: Matplotlib figure to save
        output_path: Output file path
        dpi: DPI for output (default: use figure's DPI)
        **kwargs: Additional arguments passed to fig.savefig()

    Notes:
        - Automatically adds .png extension if missing
        - Uses bbox_inches='tight' by default for optimal cropping
        - High quality settings for social media
    """
    # Convert to Path object
    output_path = Path(output_path)

    # Add .png extension if missing
    if output_path.suffix != '.png':
        output_path = output_path.with_suffix('.png')

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Default save parameters
    save_params = {
        'bbox_inches': 'tight',
        'facecolor': 'white',
        'edgecolor': 'none',
        'pad_inches': 0.1,
    }

    # Update with user-provided kwargs
    save_params.update(kwargs)

    # Use figure's DPI if not specified
    if dpi is not None:
        save_params['dpi'] = dpi
    elif 'dpi' not in save_params:
        save_params['dpi'] = fig.dpi

    # Save figure
    fig.savefig(output_path, **save_params)


# Initialize academic defaults when module is imported
configure_academic_defaults()
