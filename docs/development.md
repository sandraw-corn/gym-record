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

## Parallel Development: LLM Input Formatter (NEW TRACK)

**Branch**: `feat/llm-formatter`
**Status**: Planned - independent from Phase 1
**Goal**: Convert messy, conversational Chinese training logs to structured CSV format

### Problem Statement

**Current Reality**: Training logs are naturally messy
- Mixed language (Chinese exercises, English notes)
- Conversational style with diary entries, emotions, social interactions
- Complex formatting: "单边训练凳划船 先左后右 11 11, 11 12" = 2 sets (bilateral), not 4
- Embedded metadata: rest times, form notes, RPE feelings
- Inconsistent structure between different workout days

**Goal**: Automatic preprocessing that extracts ONLY training data, ignoring diary content

### Architecture

```
src/data/
├── formatter.py         # NEW: LLM-based formatter using Gemini Flash 2.5
├── loader.py           # Existing: Loads formatted CSV
└── validator.py        # NEW: Validates LLM output schema
```

**Pipeline Flow**:
```
Raw Chinese Log → LLM Formatter → JSON → Validator → CSV → Data Loader
```

### Technical Design

**LLM Choice**: Google Gemini Flash 2.5
- Fast and cheap for preprocessing
- Excellent multilingual support (Chinese → English)
- Structured output support (JSON mode)
- Good at understanding context (bilateral exercises, set counting)

**Key Parsing Challenges**:
1. **Bilateral exercises**: "先左后右" = left then right = ONE set, not two
   - Example: "11 11, 11 12" with bilateral = 2 sets total
2. **Mixed content**: Extract training data, ignore diary/emotions/social notes
3. **Exercise name mapping**: 腿弯举 → Leg Curl, 硬拉 → Deadlift
4. **Weight units**: Handle both kg and lbs, standardize
5. **Rep arrays**: Preserve individual set reps [17, 15, 15] not just average
6. **Form notes**: "cheat from rep 10" → goes to notes field

**Output Schema** (JSON intermediate format):
```json
[
  {
    "date": "YYYY-MM-DD",
    "exercise": "Exercise Name (English)",
    "sets": 3,
    "reps": [17, 15, 15],
    "weight": 43,
    "unit": "kg",
    "rpe": 8.5,
    "rest_times": ["3:00", "3:15", "4:00"],
    "notes": "Brief relevant training notes only"
  }
]
```

**Validation Requirements**:
- All required fields present: date, exercise, sets, reps, weight
- Reps array length matches sets count
- Weight > 0, sets > 0
- Date in valid ISO format
- Unit must be "kg" or "lbs"

### Implementation Tasks

**Phase 1: Core Formatter** (`src/data/formatter.py`):
- [ ] Gemini API integration with JSON output mode
- [ ] Prompt engineering for Chinese log parsing
- [ ] Exercise name mapping dictionary (Chinese → English)
- [ ] Handle bilateral exercise detection ("先左后右", "左右交替")
- [ ] Extract training data, filter out diary content
- [ ] Temperature = 0.1 for consistency

**Phase 2: Validation** (`src/data/validator.py`):
- [ ] JSON schema validation
- [ ] Field type checking (dates, numbers, arrays)
- [ ] Cross-field validation (reps array length = sets count)
- [ ] Unit standardization
- [ ] Error reporting with line numbers

**Phase 3: CLI Integration**:
- [ ] `format` command: convert raw text to CSV
  ```bash
  python -m cli.gym_cli format --input raw_log.txt --output data/formatted.csv
  ```
- [ ] Support stdin pipe: `cat log.txt | python -m cli.gym_cli format > output.csv`
- [ ] Date parameter: `--date 2024-01-15` (override LLM inference)
- [ ] Dry-run mode: preview JSON before writing CSV

**Phase 4: Exercise Mapping**:
- [ ] Comprehensive Chinese → English exercise dictionary
- [ ] Support for variations: "腿弯举" = "Leg Curl" = "Hamstring Curl"
- [ ] User-defined mappings via config file
- [ ] Fuzzy matching for typos

### Prompt Engineering Strategy

**Core Prompt Requirements**:
```
1. Output ONLY valid JSON array, NO preamble ("Here's the output...")
2. Bilateral exercises: Count as ONE set per side pair
3. Ignore ALL non-training content (emotions, social, diary)
4. Map Chinese exercise names to English
5. Preserve individual set reps as arrays
6. Use null for missing RPE values
7. Extract rest times if present (optional field)
8. Notes field: ONLY form cues, equipment issues, relevant training notes
```

**Example Mapping**:
```python
EXERCISE_MAPPING = {
    "腿弯举": "Leg Curl",
    "硬拉": "Deadlift",
    "髋外展": "Hip Abduction",
    "史密斯深蹲": "Smith Squat",
    "坐姿蹬腿": "Leg Press",
    "训练凳单边哑铃划船": "Single-Arm Dumbbell Row",
    "高位下拉": "Lat Pulldown",
    "坐姿划船": "Seated Cable Row",
    # ... comprehensive mapping
}
```

**Bilateral Detection Patterns**:
- "先左后右" = left then right
- "左右交替" = alternating left/right
- "单边" = unilateral (single side)

### Integration with Existing Pipeline

**Workflow**:
```bash
# Step 1: Format raw log
python -m cli.gym_cli format --input raw_notes.txt --output data/2024-01-15.csv --date 2024-01-15

# Step 2: Use existing tools
python -m cli.gym_cli visualize --exercise "Deadlift" --metric strength
```

**API Key Management**:
- Use `.env` file (git ignored)
- Environment variable: `GEMINI_API_KEY`
- Graceful fallback if key missing (manual formatting instructions)

### Design Decisions

**Q: Keep Chinese or translate to English?**
**A**: Translate to English for consistency, preserve Chinese in notes if needed

**Q: Rep arrays vs averages?**
**A**: Keep arrays `[17, 15, 15]` - more data = better progressive overload analysis

**Q: Date extraction from LLM or parameter?**
**A**: Require explicit `--date` parameter, don't trust LLM inference for dates

**Q: Handle rest times?**
**A**: Extract as optional field, not required for MVP (useful for future analysis)

**Q: Error handling for ambiguous logs?**
**A**: Validator flags issues, requires manual review before import

### Testing Strategy

**Test Cases**:
1. **Bilateral exercises**: Verify set counting is correct
2. **Mixed content**: Diary entries completely filtered out
3. **Exercise variants**: Different names map to same canonical exercise
4. **Edge cases**: Failed sets, drop sets, AMRAP, cluster sets
5. **Validation**: Invalid JSON rejected, missing fields caught

**Test Data**: Use real anonymized logs from user

### Future Enhancements

- [ ] Batch processing: multiple days in one file
- [ ] Auto-detect language (support English input too)
- [ ] Export metadata: form notes, PRs, training insights separately
- [ ] Integration with Strong/Hevy app exports
- [ ] Voice-to-text → LLM formatter pipeline (record workout verbally)

### Dependencies

**New Requirements** (add to `requirements.txt`):
```
google-generativeai>=0.3.0  # Gemini API
python-dotenv>=1.0.0        # .env file support
jsonschema>=4.17.0          # JSON validation
```

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
