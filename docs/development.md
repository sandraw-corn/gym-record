# Development Roadmap & Priorities

## 🎯 Current Development Focus

**Current Phase**: Phase 1 - Core Foundation
**Status**: Setting up data pipeline and visualization system

**Goal**: Build MVP with data loading, analysis, and 9:16 visualization capabilities

---

## Phase 1: Core Foundation & MVP (IN PROGRESS)

**Branch**: `main`
**Status**: Foundation setup complete, now implementing core features

### Completed ✅

- [x] Project structure and conda environment setup
- [x] CLAUDE.md with architecture guidance
- [x] requirements.txt with matplotlib + seaborn stack
- [x] CLI framework with click
- [x] Sample workout data CSV
- [x] GitHub repository creation and remote setup

### Priority Tasks

**Data Loading Module** (`src/data/`):
- [ ] CSV loader with pandas
  - Parse workout data (date, exercise, sets, reps, weight, RPE)
  - Validate data integrity
  - Handle missing values and data cleaning
- [ ] Data filtering and query functions
  - Filter by exercise, date range, rep ranges
  - Aggregate data for analysis
- [ ] Export loaded data for inspection

**Analysis Module** (`src/analysis/`):
- [ ] 1RM calculation (Epley, Brzycki, Lombardi formulas)
- [ ] Volume calculation (sets × reps × weight)
- [ ] Progressive overload detection
- [ ] Statistical trend analysis (linear regression, moving averages)
- [ ] Periodization detection (volume/intensity phases)

**Visualization Module** (`src/visualization/`):
- [ ] Academic styling configuration
  - 9:16 aspect ratio setup (figsize=(9, 16), dpi=160)
  - Professional color schemes
  - Grid, fonts, and annotation standards
- [ ] Strength progression chart (line plot with trend)
- [ ] Volume tracking chart (bar or area plot)
- [ ] 1RM estimation chart with confidence intervals
- [ ] Multi-exercise comparison plots

**CLI Integration** (`cli/gym_cli.py`):
- [ ] `visualize` command implementation
- [ ] `analyze` command implementation
- [ ] `compare` command implementation
- [ ] Output path handling and validation

---

## Phase 2: Advanced Analytics (PLANNED)

**Goal**: Add sophisticated analysis and multi-metric visualizations

### Planned Features

**Advanced Metrics**:
- [ ] Velocity-based training metrics
- [ ] Fatigue accumulation analysis
- [ ] Deload detection and recommendations
- [ ] Rep range distribution analysis

**Enhanced Visualizations**:
- [ ] Multi-panel comparison charts (2-3 exercises stacked)
- [ ] Heatmaps for volume distribution
- [ ] Periodization timeline with phase annotations
- [ ] Statistical overlays (confidence intervals, std dev bands)

**Data Export**:
- [ ] JSON export of analysis results
- [ ] CSV export of calculated metrics
- [ ] Batch visualization generation

---

## Phase 3: Polish & Optimization (FUTURE)

**Goal**: Production-ready tool with documentation and testing

### Future Enhancements

**Code Quality**:
- [ ] Unit tests for analysis functions
- [ ] Integration tests for end-to-end workflow
- [ ] Code documentation and docstrings
- [ ] Type hints and validation

**User Experience**:
- [ ] Progress bars for batch operations
- [ ] Better error messages and validation
- [ ] Configuration file support (.yml for preferences)
- [ ] Interactive mode with prompts

**Documentation**:
- [ ] User guide with examples
- [ ] API documentation
- [ ] Tutorial notebook (Jupyter)

---

## Technical Decisions & Architecture

### Visualization Tool Selection: matplotlib + seaborn

**Why this stack?**
- **matplotlib**: Publication-quality output, full control, LaTeX support
- **seaborn**: Statistical plotting, clean aesthetics, academic color palettes
- **Proven**: Used in Nature, Science, academic papers worldwide
- **9:16 Support**: Perfect aspect ratio control with `figsize=(9, 16)`

**Alternative Considered**:
- ~~Plotly~~: Too interactive for static PNG output
- ~~bokeh~~: Better for web apps, overkill for our use case

### Data Format: CSV

**Chosen Format**: CSV with predefined columns
**Rationale**: Simple, portable, Excel-compatible, human-readable

**Future Formats**:
- JSON for complex nested data (if needed)
- Direct integration with workout tracking apps (Strong, Hevy, etc.)

### Analysis Formulas

**1RM Calculation** - Will support multiple formulas:
- **Epley**: 1RM = weight × (1 + reps/30)
- **Brzycki**: 1RM = weight × 36 / (37 - reps)
- **Lombardi**: 1RM = weight × reps^0.1

**Volume**: Total volume = Σ(sets × reps × weight)

---

## Documentation Structure

Following the documentation pattern from doll-pantyhose-group:

- **`CLAUDE.md`** - Architecture guidance, setup instructions, Claude Code workflow
  - ✅ Should contain: Project structure, setup commands, architecture overview
  - ❌ Should NOT contain: Current todos, temporary status updates

- **`docs/development.md`** (this file) - Current development priorities only
  - ✅ Should contain: Active todos, technical problems, implementation priorities
  - ❌ Should NOT contain: Completed tasks (tracked in git history)

- **`docs/visualization-guide.md`** (future) - Visualization specifications and examples
  - Style guide for 9:16 academic graphs
  - Color palette documentation
  - Example outputs and best practices

- **`README.md`** - Project overview and quick start
  - ✅ Should contain: High-level overview, quick start, main features
  - ❌ Should NOT contain: Detailed architecture, current development status

---

## Known Issues & Blockers

**None yet** - Project just started

**Future Considerations**:
- Need real workout data for testing (using sample data for now)
- May need to handle different units (lbs vs kg)
- Rep schemes: how to handle cluster sets, drop sets, AMRAP?

---

## Questions for User

- [ ] What specific exercises should we prioritize? (Bench/Squat/Deadlift/OHP?)
- [ ] Preferred unit system? (lbs or kg or both?)
- [ ] Any specific academic papers or visualization styles to emulate?
- [ ] Target platforms beyond TikTok/Xiaohongshu? (Instagram, Twitter?)
