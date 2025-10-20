# Development Roadmap & Priorities

## 🎯 Current Development Focus

**Current Phase**: Visualization Enhancement & Dark Mode
**Status**: Core foundation complete (PR #1 merged), now improving charts for better social media presentation

**Goal**: Optimize visualizations for night viewing with dark themes, larger fonts, better readability, and more in-depth composed analysis

---

## Active Development: Visualization Improvements

**Branch**: TBD (to be created)
**Status**: Planning phase

### Priority Improvements

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
