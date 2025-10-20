"""Visualization module for gym workout charts."""

from src.visualization.charts import (
    create_strength_progression_chart,
    create_volume_chart,
    create_comparison_chart,
    create_combined_metrics_chart,
)
from src.visualization.styling import (
    create_9_16_figure,
    apply_academic_style,
    get_color_palette,
    get_primary_color,
    save_figure,
    configure_academic_defaults,
)

__all__ = [
    # Chart functions
    'create_strength_progression_chart',
    'create_volume_chart',
    'create_comparison_chart',
    'create_combined_metrics_chart',
    # Styling functions
    'create_9_16_figure',
    'apply_academic_style',
    'get_color_palette',
    'get_primary_color',
    'save_figure',
    'configure_academic_defaults',
]
