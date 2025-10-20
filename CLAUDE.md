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
│   ├── data/          # Data loading and processing modules
│   ├── analysis/      # Statistical analysis and metrics
│   └── visualization/ # Graph generation and styling
├── cli/               # Command-line interface
├── data/              # Sample workout data and datasets
├── output/            # Generated .png visualizations
├── requirements.txt   # Python dependencies
├── claude.md          # This file - architecture guidance
└── .gitignore        # Git exclusions
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

**Example Commands** (to be implemented):
```bash
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

### Future Enhancements
- Interactive web dashboard (optional)
- Export to PDF for detailed reports
- Integration with workout tracking apps
- Machine learning for periodization recommendations
- Automated Instagram/TikTok posting
