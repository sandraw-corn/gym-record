"""
Visualization styling module for academic-quality 9:16 charts.

This module provides:
- 9:16 aspect ratio figure creation (TikTok/Xiaohongshu optimized)
- Dark theme styling optimized for night viewing on mobile
- Academic styling configuration
- Color palettes for dark backgrounds
- Figure saving utilities
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from pathlib import Path
from typing import List, Union, Tuple, Optional


# ============================================================================
# THEME CONFIGURATION
# ============================================================================

# Dark theme colors (optimized for OLED displays and night viewing)
DARK_BACKGROUND = '#1a1a1a'  # Near-black for OLED
DARK_AXES_BG = '#2b2b2b'     # Slightly lighter for axes area
DARK_GRID = '#404040'         # Visible grid on dark background
DARK_TEXT = '#e0e0e0'         # High-contrast light text
DARK_SPINE = '#606060'        # Subtle spines

# Light theme colors (for daytime viewing)
LIGHT_BACKGROUND = '#ffffff'
LIGHT_AXES_BG = '#ffffff'
LIGHT_GRID = '#d0d0d0'
LIGHT_TEXT = '#2b2b2b'
LIGHT_SPINE = '#2b2b2b'


# ============================================================================
# 9:16 ASPECT RATIO CONFIGURATION
# ============================================================================

def create_9_16_figure(dpi: int = 160, theme: str = 'dark') -> Figure:
    """
    Create a matplotlib figure with 9:16 aspect ratio for vertical display.

    Args:
        dpi: Dots per inch for figure resolution (default: 160)
             - 160 DPI: 1440x2560 pixels (high quality for social media)
             - 120 DPI: 1080x1920 pixels (standard TikTok size)
             - 180 DPI: 1620x2880 pixels (extra high quality)
        theme: Color theme ('dark' or 'light'). Default: 'dark' for night viewing

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Notes:
        - Optimized for TikTok, Instagram Reels, Xiaohongshu vertical format
        - Figure size is 9x16 inches at specified DPI
        - Recommended DPI range: 120-180 for balance of quality and file size
        - Dark theme is default for better night viewing on mobile devices
    """
    # Calculate figure size in inches (9:16 ratio)
    width = 9  # inches
    height = 16  # inches

    # Create figure with specified DPI
    fig = plt.figure(figsize=(width, height), dpi=dpi)

    # Set background color based on theme
    if theme == 'dark':
        fig.patch.set_facecolor(DARK_BACKGROUND)
    else:
        fig.patch.set_facecolor(LIGHT_BACKGROUND)

    return fig


# ============================================================================
# ACADEMIC STYLING
# ============================================================================

def apply_academic_style(ax: plt.Axes, theme: str = 'dark') -> None:
    """
    Apply academic styling to matplotlib axes for publication-quality plots.

    Args:
        ax: Matplotlib axes object to style
        theme: Color theme ('dark' or 'light'). Default: 'dark'

    Styling includes:
        - Clean grid lines (below data)
        - Minimal spines (remove top and right)
        - Professional fonts with larger sizes for mobile
        - High contrast for readability
        - Theme-aware colors for dark/light backgrounds
    """
    # Theme-specific colors
    if theme == 'dark':
        bg_color = DARK_AXES_BG
        grid_color = DARK_GRID
        text_color = DARK_TEXT
        spine_color = DARK_SPINE
        grid_alpha = 0.5  # Higher alpha for visibility on dark background
    else:
        bg_color = LIGHT_AXES_BG
        grid_color = LIGHT_GRID
        text_color = LIGHT_TEXT
        spine_color = LIGHT_SPINE
        grid_alpha = 0.3

    # Set axes background
    ax.set_facecolor(bg_color)

    # Enable grid with theme-appropriate styling
    ax.grid(True, alpha=grid_alpha, linestyle='--', linewidth=0.8, color=grid_color)
    ax.set_axisbelow(True)  # Grid below data points

    # Remove top and right spines for clean look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Make left and bottom spines bolder with theme color
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_color(spine_color)
    ax.spines['left'].set_color(spine_color)

    # Tick styling with larger sizes for mobile readability
    ax.tick_params(
        axis='both',
        which='major',
        labelsize=13,  # Increased from 10 for mobile
        length=8,       # Increased from 6
        width=1.5,      # Increased from 1.2
        colors=text_color
    )

    # Set text colors for labels
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)


def configure_academic_defaults(theme: str = 'dark') -> None:
    """
    Configure matplotlib defaults for academic-quality visualizations.

    Args:
        theme: Color theme ('dark' or 'light'). Default: 'dark'

    Sets global style parameters for consistent, professional appearance
    optimized for mobile viewing.
    """
    # Font settings - larger for mobile readability
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    mpl.rcParams['font.size'] = 13  # Increased from 11 for mobile

    # Theme-specific colors
    if theme == 'dark':
        mpl.rcParams['figure.facecolor'] = DARK_BACKGROUND
        mpl.rcParams['axes.facecolor'] = DARK_AXES_BG
        mpl.rcParams['text.color'] = DARK_TEXT
        mpl.rcParams['axes.labelcolor'] = DARK_TEXT
        mpl.rcParams['xtick.color'] = DARK_TEXT
        mpl.rcParams['ytick.color'] = DARK_TEXT
        mpl.rcParams['legend.edgecolor'] = DARK_SPINE
        mpl.rcParams['legend.facecolor'] = DARK_AXES_BG
        mpl.rcParams['legend.labelcolor'] = DARK_TEXT
    else:
        mpl.rcParams['figure.facecolor'] = LIGHT_BACKGROUND
        mpl.rcParams['axes.facecolor'] = LIGHT_AXES_BG
        mpl.rcParams['text.color'] = LIGHT_TEXT
        mpl.rcParams['axes.labelcolor'] = LIGHT_TEXT
        mpl.rcParams['xtick.color'] = LIGHT_TEXT
        mpl.rcParams['ytick.color'] = LIGHT_TEXT
        mpl.rcParams['legend.edgecolor'] = LIGHT_SPINE
        mpl.rcParams['legend.facecolor'] = LIGHT_AXES_BG

    # Line and marker settings - larger for mobile visibility
    mpl.rcParams['lines.linewidth'] = 3.0  # Increased from 2.0
    mpl.rcParams['lines.markersize'] = 12  # Increased from 8

    # Legend settings
    mpl.rcParams['legend.frameon'] = True
    mpl.rcParams['legend.framealpha'] = 0.95  # Slightly more opaque
    mpl.rcParams['legend.fancybox'] = False
    mpl.rcParams['legend.fontsize'] = 13  # Larger legend text


# ============================================================================
# COLOR SCHEMES
# ============================================================================

def get_color_palette(palette: str = 'dark', mode: str = 'dark') -> List[str]:
    """
    Get color palette for visualizations.

    Args:
        palette: Palette name ('dark', 'vibrant', 'neon', 'pastel')
        mode: Background mode ('dark' or 'light') - affects color brightness

    Returns:
        List of color codes (hex)

    Palettes for dark backgrounds (high-contrast, OLED-optimized):
        - dark: Professional bright colors for dark backgrounds
        - vibrant: High-saturation colors for social media impact
        - neon: Eye-catching neon colors for maximum attention
        - pastel: Soft pastel colors (better on light backgrounds)
    """
    # Dark mode palettes (bright, saturated colors)
    dark_palettes = {
        'dark': [
            '#4FC3F7',  # Bright cyan-blue (primary)
            '#FF4081',  # Bright pink
            '#FFD54F',  # Bright yellow
            '#81C784',  # Bright green
            '#BA68C8',  # Bright purple
        ],
        'vibrant': [
            '#FF6B6B',  # Coral red
            '#4ECDC4',  # Turquoise
            '#FFE66D',  # Yellow
            '#95E1D3',  # Mint
            '#F38181',  # Pink
        ],
        'neon': [
            '#00E5FF',  # Neon cyan
            '#FF1744',  # Neon red
            '#76FF03',  # Neon green
            '#FFEA00',  # Neon yellow
            '#E040FB',  # Neon purple
        ],
        'pastel': [
            '#90CAF9',  # Pastel blue
            '#F48FB1',  # Pastel pink
            '#FFF59D',  # Pastel yellow
            '#A5D6A7',  # Pastel green
            '#CE93D8',  # Pastel purple
        ]
    }

    # Light mode palettes (darker, muted colors)
    light_palettes = {
        'dark': [
            '#2E86AB',  # Professional blue
            '#A23B72',  # Purple
            '#F18F01',  # Orange
            '#C73E1D',  # Red
            '#6A994E',  # Green
        ],
        'vibrant': [
            '#E63946',  # Dark coral
            '#1D3557',  # Navy
            '#F4A261',  # Orange
            '#2A9D8F',  # Teal
            '#E76F51',  # Terracotta
        ],
        'neon': [
            '#0096C7',  # Dark cyan
            '#C1121F',  # Dark red
            '#588157',  # Dark green
            '#FFB703',  # Dark yellow
            '#8338EC',  # Dark purple
        ],
        'pastel': [
            '#1976D2',  # Dark blue
            '#C2185B',  # Dark pink
            '#FBC02D',  # Dark yellow
            '#388E3C',  # Dark green
            '#7B1FA2',  # Dark purple
        ]
    }

    # Select appropriate palette based on mode
    if mode == 'dark':
        palettes = dark_palettes
    else:
        palettes = light_palettes

    return palettes.get(palette, palettes['dark'])


def get_primary_color(theme: str = 'dark') -> str:
    """
    Get the primary color for single-series charts.

    Args:
        theme: Color theme ('dark' or 'light')

    Returns:
        Primary color code (hex)
    """
    if theme == 'dark':
        return '#4FC3F7'  # Bright cyan-blue for dark backgrounds
    else:
        return '#2E86AB'  # Professional blue for light backgrounds


# ============================================================================
# FIGURE SAVING
# ============================================================================

def save_figure(
    fig: Figure,
    output_path: Union[str, Path],
    dpi: Optional[int] = None,
    theme: str = 'dark',
    **kwargs
) -> None:
    """
    Save matplotlib figure to PNG with optimal settings.

    Args:
        fig: Matplotlib figure to save
        output_path: Output file path
        dpi: DPI for output (default: use figure's DPI)
        theme: Color theme ('dark' or 'light') for background color
        **kwargs: Additional arguments passed to fig.savefig()

    Notes:
        - Automatically adds .png extension if missing
        - Uses bbox_inches='tight' by default for optimal cropping
        - High quality settings for social media
        - Dark theme is default for better mobile viewing
    """
    # Convert to Path object
    output_path = Path(output_path)

    # Add .png extension if missing
    if output_path.suffix != '.png':
        output_path = output_path.with_suffix('.png')

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Default save parameters with theme-appropriate background
    bg_color = DARK_BACKGROUND if theme == 'dark' else LIGHT_BACKGROUND

    save_params = {
        'bbox_inches': 'tight',
        'facecolor': bg_color,
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


# Initialize academic defaults when module is imported (dark theme by default)
configure_academic_defaults(theme='dark')
