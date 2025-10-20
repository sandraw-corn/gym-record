"""
Chart generation module for gym workout visualizations.

This module provides:
- Strength progression charts (1RM over time)
- Volume tracking charts
- Multi-exercise comparison charts
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from typing import List, Optional
import numpy as np
from scipy import stats

from src.visualization.styling import (
    create_9_16_figure,
    apply_academic_style,
    get_color_palette,
    get_primary_color
)
from src.analysis.metrics import calculate_1rm, calculate_volume_over_time


# ============================================================================
# STRENGTH PROGRESSION CHARTS
# ============================================================================

def create_strength_progression_chart(
    data: pd.DataFrame,
    exercise: str,
    title: Optional[str] = None,
    show_trend: bool = True,
    show_statistics: bool = True,
    show_records: bool = True,
    theme: str = 'dark',
    formula: str = 'epley'
) -> Figure:
    """
    Create strength progression chart showing estimated 1RM over time.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to visualize
        title: Custom title (optional, auto-generated if None)
        show_trend: Whether to show trend line
        show_statistics: Whether to show statistical annotations (avg, % change)
        show_records: Whether to mark personal records
        theme: Color theme ('dark' or 'light'). Default: 'dark'
        formula: 1RM formula to use ('epley', 'brzycki', 'lombardi')

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Estimated 1RM over time
        - Data points with larger markers for mobile
        - Optional trend line
        - Statistical annotations (avg, % improvement)
        - PR markers
        - Date formatting on x-axis
        - Dark theme optimized for night viewing
    """
    # Filter data for specific exercise
    df = data[data['exercise'].str.lower() == exercise.lower()].copy()

    if len(df) == 0:
        raise ValueError(f"No data found for exercise: {exercise}")

    # Calculate estimated 1RM for each set
    df['estimated_1rm'] = df.apply(
        lambda row: calculate_1rm(row['weight'], row['reps'], formula),
        axis=1
    )

    # Group by date and take maximum 1RM
    df_grouped = df.groupby('date').agg({
        'estimated_1rm': 'max',
        'weight': 'max'
    }).reset_index()

    # Create 9:16 figure with theme
    fig = create_9_16_figure(theme=theme)
    ax = fig.add_subplot(111)

    # Get theme colors
    primary_color = get_primary_color(theme=theme)
    text_color = '#e0e0e0' if theme == 'dark' else '#2b2b2b'

    # Plot data points
    ax.plot(
        df_grouped['date'],
        df_grouped['estimated_1rm'],
        marker='o',
        markersize=14,  # Larger for mobile
        linewidth=3.5,  # Thicker for visibility
        color=primary_color,
        label='Estimated 1RM',
        zorder=3,
        markeredgecolor=text_color,
        markeredgewidth=1.5
    )

    # Mark personal records if requested
    if show_records:
        # Find records (each new maximum)
        df_grouped['is_record'] = df_grouped['estimated_1rm'].cummax() == df_grouped['estimated_1rm']
        df_grouped['is_new_record'] = (
            df_grouped['is_record'] &
            (df_grouped['estimated_1rm'] > df_grouped['estimated_1rm'].shift(1).fillna(0))
        )

        records = df_grouped[df_grouped['is_new_record']]

        if len(records) > 0:
            # Highlight PRs with star markers
            ax.scatter(
                records['date'],
                records['estimated_1rm'],
                marker='*',
                s=500,  # Large star
                color='#FFD700',  # Gold color
                edgecolor=text_color,
                linewidth=2,
                zorder=4,
                label='Personal Record'
            )

    # Add trend line if requested
    if show_trend and len(df_grouped) >= 2:
        # Convert dates to numeric for regression
        x_numeric = mdates.date2num(df_grouped['date'])
        y = df_grouped['estimated_1rm'].values

        # Linear regression
        slope, intercept = np.polyfit(x_numeric, y, 1)
        trend_line = slope * x_numeric + intercept

        # Plot trend
        trend_color = '#AAAAAA' if theme == 'dark' else '#666666'
        ax.plot(
            df_grouped['date'],
            trend_line,
            linestyle='--',
            linewidth=2.5,
            color=trend_color,
            alpha=0.8,
            label='Trend',
            zorder=2
        )

    # Add statistical annotations if requested
    if show_statistics and len(df_grouped) >= 2:
        # Calculate statistics
        avg_1rm = df_grouped['estimated_1rm'].mean()
        start_1rm = df_grouped['estimated_1rm'].iloc[0]
        end_1rm = df_grouped['estimated_1rm'].iloc[-1]
        total_improvement = end_1rm - start_1rm
        pct_improvement = (total_improvement / start_1rm) * 100 if start_1rm > 0 else 0

        # Add text box with statistics
        stats_text = (
            f'Avg: {avg_1rm:.1f} kg\n'
            f'Improvement: {total_improvement:+.1f} kg ({pct_improvement:+.1f}%)'
        )

        # Position text box in upper left
        ax.text(
            0.05, 0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment='top',
            bbox=dict(
                boxstyle='round,pad=0.8',
                facecolor='#3a3a3a' if theme == 'dark' else '#f0f0f0',
                edgecolor=primary_color,
                linewidth=2,
                alpha=0.95
            ),
            color=text_color,
            fontweight='bold'
        )

    # Apply academic styling with theme
    apply_academic_style(ax, theme=theme)

    # Labels and title (larger fonts for mobile)
    ax.set_xlabel('Date', fontsize=16, fontweight='bold')
    ax.set_ylabel('Estimated 1RM (kg)', fontsize=16, fontweight='bold')

    if title:
        ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    else:
        ax.set_title(
            f'{exercise} Strength Progression',
            fontsize=20,
            fontweight='bold',
            pad=20
        )

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()  # Rotate date labels

    # Legend with larger font
    ax.legend(loc='upper left', fontsize=12, bbox_to_anchor=(0.05, 0.75))

    # Adjust layout
    fig.tight_layout()

    return fig


# ============================================================================
# VOLUME TRACKING CHARTS
# ============================================================================

def create_volume_chart(
    data: pd.DataFrame,
    exercise: str,
    title: Optional[str] = None,
    chart_type: str = 'bar',
    show_statistics: bool = True,
    theme: str = 'dark'
) -> Figure:
    """
    Create volume tracking chart showing total volume over time.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to visualize
        title: Custom title (optional)
        chart_type: 'bar', 'line', or 'area'
        show_statistics: Whether to show statistical annotations
        theme: Color theme ('dark' or 'light'). Default: 'dark'

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Total volume (sets × reps × weight) over time
        - Bar, line, or area visualization
        - Statistical annotations
        - Date formatting
        - Dark theme optimized for night viewing
    """
    # Calculate volume over time
    volume_series = calculate_volume_over_time(data, exercise=exercise)

    if len(volume_series) == 0:
        raise ValueError(f"No data found for exercise: {exercise}")

    # Create 9:16 figure with theme
    fig = create_9_16_figure(theme=theme)
    ax = fig.add_subplot(111)

    # Get theme colors
    primary_color = get_primary_color(theme=theme)
    text_color = '#e0e0e0' if theme == 'dark' else '#2b2b2b'
    edge_color = text_color if theme == 'dark' else '#2b2b2b'

    # Plot based on chart type
    if chart_type == 'bar':
        ax.bar(
            volume_series.index,
            volume_series.values,
            color=primary_color,
            alpha=0.85,
            edgecolor=edge_color,
            linewidth=1.8
        )
    elif chart_type == 'line':
        ax.plot(
            volume_series.index,
            volume_series.values,
            marker='o',
            markersize=14,
            linewidth=3.5,
            color=primary_color,
            markeredgecolor=text_color,
            markeredgewidth=1.5
        )
    elif chart_type == 'area':
        ax.fill_between(
            volume_series.index,
            volume_series.values,
            color=primary_color,
            alpha=0.6
        )
        ax.plot(
            volume_series.index,
            volume_series.values,
            linewidth=3.5,
            color=primary_color
        )

    # Add statistical annotations if requested
    if show_statistics and len(volume_series) >= 2:
        # Calculate statistics
        avg_volume = volume_series.mean()
        total_volume = volume_series.sum()
        start_volume = volume_series.iloc[0]
        end_volume = volume_series.iloc[-1]
        volume_change = end_volume - start_volume
        pct_change = (volume_change / start_volume) * 100 if start_volume > 0 else 0

        # Add text box with statistics
        stats_text = (
            f'Avg: {avg_volume:.0f} kg\n'
            f'Total: {total_volume:.0f} kg\n'
            f'Change: {volume_change:+.0f} kg ({pct_change:+.1f}%)'
        )

        # Position text box
        ax.text(
            0.05, 0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment='top',
            bbox=dict(
                boxstyle='round,pad=0.8',
                facecolor='#3a3a3a' if theme == 'dark' else '#f0f0f0',
                edgecolor=primary_color,
                linewidth=2,
                alpha=0.95
            ),
            color=text_color,
            fontweight='bold'
        )

    # Apply academic styling with theme
    apply_academic_style(ax, theme=theme)

    # Labels and title (larger fonts for mobile)
    ax.set_xlabel('Date', fontsize=16, fontweight='bold')
    ax.set_ylabel('Total Volume (kg)', fontsize=16, fontweight='bold')

    if title:
        ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    else:
        ax.set_title(
            f'{exercise} Volume Tracking',
            fontsize=20,
            fontweight='bold',
            pad=20
        )

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    # Adjust layout
    fig.tight_layout()

    return fig


# ============================================================================
# COMPARISON CHARTS
# ============================================================================

def create_comparison_chart(
    data: pd.DataFrame,
    exercises: List[str],
    metric: str = 'strength',
    title: Optional[str] = None,
    theme: str = 'dark'
) -> Figure:
    """
    Create comparison chart for multiple exercises.

    Args:
        data: DataFrame with workout data
        exercises: List of exercise names to compare
        metric: Metric to compare ('strength' or 'volume')
        title: Custom title (optional)
        theme: Color theme ('dark' or 'light'). Default: 'dark'

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Multiple exercises on same chart
        - Different colors for each exercise
        - Legend for identification
        - Larger markers and lines for mobile
        - Dark theme optimized for night viewing
    """
    # Create 9:16 figure with theme
    fig = create_9_16_figure(theme=theme)
    ax = fig.add_subplot(111)

    # Get color palette for theme
    colors = get_color_palette('dark', mode=theme)
    text_color = '#e0e0e0' if theme == 'dark' else '#2b2b2b'

    # Plot each exercise
    for i, exercise in enumerate(exercises):
        df = data[data['exercise'].str.lower() == exercise.lower()].copy()

        if len(df) == 0:
            continue

        color = colors[i % len(colors)]

        if metric == 'strength':
            # Calculate estimated 1RM
            df['estimated_1rm'] = df.apply(
                lambda row: calculate_1rm(row['weight'], row['reps']),
                axis=1
            )
            df_grouped = df.groupby('date')['estimated_1rm'].max().reset_index()

            ax.plot(
                df_grouped['date'],
                df_grouped['estimated_1rm'],
                marker='o',
                markersize=12,
                linewidth=3,
                color=color,
                label=exercise,
                markeredgecolor=text_color,
                markeredgewidth=1.2
            )

        elif metric == 'volume':
            volume_series = calculate_volume_over_time(data, exercise=exercise)

            ax.plot(
                volume_series.index,
                volume_series.values,
                marker='o',
                markersize=12,
                linewidth=3,
                color=color,
                label=exercise,
                markeredgecolor=text_color,
                markeredgewidth=1.2
            )

    # Apply academic styling with theme
    apply_academic_style(ax, theme=theme)

    # Labels and title (larger fonts for mobile)
    ax.set_xlabel('Date', fontsize=16, fontweight='bold')

    if metric == 'strength':
        ax.set_ylabel('Estimated 1RM (kg)', fontsize=16, fontweight='bold')
        default_title = 'Strength Progression Comparison'
    else:
        ax.set_ylabel('Total Volume (kg)', fontsize=16, fontweight='bold')
        default_title = 'Volume Comparison'

    ax.set_title(
        title if title else default_title,
        fontsize=20,
        fontweight='bold',
        pad=20
    )

    # Legend with larger font
    ax.legend(loc='best', fontsize=13, framealpha=0.95)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    # Adjust layout
    fig.tight_layout()

    return fig


# ============================================================================
# MULTI-METRIC COMBINED CHARTS
# ============================================================================

def create_combined_metrics_chart(
    data: pd.DataFrame,
    exercise: str,
    title: Optional[str] = None,
    show_statistics: bool = True,
    theme: str = 'dark',
    formula: str = 'epley'
) -> Figure:
    """
    Create combined chart showing both strength and volume progression.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to visualize
        title: Custom title (optional)
        show_statistics: Whether to show statistical annotations
        theme: Color theme ('dark' or 'light'). Default: 'dark'
        formula: 1RM formula to use ('epley', 'brzycki', 'lombardi')

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Two subplots stacked vertically
        - Top: Strength progression (1RM)
        - Bottom: Volume tracking
        - Shared x-axis for time alignment
        - Statistical annotations on both
        - Dark theme optimized for night viewing
    """
    # Filter data for specific exercise
    df = data[data['exercise'].str.lower() == exercise.lower()].copy()

    if len(df) == 0:
        raise ValueError(f"No data found for exercise: {exercise}")

    # Calculate strength data
    df['estimated_1rm'] = df.apply(
        lambda row: calculate_1rm(row['weight'], row['reps'], formula),
        axis=1
    )
    df_strength = df.groupby('date').agg({
        'estimated_1rm': 'max',
        'weight': 'max'
    }).reset_index()

    # Calculate volume data
    volume_series = calculate_volume_over_time(data, exercise=exercise)

    # Create 9:16 figure with theme
    fig = create_9_16_figure(theme=theme)

    # Create two subplots stacked vertically
    # Adjust height ratios to fit 9:16 better
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.25)
    ax1 = fig.add_subplot(gs[0])  # Strength
    ax2 = fig.add_subplot(gs[1], sharex=ax1)  # Volume

    # Get theme colors
    colors = get_color_palette('dark', mode=theme)
    strength_color = colors[0]  # Blue
    volume_color = colors[2]     # Yellow
    text_color = '#e0e0e0' if theme == 'dark' else '#2b2b2b'

    # === TOP PLOT: STRENGTH ===
    ax1.plot(
        df_strength['date'],
        df_strength['estimated_1rm'],
        marker='o',
        markersize=12,
        linewidth=3,
        color=strength_color,
        label='Estimated 1RM',
        markeredgecolor=text_color,
        markeredgewidth=1.2
    )

    # Add statistical annotations for strength
    if show_statistics and len(df_strength) >= 2:
        avg_1rm = df_strength['estimated_1rm'].mean()
        start_1rm = df_strength['estimated_1rm'].iloc[0]
        end_1rm = df_strength['estimated_1rm'].iloc[-1]
        improvement = end_1rm - start_1rm
        pct_improvement = (improvement / start_1rm) * 100 if start_1rm > 0 else 0

        stats_text = f'Avg: {avg_1rm:.1f} kg | Change: {improvement:+.1f} kg ({pct_improvement:+.1f}%)'

        ax1.text(
            0.5, 0.95,
            stats_text,
            transform=ax1.transAxes,
            fontsize=12,
            verticalalignment='top',
            horizontalalignment='center',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='#3a3a3a' if theme == 'dark' else '#f0f0f0',
                edgecolor=strength_color,
                linewidth=2,
                alpha=0.95
            ),
            color=text_color,
            fontweight='bold'
        )

    apply_academic_style(ax1, theme=theme)
    ax1.set_ylabel('Estimated 1RM (kg)', fontsize=15, fontweight='bold')
    ax1.set_title(
        title if title else f'{exercise} - Strength & Volume',
        fontsize=18,
        fontweight='bold',
        pad=15
    )
    ax1.tick_params(labelbottom=False)  # Hide x labels on top plot

    # === BOTTOM PLOT: VOLUME ===
    ax2.bar(
        volume_series.index,
        volume_series.values,
        color=volume_color,
        alpha=0.85,
        edgecolor=text_color,
        linewidth=1.5
    )

    # Add statistical annotations for volume
    if show_statistics and len(volume_series) >= 2:
        avg_volume = volume_series.mean()
        total_volume = volume_series.sum()
        start_volume = volume_series.iloc[0]
        end_volume = volume_series.iloc[-1]
        volume_change = end_volume - start_volume
        pct_change = (volume_change / start_volume) * 100 if start_volume > 0 else 0

        stats_text = f'Avg: {avg_volume:.0f} kg | Total: {total_volume:.0f} kg | Change: {pct_change:+.1f}%'

        ax2.text(
            0.5, 0.95,
            stats_text,
            transform=ax2.transAxes,
            fontsize=12,
            verticalalignment='top',
            horizontalalignment='center',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='#3a3a3a' if theme == 'dark' else '#f0f0f0',
                edgecolor=volume_color,
                linewidth=2,
                alpha=0.95
            ),
            color=text_color,
            fontweight='bold'
        )

    apply_academic_style(ax2, theme=theme)
    ax2.set_xlabel('Date', fontsize=15, fontweight='bold')
    ax2.set_ylabel('Volume (kg)', fontsize=15, fontweight='bold')

    # Format x-axis dates (only on bottom plot)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    # Adjust layout
    fig.tight_layout()

    return fig
