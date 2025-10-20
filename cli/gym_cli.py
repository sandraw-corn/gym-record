#!/usr/bin/env python3
"""
Gym Record CLI - Command-line interface for workout analysis and visualization

Usage:
    source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli <command>

Commands:
    format    - Convert raw Chinese workout logs to structured CSV
    visualize - Generate visualization graphs
    analyze   - Perform statistical analysis
    compare   - Compare multiple exercises
    list-data - List available workout data
"""

import sys
import json
import csv
import click
from pathlib import Path
from datetime import datetime

from src.data.loader import WorkoutDataLoader
from src.visualization.charts import (
    create_strength_progression_chart,
    create_volume_chart,
    create_comparison_chart,
    create_combined_metrics_chart,
    create_rep_range_heatmap
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
@click.option('--input', '-i', type=click.Path(exists=True), help='Input file (raw Chinese log). If not provided, reads from stdin.')
@click.option('--output', '-o', type=click.Path(), help='Output CSV file. If not provided, writes to stdout.')
@click.option('--date', '-d', help='Date for workout (YYYY-MM-DD). If not provided, LLM will infer.')
@click.option('--dry-run', is_flag=True, help='Preview JSON output without writing CSV')
@click.option('--json-output', is_flag=True, help='Output JSON instead of CSV')
@click.option('--detailed', is_flag=True, help='Output one row per set (default: one row per exercise)')
@click.option('--validate/--no-validate', default=True, help='Validate output schema (default: True)')
def format(input, output, date, dry_run, json_output, detailed, validate):
    """Convert raw Chinese workout logs to structured CSV/JSON"""

    # Import here to avoid slow startup for other commands
    from src.data.formatter import WorkoutLogFormatter

    # Read input
    if input:
        with open(input, 'r', encoding='utf-8') as f:
            raw_log = f.read()
        click.echo(f"📖 Reading from: {input}")
    else:
        click.echo("📖 Reading from stdin (Ctrl+D when done)...")
        raw_log = sys.stdin.read()

    if not raw_log.strip():
        click.secho("✗ No input provided", fg='red')
        sys.exit(1)

    # Validate date format if provided
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            click.secho(f"✗ Invalid date format: {date} (use YYYY-MM-DD)", fg='red')
            sys.exit(1)

    # Format log
    click.echo("🤖 Processing with Gemini API...")

    try:
        formatter = WorkoutLogFormatter()
        result = formatter.format_log(raw_log, date=date, validate=validate)
    except ValueError as e:
        click.secho(f"✗ Configuration error: {e}", fg='red')
        click.echo("   Check that GOOGLE_API_KEY is set in .env file")
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Formatting failed: {e}", fg='red')
        sys.exit(1)

    # Check for errors
    if not result['success']:
        click.secho(f"✗ Formatting failed: {result.get('error')}", fg='red')

        if 'validation_errors' in result:
            click.echo("\nValidation errors:")
            for error in result['validation_errors']:
                click.echo(f"  • {error}")

        sys.exit(1)

    data = result['data']
    click.secho(f"✓ Successfully formatted {len(data)} exercise(s)", fg='green')

    # Dry run - just show JSON
    if dry_run:
        click.echo("\n" + "=" * 70)
        click.echo("Preview (JSON):")
        click.echo("=" * 70)
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        click.echo("\nTo save as CSV, remove --dry-run flag")
        return

    # JSON output mode
    if json_output:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_str)
            click.secho(f"✓ JSON saved to: {output}", fg='green')
        else:
            click.echo(json_str)

        return

    # CSV output mode (default)
    # Use aggregated format (one row per exercise) for compatibility with main branch
    # Use detailed format (one row per set) only if --detailed flag is specified
    if detailed:
        csv_rows = formatter.format_to_csv_rows(data)
    else:
        csv_rows = formatter.format_to_csv_aggregated(data)

    if not csv_rows:
        click.secho("⚠ No data to export", fg='yellow')
        return

    # Determine fieldnames from first row
    fieldnames = list(csv_rows[0].keys())

    if output:
        # Write to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        click.secho(f"✓ CSV saved to: {output}", fg='green')
        click.echo(f"  {len(csv_rows)} row(s) written")
    else:
        # Write to stdout
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)


@cli.command()
@click.option('--exercise', '-e', required=True, help='Exercise name (e.g., "Bench Press")')
@click.option('--metric', '-m', type=click.Choice(['volume', 'strength', '1rm', 'combined', 'rep_range']), default='volume', help='Metric to visualize (default: volume for hypertrophy)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--period', '-p', default='all', help='Time period (e.g., "12weeks", "3months", "all")')
@click.option('--data', '-d', default='data/sample_workout.csv', help='Path to workout data CSV')
@click.option('--theme', '-t', type=click.Choice(['dark', 'light']), default='dark', help='Color theme (default: dark for night viewing)')
@click.option('--no-stats', is_flag=True, help='Disable statistical annotations')
@click.option('--no-records', is_flag=True, help='Disable personal record markers (strength charts only)')
def visualize(exercise, metric, output, period, data, theme, no_stats, no_records):
    """Generate visualization graphs for workout progression

    Examples:
        # Dark theme volume chart with stats (default - hypertrophy focus)
        python -m cli.gym_cli visualize -e "Bench Press"

        # Rep range analysis for hypertrophy zone
        python -m cli.gym_cli visualize -e "Squat" -m rep_range

        # Combined volume + rep progression (hypertrophy mode)
        python -m cli.gym_cli visualize -e "Squat" -m combined

        # Strength chart for powerlifting analysis
        python -m cli.gym_cli visualize -e "Deadlift" -m strength
    """
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
        show_stats = not no_stats
        show_records = not no_records

        if metric in ['strength', '1rm']:
            click.echo(f"📊 Generating strength progression chart for {exercise}...")
            click.echo(f"   Theme: {theme} | Stats: {show_stats} | PR markers: {show_records}")
            fig = create_strength_progression_chart(
                df,
                exercise=exercise,
                show_trend=True,
                show_statistics=show_stats,
                show_records=show_records,
                show_prediction=True,
                theme=theme
            )
        elif metric == 'volume':
            click.echo(f"📊 Generating volume tracking chart for {exercise}...")
            click.echo(f"   Theme: {theme} | Stats: {show_stats}")
            fig = create_volume_chart(
                df,
                exercise=exercise,
                chart_type='bar',
                show_statistics=show_stats,
                show_prediction=True,
                theme=theme
            )
        elif metric == 'rep_range':
            click.echo(f"📊 Generating rep range analysis chart for {exercise}...")
            click.echo(f"   Theme: {theme} | Stats: {show_stats}")
            fig = create_rep_range_heatmap(
                df,
                exercise=exercise,
                show_statistics=show_stats,
                theme=theme
            )
        elif metric == 'combined':
            click.echo(f"📊 Generating combined metrics chart for {exercise}...")
            click.echo(f"   Theme: {theme} | Stats: {show_stats} | Mode: hypertrophy")
            fig = create_combined_metrics_chart(
                df,
                exercise=exercise,
                show_statistics=show_stats,
                mode='hypertrophy',
                theme=theme
            )

        # Determine output path
        if not output:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output = output_dir / f"{exercise.lower().replace(' ', '_')}_{metric}_{theme}.png"

        # Save figure with theme
        save_figure(fig, str(output), theme=theme)

        click.secho(f"✓ Chart saved to: {output}", fg='green')
        click.echo(f"  • Theme: {theme} mode (optimized for {'night' if theme == 'dark' else 'day'} viewing)")
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
@click.option('--metric', '-m', type=click.Choice(['volume', 'strength', '1rm']), default='volume', help='Comparison metric (default: volume for hypertrophy)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--data', '-d', default='data/sample_workout.csv', help='Path to workout data CSV')
@click.option('--theme', '-t', type=click.Choice(['dark', 'light']), default='dark', help='Color theme (default: dark for night viewing)')
def compare(exercises, metric, output, data, theme):
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
        click.echo(f"   Theme: {theme}")

        # Generate comparison chart
        metric_type = 'strength' if metric in ['strength', '1rm'] else 'volume'
        fig = create_comparison_chart(df, exercises=exercise_list, metric=metric_type, theme=theme)

        # Determine output path
        if not output:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output = output_dir / f"comparison_{metric}_{theme}.png"

        # Save figure with theme
        save_figure(fig, str(output), theme=theme)

        click.secho(f"✓ Comparison chart saved to: {output}", fg='green')
        click.echo(f"  • Theme: {theme} mode (optimized for {'night' if theme == 'dark' else 'day'} viewing)")

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
