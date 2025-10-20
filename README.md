# Gym Record Analysis & Visualization

Professional workout tracking and progression analysis with academic-quality visualizations optimized for social media (9:16 TikTok format).

## Features

- **Strength Progression Tracking** - Monitor 1RM estimates and strength gains over time
- **Volume Analysis** - Track total training volume and periodization
- **Hypertrophy Metrics** - Analyze progressive overload for muscle growth
- **Academic-Quality Graphs** - Publication-style visualizations with professional aesthetics
- **Social Media Ready** - 9:16 aspect ratio PNG exports optimized for TikTok/Instagram Stories

## Quick Start

### 1. Environment Setup

```bash
# Create conda environment
conda create -n gym-record python=3.10 -y

# Activate environment
source ~/.zshrc && conda activate gym-record

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import matplotlib; import seaborn; import pandas; print('✓ All dependencies installed')"
```

### 3. List Sample Data

```bash
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli list-data
```

## Usage

All commands require conda environment activation:

```bash
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli <command>
```

### Available Commands

```bash
# Generate strength progression chart
python -m cli.gym_cli visualize --exercise "Bench Press" --metric strength

# Analyze volume over 12 weeks
python -m cli.gym_cli visualize --exercise "Squat" --metric volume --period 12weeks

# Compare multiple exercises
python -m cli.gym_cli compare --exercises "Bench Press,Squat,Deadlift" --metric strength

# Analyze hypertrophy metrics
python -m cli.gym_cli analyze --focus hypertrophy --period 8weeks
```

## Data Format

Place your workout data in `data/` directory as CSV files:

```csv
date,exercise,sets,reps,weight,rpe,notes
2024-01-15,Bench Press,3,8,185,8.5,Felt strong
2024-01-17,Squat,4,6,275,9.0,
```

See `data/sample_workout.csv` for example format.

## Project Structure

```
gym-record/
├── src/
│   ├── data/          # Data loading and processing
│   ├── analysis/      # Statistical analysis and metrics
│   └── visualization/ # Graph generation
├── cli/               # Command-line interface
├── data/              # Workout data (CSV/JSON)
├── output/            # Generated visualizations
└── requirements.txt   # Python dependencies
```

## Tech Stack

- **Python 3.10+** - Core language
- **matplotlib + seaborn** - Professional graph generation
- **pandas** - Data manipulation and analysis
- **numpy + scipy** - Scientific computing and statistics
- **click** - CLI framework

## Development

See `claude.md` for detailed architecture documentation and development guidelines.

## Future Features

- Web dashboard
- PDF report generation
- Machine learning periodization recommendations
- Automated social media posting

## License

MIT
