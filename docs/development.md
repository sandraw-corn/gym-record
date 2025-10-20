# Development Roadmap & Priorities

## 🎯 Current Development Focus

**Current Phase**: Smart Date Detection for Workout Logs
**Status**: Directory structure created, now implementing intelligent date inference

**Goal**: Automatic date detection from multiple sources with smart year inference and user-friendly conflict resolution

---

## Active Development: Smart Date Detection

**Branch**: `feat/smart-date-detection`
**Status**: Design phase

### Implementation Plan

**Date Priority System** (with conflict resolution):
- [ ] Priority 1: `--date` flag (explicit user override)
  - If conflicts with filename/note → warn user
- [ ] Priority 2: Filename parsing (e.g., `2024-10-14.txt`)
  - Extract date from filename using regex
  - Validate date format
- [ ] Priority 3: Note content extraction (LLM-based)
  - Parse Chinese date patterns: "10月14日", "2024年10月14日"
  - Smart year inference (default to 2025/current year)
  - Detect future dates and suggest previous year
- [ ] Priority 4: No date found → ERROR (fail safely)

**Year Auto-Detection**:
- [ ] Default to current year (2025) for "10月14日" format
- [ ] Parse explicit years: "2024年10月14日" → 2024
- [ ] Smart future date detection (if >30 days future → suggest previous year)
- [ ] Handle edge case: December workout logged in January

**Mismatch Handling** (CRITICAL):
- [ ] Detect filename vs note content mismatch
- [ ] **STOP and prompt user** for choice (never auto-pick)
- [ ] Interactive menu:
  - [1] Use filename date
  - [2] Use note content date
  - [3] Specify manually
  - [q] Quit and fix manually
- [ ] Log chosen date and source for audit trail

**Implementation Details**:
- [ ] Add `extract_date_from_filename()` helper
- [ ] Update LLM prompt with explicit Chinese date patterns
- [ ] Add `resolve_date_conflict()` interactive resolver
- [ ] Update CLI help text to explain date priority
- [ ] Add validation warnings (don't silently proceed on ambiguity)

**Testing**:
- [ ] Test filename parsing: `2024-10-14.txt`, `2024-10-14_legs.txt`
- [ ] Test Chinese date extraction: "10月14日", "2024年10月14日"
- [ ] Test year inference: December date in January
- [ ] Test conflict resolution: filename ≠ note content
- [ ] Test error handling: no date found anywhere

---

## Known Issues & Pain Points

### Data Aggregation Problem (CRITICAL)

**Current Problem**: Manual CSV concatenation required for multi-workout analysis

**Current Workflow** (painful):
```bash
# User must manually concatenate CSVs for analysis
cat data/formatted/2025-10-08.csv > data/all_workouts.csv
tail -n +2 data/formatted/2025-10-14.csv >> data/all_workouts.csv
tail -n +2 data/formatted/2025-10-19.csv >> data/all_workouts.csv

# Then analyze
python -m cli.gym_cli analyze --data data/all_workouts.csv
```

**Why This Sucks**:
- ❌ Manual process every time you add new workout
- ❌ Easy to forget to update `all_workouts.csv`
- ❌ No single source of truth
- ❌ Can't query "show me all leg workouts" without manual filtering
- ❌ No way to track which files are included
- ❌ Breaks when you have 50+ workout files

**Proposed Solutions**:

#### Option 1: Automatic CSV Aggregation
```bash
# CLI automatically loads all CSVs in data/formatted/
python -m cli.gym_cli analyze --focus strength
# → Automatically scans data/formatted/*.csv

# Or explicit directory
python -m cli.gym_cli analyze --data-dir data/formatted/
```

**Pros**: Simple, no new dependencies
**Cons**: Still CSV-based, no querying capability

#### Option 2: SQLite Database (Recommended)
```bash
# Import formatted CSVs to local SQLite database
python -m cli.gym_cli db import --input data/formatted/2025-10-08.csv

# Analyze from database
python -m cli.gym_cli analyze --focus strength
# → Queries: SELECT * FROM workouts WHERE date >= '2025-10-01'

# Batch import
python -m cli.gym_cli db import --dir data/formatted/
```

**Pros**:
- ✅ Single source of truth
- ✅ SQL queries (filter by date, exercise, rep range)
- ✅ No manual concatenation
- ✅ Track import history
- ✅ Efficient for large datasets

**Cons**: Adds SQLite dependency (but it's in Python stdlib)

#### Option 3: PostgreSQL (Overkill for now)
- Full-featured database
- Better for multi-user or web app
- Too heavy for single-user CLI tool

**Decision**: Implement **Option 2 (SQLite)** in separate branch `feat/database-backend`

**Implementation Plan**:
- [ ] Create SQLite schema (workouts table, metadata table)
- [ ] Add `db import` command (CSV → SQLite)
- [ ] Add `db list` command (show imported workouts)
- [ ] Update `analyze`, `visualize`, `compare` to use SQLite by default
- [ ] Keep CSV output as export option
- [ ] Add migration tool: existing CSVs → SQLite

**Database Schema (Draft)**:
```sql
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    exercise TEXT NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight REAL NOT NULL,
    rpe REAL,
    notes TEXT,
    rest_times TEXT, -- JSON array
    source_file TEXT, -- original filename
    imported_at TIMESTAMP,
    UNIQUE(date, exercise, sets, reps, weight) -- prevent duplicates
);

CREATE TABLE import_history (
    id INTEGER PRIMARY KEY,
    source_file TEXT NOT NULL,
    imported_at TIMESTAMP,
    records_imported INTEGER
);
```

---

## Planned Features

### Batch Processing & Workflow Automation

**Branch**: `feat/batch-processing` (future)
**Goal**: Process multiple workout logs efficiently with tracking

**Features**:
- [ ] Batch format all files in `data/raw/` that haven't been formatted
  ```bash
  python -m cli.gym_cli format --batch
  ```
- [ ] Track formatting history to avoid re-formatting
  - Store manifest: `data/.format_history.json` (git-ignored)
  - Record: source file, output file, date used, date source, timestamp
- [ ] Smart output path inference
  - `data/raw/2024-10-14.txt` → `data/formatted/2024-10-14.csv` (auto)
- [ ] Dry-run mode for batch: preview all operations before execution
- [ ] Progress bars for batch operations
- [ ] Error recovery: continue on failure, report summary at end

**Design Considerations**:
- Avoid re-formatting already processed files (check manifest)
- Warn if source file modified after formatting
- Allow force re-format with `--force` flag
- Smart date detection applies to each file individually

### Visualization Enhancements

**Branch**: `feat/viz-improvements` (future)
**Goal**: Dark mode, better readability, richer analysis for social media

**Dark Mode & Styling**:
- [ ] Implement dark background themes (better for night viewing on mobile)
- [ ] Increase font sizes for better readability on mobile
- [ ] Larger data point markers/nodes for clarity
- [ ] Improve color schemes for dark backgrounds
- [ ] High-contrast color palettes optimized for OLED displays

**Composed Analysis & Rich Visualizations**:
- [ ] Add multi-metric panels (strength + volume on same chart)
- [ ] Statistical annotations (average, trend, % change)
- [ ] Progressive overload indicators (visual markers when records broken)
- [ ] Periodization phase annotations on timeline
- [ ] Confidence intervals and statistical significance markers

**Readability Enhancements**:
- [ ] Larger axis labels and titles
- [ ] Bold trend lines with better contrast
- [ ] Clearer legend placement and sizing
- [ ] Grid styling optimized for dark backgrounds
- [ ] Better spacing and margins for mobile screens

---

## Phase 1: Core Foundation ✅ COMPLETE

**Merged**: PR #1 (Oct 21, 2025)
**Test Coverage**: 86/86 tests passing, 94% coverage

**Implemented Features**:
- Data loading module with CSV parsing, filtering, and validation
- Analysis metrics: 1RM calculations, volume tracking, progressive overload detection
- Visualization module with 9:16 aspect ratio charts
- CLI commands: `visualize`, `analyze`, `compare`, `list-data`
- Complete test suite (73 unit + 13 integration tests)

**See**: Git history and PR #1 for implementation details

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

## LLM Formatter ✅ COMPLETE

**Merged**: PR #2 (Oct 21, 2025)
**Test Coverage**: 93/93 tests passing (100% pass rate)

**Implemented Features**:
- LLM-based formatter using Google Gemini Flash 2.5
- 80+ exercise mappings (Chinese → English)
- Bilateral exercise detection ("先左后右" = 1 set, not 2)
- JSON schema validation with auto-fix capabilities
- CLI `format` command with dual output modes (aggregated/detailed)
- Full integration with existing analysis pipeline

**See**: Git history and PR #2 for implementation details

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
