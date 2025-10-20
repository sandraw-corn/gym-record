# Gym Record Analysis & Visualization

## Project Overview
A professional gym records analysis tool designed to track workout progression with a focus on hypertrophy (muscle growth) and strength development.

## Key Features
- **Data Analysis**: Track and analyze gym records including sets, reps, weight, and volume
- **Progression Tracking**: Monitor strength and hypertrophy progression over time
- **Professional Visualization**: Generate high-quality, academic-style graphs and charts

## Output Specifications
- **Format**: PNG images
- **Aspect Ratio**: 9:16 (optimized for TikTok vertical display)
- **Style**: Academic quality with professional presentation
- **Target Use**: Social media content that maintains scientific rigor

## Goals
1. Provide accurate, data-driven insights into workout progression
2. Create visually compelling graphs suitable for social media
3. Maintain academic standards in data visualization
4. Enable evidence-based training decisions through clear metrics

## Visualization Focus
- Strength progression charts
- Volume tracking over time
- Hypertrophy indicators
- Exercise-specific performance metrics
- Periodization analysis

## Technical Architecture

### Tech Stack
- **Language**: Python 3.10+
- **Environment**: Conda (gym-record environment)
- **Visualization Libraries**:
  - **matplotlib**: Publication-quality graphs with full control
  - **seaborn**: Statistical visualizations with academic styling
- **Data Processing**:
  - **pandas**: Data manipulation and analysis
  - **numpy**: Numerical computations
  - **scipy**: Statistical analysis and calculations

### Project Structure
```
gym-record/
├── src/
│   ├── data/              # Data loading and processing modules
│   │   ├── loader.py      # CSV loading, filtering, validation
│   │   ├── formatter.py   # LLM-based Chinese log → JSON formatter
│   │   └── validator.py   # JSON schema validation & auto-fix
│   ├── analysis/          # Statistical analysis and metrics
│   │   └── metrics.py     # 1RM, volume, trends, progressive overload
│   └── visualization/     # Graph generation and styling
│       ├── styling.py     # 9:16 aspect ratio, academic themes
│       └── charts.py      # Strength, volume, comparison charts
├── cli/
│   └── gym_cli.py         # CLI commands (visualize, analyze, compare, format)
├── tests/
│   ├── unit/              # Unit tests (73 tests)
│   ├── integration/       # Integration tests (16 tests: 13 core + 3 API)
│   └── manual/            # Manual formatter tests (4 tests)
├── data/                  # Workout data (CSV files, git-ignored except samples)
│   ├── sample_workout.csv # Sample structured workout data
│   └── sample_log.txt     # Sample Chinese workout log
├── output/                # Generated .png visualizations (git-ignored)
├── docs/
│   ├── development.md     # Current development priorities
│   └── llm-formatter.md   # LLM formatter detailed guide
├── .env.example           # Environment config template (Gemini API)
├── requirements.txt       # Python dependencies
├── pytest.ini             # Test configuration
├── CLAUDE.md              # This file - architecture guidance
└── .gitignore             # Git exclusions
```

### Environment Setup

**CRITICAL**: All CLI commands must be run with conda environment activated:

```bash
# Create conda environment (first time only)
conda create -n gym-record python=3.10 -y

# Activate environment (ALWAYS required before running commands)
source ~/.zshrc && conda activate gym-record

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import matplotlib; import seaborn; import pandas; print('All dependencies installed')"
```

### CLI Commands Pattern

**Environment activation prefix** (ALWAYS required):
```bash
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli <command>
```

**Example Commands**:
```bash
# Format Chinese workout log to CSV (requires Gemini API key)
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli format --input data/raw_log.txt --date 2024-01-20 --output data/workout.csv

# Preview formatting without saving (dry-run mode)
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli format --input data/raw_log.txt --date 2024-01-20 --dry-run

# Generate strength progression chart
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli visualize --exercise "Bench Press" --metric strength --output output/bench_strength.png

# Analyze volume progression
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli visualize --exercise "Squat" --metric volume --period 12weeks

# Compare multiple exercises
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli compare --exercises "Bench Press,Squat,Deadlift" --metric strength

# Generate hypertrophy analysis
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli analyze --focus hypertrophy --period 8weeks

# List available data
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli list-data
```

### Visualization Specifications

**9:16 Aspect Ratio Configuration**:
```python
# Standard TikTok size: 1080x1920 pixels
# For high-quality: 1440x2560 pixels (1.5x)
# Figsize calculation: width=9, height=16 inches with DPI=120-180

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 16), dpi=160)
```

**Academic Style Requirements**:
- Clean, minimalist design with high contrast
- Grid lines for readability
- Clear axis labels with units
- Professional color schemes (not flashy)
- Proper legends and annotations
- Citation-quality fonts and sizing
- Statistical indicators (confidence intervals, trend lines)

**Graph Types to Support**:
1. **Strength Progression**: Line charts with trend analysis
2. **Volume Tracking**: Bar charts or area plots over time
3. **1RM Estimation**: Calculated max strength with confidence intervals
4. **Exercise Comparison**: Multi-line plots or grouped bars
5. **Periodization Analysis**: Phase-based breakdown with annotations
6. **Rep Range Distribution**: Histograms or heatmaps
7. **Progressive Overload**: Cumulative volume or intensity charts

### Import Conventions

**All imports use absolute paths from project root:**
```python
# Correct - absolute imports
from src.data.loader import load_workout_data
from src.analysis.metrics import calculate_1rm, estimate_volume
from src.visualization.charts import create_progression_chart
from cli.gym_cli import main

# ❌ Avoid - relative imports
from ..data import loader  # Don't use this
from .metrics import calculate_1rm  # Don't use this
```

### Data Format Specification

**Expected CSV/JSON structure**:
```csv
date,exercise,sets,reps,weight,rpe,notes
2024-01-15,Bench Press,3,8,185,8.5,
2024-01-17,Squat,4,6,275,9.0,Felt heavy
2024-01-19,Deadlift,3,5,315,8.0,
```

**Key Fields**:
- `date`: ISO format (YYYY-MM-DD)
- `exercise`: Exercise name (string)
- `sets`: Number of sets (integer)
- `reps`: Repetitions per set (integer or list)
- `weight`: Weight used in lbs/kg (float)
- `rpe`: Rate of Perceived Exertion 1-10 (optional)
- `notes`: Free text (optional)

### LLM Formatter for Chinese Workout Logs

**Purpose**: Convert messy Chinese training logs into structured CSV format using Google Gemini Flash 2.5.

**Quick Setup**:
1. Get free API key at https://aistudio.google.com/apikey
2. Copy `.env.example` to `.env` and add your key
3. Run: `python -m cli.gym_cli format --input log.txt --date 2024-01-20 --output workout.csv`

**Key Features**:
- 80+ exercise mappings (Chinese → English)
- Bilateral exercise detection ("先左后右" = 1 set, not 2)
- Auto-validation with smart fixes
- Dual output modes (aggregated/detailed)

**📖 Detailed Documentation**: See `docs/llm-formatter.md` for:
- Bilateral exercise handling (critical edge case)
- Complete exercise mapping dictionary
- Validator auto-fix capabilities
- Troubleshooting guide
- Advanced usage examples

### Development Workflow

**Running the CLI**:
```bash
# Navigate to project root
cd ~/gym-record

# Activate environment and run command
source ~/.zshrc && conda activate gym-record && python -m cli.gym_cli <command>
```

**Note**: The `source ~/.zshrc && conda activate gym-record` prefix ensures the correct Python environment with all required dependencies (matplotlib, seaborn, pandas, etc.) is used.

### Git Workflow

**Commit Style** (conventional commits):
```bash
feat: add volume progression visualization
fix: correct 1RM calculation formula
docs: update visualization specifications
style: improve graph color schemes for readability
refactor: modularize chart generation code
```

## File Organization

### Key Documentation Files

**Core Development Docs (Frequently Updated):**
- **`CLAUDE.md`** (this file) - Architecture guidance, setup instructions, Claude Code workflow
  - ✅ Should contain: Project structure, setup commands, architecture overview
  - ❌ Should NOT contain: Current todos, temporary status updates

- **`docs/development.md`** - Current development priorities only
  - ✅ Should contain: Active todos, technical problems, implementation priorities
  - ❌ Should NOT contain: Completed tasks (tracked in git history)

- **`README.md`** - Project overview and quick start
  - ✅ Should contain: High-level overview, quick start, main features
  - ❌ Should NOT contain: Detailed architecture, current development status

**Documentation Management:**
Use `/update-docs` when documentation appears outdated or before creating pull requests.

### Documentation Structure
- `docs/development.md` - **CURRENT PRIORITIES**: Active todos, phase tracking, technical decisions
- `docs/llm-formatter.md` - **LLM FORMATTER**: Detailed guide for Chinese log processing, prompts, troubleshooting
- `docs/visualization-guide.md` (future) - Graph specifications, color palettes, examples
- `docs/troubleshooting.md` (future) - Common issues and solutions

### Code Structure
- `src/data/` - Data loading and processing modules
- `src/analysis/` - Statistical analysis and metrics calculation
- `src/visualization/` - Graph generation with academic styling
- `cli/gym_cli.py` - Command-line interface with click

### Data Organization
- `data/` - Workout data CSV files (git ignored, except samples)
- `output/` - Generated PNG visualizations (git ignored)

### Future Enhancements
- Interactive web dashboard (optional)
- Export to PDF for detailed reports
- Integration with workout tracking apps
- Machine learning for periodization recommendations
- Automated Instagram/TikTok posting
