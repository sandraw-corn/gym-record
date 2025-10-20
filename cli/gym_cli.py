#!/usr/bin/env python3
"""
Gym Record CLI - Command-line interface for workout analysis and visualization

Usage:
    source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli <command>

Commands:
    visualize - Generate visualization graphs
    analyze   - Perform statistical analysis
    compare   - Compare multiple exercises
    list-data - List available workout data
"""

import click
from pathlib import Path
import sys

from src.data.loader import WorkoutDataLoader
from src.visualization.charts import (
    create_strength_progression_chart,
    create_volume_chart,
    create_comparison_chart
)
from src.visualization.styling import save_figure
from src.analysis.metrics import (
    calculate_volume_by_exercise,
    calculate_strength_progression,
    detect_progressive_overload,
    estimate_1rm_from_workout
)


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Gym Record Analysis & Visualization CLI"""
    pass


@cli.command()
@click.option('--exercise', '-e', required=True, help='Exercise name (e.g., "Bench Press")')
@click.option('--metric', '-m', type=click.Choice(['strength', 'volume', '1rm']), default='strength', help='Metric to visualize')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--period', '-p', default='all', help='Time period (e.g., "12weeks", "3months", "all")')
@click.option('--data', '-d', default='data/sample_workout.csv', help='Path to workout data CSV')
def visualize(exercise, metric, output, period, data):
    """Generate visualization graphs for workout progression"""
    try:
        # Load data
        # Extract just the filename if full path is provided
        from pathlib import Path
        data_file = Path(data).name
        loader = WorkoutDataLoader()
        df = loader.load_csv(data_file)

        # Filter by exercise
        exercise_data = loader.filter_by_exercise(exercise)

        if len(exercise_data) == 0:
            click.secho(f"✗ No data found for exercise: {exercise}", fg='red')
            sys.exit(1)

        # Generate chart based on metric
        if metric in ['strength', '1rm']:
            click.echo(f"📊 Generating strength progression chart for {exercise}...")
            fig = create_strength_progression_chart(df, exercise=exercise, show_trend=True)
        elif metric == 'volume':
            click.echo(f"📊 Generating volume tracking chart for {exercise}...")
            fig = create_volume_chart(df, exercise=exercise, chart_type='bar')

        # Determine output path
        if not output:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output = output_dir / f"{exercise.lower().replace(' ', '_')}_{metric}.png"

        # Save figure
        save_figure(fig, str(output))

        click.secho(f"✓ Chart saved to: {output}", fg='green')
        click.echo(f"  • Aspect ratio: 9:16 (perfect for TikTok/Xiaohongshu)")
        click.echo(f"  • Resolution: {int(fig.get_figwidth() * fig.dpi)}x{int(fig.get_figheight() * fig.dpi)} pixels")

        # Close figure
        import matplotlib.pyplot as plt
        plt.close(fig)

    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg='red')
        sys.exit(1)


@cli.command()
@click.option('--focus', '-f', type=click.Choice(['hypertrophy', 'strength', 'volume']), required=True, help='Analysis focus')
@click.option('--period', '-p', default='8weeks', help='Time period to analyze')
@click.option('--data', '-d', default='data/sample_workout.csv', help='Path to workout data CSV')
def analyze(focus, period, data):
    """Perform statistical analysis on workout data"""
    try:
        # Load data
        # Extract just the filename if full path is provided
        from pathlib import Path
        data_file = Path(data).name
        loader = WorkoutDataLoader()
        df = loader.load_csv(data_file)

        summary = loader.get_summary()

        click.echo(f"\n{'='*60}")
        click.echo(f"  WORKOUT ANALYSIS - Focus: {focus.upper()}")
        click.echo(f"{'='*60}\n")

        click.echo(f"📅 Date Range: {summary['date_range'][0]} to {summary['date_range'][1]}")
        click.echo(f"📊 Total Records: {summary['total_records']} sets")
        click.echo(f"💪 Exercises: {summary['unique_exercises']}\n")

        if focus == 'strength':
            click.echo("🏋️  STRENGTH ANALYSIS\n")

            for exercise in summary['exercises'][:5]:  # Top 5 exercises
                try:
                    ex_data = loader.filter_by_exercise(exercise)
                    if len(ex_data) == 0:
                        continue

                    # Get best set
                    best_set = ex_data.nlargest(1, 'reps').iloc[0]
                    from src.analysis.metrics import calculate_1rm
                    est_1rm = calculate_1rm(best_set['weight'], best_set['reps'])

                    click.echo(f"  {exercise}:")
                    click.echo(f"    Best set: {int(best_set['reps'])} reps @ {best_set['weight']}kg")
                    click.echo(f"    Estimated 1RM: {est_1rm:.1f}kg")

                    # Progressive overload check
                    overload = detect_progressive_overload(df, exercise)
                    if overload['has_overload']:
                        click.secho(f"    ✓ Progressive overload detected ({overload['type']})", fg='green')
                    else:
                        click.secho(f"    ⚠ No significant progression", fg='yellow')

                    click.echo("")

                except Exception as e:
                    continue

        elif focus == 'volume':
            click.echo("📈 VOLUME ANALYSIS\n")

            volume_by_ex = calculate_volume_by_exercise(df)

            # Sort by volume
            sorted_exercises = sorted(volume_by_ex.items(), key=lambda x: x[1], reverse=True)

            for exercise, volume in sorted_exercises[:10]:  # Top 10
                click.echo(f"  {exercise}: {volume:,.0f}kg total volume")

        elif focus == 'hypertrophy':
            click.echo("💪 HYPERTROPHY ANALYSIS\n")

            for exercise in summary['exercises'][:5]:
                ex_data = loader.filter_by_exercise(exercise)
                if len(ex_data) == 0:
                    continue

                # Rep range analysis
                avg_reps = ex_data['reps'].mean()
                total_sets = len(ex_data)

                click.echo(f"  {exercise}:")
                click.echo(f"    Total sets: {total_sets}")
                click.echo(f"    Average reps: {avg_reps:.1f}")

                if 6 <= avg_reps <= 12:
                    click.secho(f"    ✓ Optimal hypertrophy range (6-12 reps)", fg='green')
                else:
                    click.secho(f"    ⚠ Outside typical hypertrophy range", fg='yellow')

                click.echo("")

    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg='red')
        sys.exit(1)


@cli.command()
@click.option('--exercises', '-e', required=True, help='Comma-separated list of exercises')
@click.option('--metric', '-m', type=click.Choice(['strength', 'volume', '1rm']), default='strength', help='Comparison metric')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--data', '-d', default='data/sample_workout.csv', help='Path to workout data CSV')
def compare(exercises, metric, output, data):
    """Compare progression across multiple exercises"""
    try:
        # Parse exercise list
        exercise_list = [ex.strip() for ex in exercises.split(',')]

        # Load data
        # Extract just the filename if full path is provided
        from pathlib import Path
        data_file = Path(data).name
        loader = WorkoutDataLoader()
        df = loader.load_csv(data_file)

        click.echo(f"📊 Comparing {metric} for {len(exercise_list)} exercises...")

        # Generate comparison chart
        metric_type = 'strength' if metric in ['strength', '1rm'] else 'volume'
        fig = create_comparison_chart(df, exercises=exercise_list, metric=metric_type)

        # Determine output path
        if not output:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output = output_dir / f"comparison_{metric}.png"

        # Save figure
        save_figure(fig, str(output))

        click.secho(f"✓ Comparison chart saved to: {output}", fg='green')

        # Close figure
        import matplotlib.pyplot as plt
        plt.close(fig)

    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg='red')
        sys.exit(1)


@cli.command(name='list-data')
def list_data():
    """List available workout data files"""
    data_dir = Path('data')

    if not data_dir.exists():
        click.secho("✗ Data directory not found", fg='red')
        return

    click.echo("Available workout data files:")
    click.echo("")

    data_files = list(data_dir.glob('*.csv')) + list(data_dir.glob('*.json'))

    if not data_files:
        click.secho("No data files found in data/", fg='yellow')
        return

    for file in data_files:
        size_kb = file.stat().st_size / 1024
        click.echo(f"  • {file.name} ({size_kb:.1f} KB)")

    click.echo(f"\nTotal: {len(data_files)} file(s)")


if __name__ == '__main__':
    cli()
