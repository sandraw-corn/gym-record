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
    formula: str = 'epley'
) -> Figure:
    """
    Create strength progression chart showing estimated 1RM over time.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to visualize
        title: Custom title (optional, auto-generated if None)
        show_trend: Whether to show trend line
        formula: 1RM formula to use ('epley', 'brzycki', 'lombardi')

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Estimated 1RM over time
        - Data points with markers
        - Optional trend line
        - Date formatting on x-axis
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

    # Create 9:16 figure
    fig = create_9_16_figure()
    ax = fig.add_subplot(111)

    # Plot data points
    ax.plot(
        df_grouped['date'],
        df_grouped['estimated_1rm'],
        marker='o',
        markersize=10,
        linewidth=2.5,
        color=get_primary_color(),
        label='Estimated 1RM',
        zorder=3
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
        ax.plot(
            df_grouped['date'],
            trend_line,
            linestyle='--',
            linewidth=2,
            color='gray',
            alpha=0.7,
            label='Trend',
            zorder=2
        )

    # Apply academic styling
    apply_academic_style(ax)

    # Labels and title
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Estimated 1RM (kg)', fontsize=14, fontweight='bold')

    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    else:
        ax.set_title(
            f'{exercise} Strength Progression',
            fontsize=16,
            fontweight='bold',
            pad=20
        )

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()  # Rotate date labels

    # Legend
    if show_trend:
        ax.legend(loc='best', fontsize=11)

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
    chart_type: str = 'bar'
) -> Figure:
    """
    Create volume tracking chart showing total volume over time.

    Args:
        data: DataFrame with workout data
        exercise: Exercise name to visualize
        title: Custom title (optional)
        chart_type: 'bar', 'line', or 'area'

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Total volume (sets × reps × weight) over time
        - Bar, line, or area visualization
        - Date formatting
    """
    # Calculate volume over time
    volume_series = calculate_volume_over_time(data, exercise=exercise)

    if len(volume_series) == 0:
        raise ValueError(f"No data found for exercise: {exercise}")

    # Create 9:16 figure
    fig = create_9_16_figure()
    ax = fig.add_subplot(111)

    # Plot based on chart type
    if chart_type == 'bar':
        ax.bar(
            volume_series.index,
            volume_series.values,
            color=get_primary_color(),
            alpha=0.8,
            edgecolor='black',
            linewidth=1.5
        )
    elif chart_type == 'line':
        ax.plot(
            volume_series.index,
            volume_series.values,
            marker='o',
            markersize=10,
            linewidth=2.5,
            color=get_primary_color()
        )
    elif chart_type == 'area':
        ax.fill_between(
            volume_series.index,
            volume_series.values,
            color=get_primary_color(),
            alpha=0.5
        )
        ax.plot(
            volume_series.index,
            volume_series.values,
            linewidth=2.5,
            color=get_primary_color()
        )

    # Apply academic styling
    apply_academic_style(ax)

    # Labels and title
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Total Volume (kg)', fontsize=14, fontweight='bold')

    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    else:
        ax.set_title(
            f'{exercise} Volume Tracking',
            fontsize=16,
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
    title: Optional[str] = None
) -> Figure:
    """
    Create comparison chart for multiple exercises.

    Args:
        data: DataFrame with workout data
        exercises: List of exercise names to compare
        metric: Metric to compare ('strength' or 'volume')
        title: Custom title (optional)

    Returns:
        matplotlib Figure with 9:16 aspect ratio

    Chart features:
        - Multiple exercises on same chart
        - Different colors for each exercise
        - Legend for identification
    """
    # Create 9:16 figure
    fig = create_9_16_figure()
    ax = fig.add_subplot(111)

    # Get color palette
    colors = get_color_palette('academic')

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
                markersize=8,
                linewidth=2,
                color=color,
                label=exercise
            )

        elif metric == 'volume':
            volume_series = calculate_volume_over_time(data, exercise=exercise)

            ax.plot(
                volume_series.index,
                volume_series.values,
                marker='o',
                markersize=8,
                linewidth=2,
                color=color,
                label=exercise
            )

    # Apply academic styling
    apply_academic_style(ax)

    # Labels and title
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')

    if metric == 'strength':
        ax.set_ylabel('Estimated 1RM (kg)', fontsize=14, fontweight='bold')
        default_title = 'Strength Progression Comparison'
    else:
        ax.set_ylabel('Total Volume (kg)', fontsize=14, fontweight='bold')
        default_title = 'Volume Comparison'

    ax.set_title(
        title if title else default_title,
        fontsize=16,
        fontweight='bold',
        pad=20
    )

    # Legend
    ax.legend(loc='best', fontsize=11, framealpha=0.9)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    # Adjust layout
    fig.tight_layout()

    return fig
