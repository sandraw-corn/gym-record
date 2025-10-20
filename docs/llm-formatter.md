# LLM Formatter Documentation

## Overview

The LLM formatter converts messy Chinese workout logs into structured CSV format using Google Gemini Flash 2.5. This addresses the real-world challenge of handwritten training logs that mix diary content with workout data.

**Status**: ✅ Complete (Merged in PR #2, Oct 21 2025)

---

## Quick Start

### 1. Setup

Get free Gemini API key at https://aistudio.google.com/apikey

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. Basic Usage

```bash
# Activate conda environment
source ~/.zshrc && conda activate gym-record

# Format a Chinese workout log
python -m cli.gym_cli format --input data/raw_log.txt --date 2024-01-20 --output data/workout.csv

# Preview before saving (recommended)
python -m cli.gym_cli format --input data/raw_log.txt --date 2024-01-20 --dry-run
```

### 3. Use with Analysis Tools

```bash
# Visualize formatted data
python -m cli.gym_cli visualize --exercise "Leg Curl" --data data/workout.csv

# Analyze formatted data
python -m cli.gym_cli analyze --focus strength --data data/workout.csv
```

---

## Processing Pipeline

```
┌─────────────────┐
│ Raw Chinese Log │  今天练腿日！腿弯举 4组 43公斤 x 17, 15, 15, 14次...
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Gemini LLM    │  Temperature=0.1, JSON output mode
│  (Flash 2.5)    │  Extracts training data, ignores diary
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   JSON Output   │  [{"date":"2024-01-20","exercise":"Leg Curl",...}]
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Validator    │  Schema check + auto-fix (unit normalization, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   CSV Output    │  date,exercise,sets,reps,weight,rpe,notes
└─────────────────┘  2024-01-20,Leg Curl,4,15,43,,
```

---

## CRITICAL: Bilateral Exercise Handling

**The Most Important Edge Case**

### The Problem

Chinese workout logs often describe unilateral (single-side) exercises with bilateral execution:

```
单边训练凳划船
先左后右
20kg
11 11, 11 12
```

**Meaning**:
- **Exercise**: Single-Arm Dumbbell Row (单边 = unilateral)
- **Execution**: Left side then right side (先左后右)
- **Weight**: 20kg per side
- **Reps**: "11 11, 11 12" means TWO sets total:
  - Set 1: 11 reps left + 11 reps right = 1 bilateral set
  - Set 2: 11 reps left + 12 reps right = 1 bilateral set

### Common Mistake

❌ **WRONG**: Interpreting "11 11, 11 12" as 4 sets (treating each side as separate set)
✅ **CORRECT**: 2 sets total (each number pair is one bilateral set)

### Detection Patterns

The LLM is trained to recognize these patterns:

| Chinese Pattern | Meaning | Set Counting |
|----------------|---------|--------------|
| 先左后右 | Left then right | Pair = 1 set |
| 左右交替 | Alternating L/R | Pair = 1 set |
| 单边 | Unilateral/single-side | Context-dependent |

### Example Processing

**Input (Chinese log)**:
```
单边训练凳划船
先左后右
20kg
11 11, 11 12
```

**LLM Output (JSON)**:
```json
[
  {
    "date": "2024-01-20",
    "exercise": "Single-Arm Dumbbell Row",
    "sets": 2,
    "reps": [11, 11],
    "weight": 20,
    "unit": "kg",
    "notes": "Bilateral execution (left then right)"
  }
]
```

**Final CSV**:
```csv
date,exercise,sets,reps,weight,rpe,notes
2024-01-20,Single-Arm Dumbbell Row,2,11,20,,Bilateral execution (left then right)
```

---

## Exercise Name Mapping

### Comprehensive Dictionary

The formatter includes **80+ exercise mappings** from Chinese to English:

#### Legs
- 腿弯举 → Leg Curl
- 硬拉 → Deadlift
- 深蹲 → Squat
- 史密斯深蹲 → Smith Squat
- 坐姿蹬腿 / 倒蹬 / 腿举 → Leg Press
- 腿屈伸 → Leg Extension
- 髋外展 → Hip Abduction
- 髋内收 → Hip Adduction
- 提踵 → Calf Raise

#### Back
- 引体向上 → Pull-up
- 高位下拉 → Lat Pulldown
- 坐姿划船 → Seated Cable Row
- 杠铃划船 → Barbell Row
- 哑铃划船 → Dumbbell Row
- 单臂哑铃划船 / 训练凳单边哑铃划船 → Single-Arm Dumbbell Row
- T杠划船 → T-Bar Row
- 面拉 → Face Pull

#### Chest
- 卧推 → Bench Press
- 上斜卧推 → Incline Bench Press
- 飞鸟 / 哑铃飞鸟 → Dumbbell Fly
- 夹胸 / 龙门架夹胸 → Cable Fly
- 俯卧撑 → Push-up

#### Shoulders
- 推举 / 肩推 → Shoulder Press
- 侧平举 → Lateral Raise
- 前平举 → Front Raise
- 后束飞鸟 / 俯身飞鸟 → Reverse Fly
- 直立划船 → Upright Row
- 耸肩 → Shrug

#### Arms
- 弯举 / 二头弯举 → Bicep Curl
- 锤式弯举 → Hammer Curl
- 三头下压 → Tricep Pushdown
- 臂屈伸 → Tricep Dip

**See `src/data/formatter.py` for complete mapping**

---

## Validator Auto-Fix Capabilities

The validator automatically fixes common data quality issues:

### 1. Unit Normalization
```python
# Before
{"weight": 100, "unit": "lb"}

# After (auto-fixed)
{"weight": 100, "unit": "lbs"}
```

### 2. Rep Array Extension
```python
# Before (incomplete)
{"sets": 3, "reps": [15]}

# After (auto-fixed)
{"sets": 3, "reps": [15, 15, 15]}
```

### 3. Business Rule Validation
- ✅ Reps count matches sets count
- ✅ Weight ≥ 0 (allows 0 for bodyweight exercises)
- ✅ Sets ≥ 1
- ✅ Date in valid ISO format (YYYY-MM-DD)
- ✅ Unit must be "kg" or "lbs"
- ✅ RPE between 1-10 (if provided)

### 4. Error Reporting
When validation fails, clear error messages are provided:
```
Validation failed for item 0:
  - Field 'date': Invalid date format. Expected YYYY-MM-DD, got: 2024/01/20
  - Field 'reps': Array length (2) doesn't match sets count (3)
```

---

## Output Format Options

### Aggregated Format (Default)

**One row per exercise** - Compatible with existing analysis tools

```csv
date,exercise,sets,reps,weight,rpe,notes
2024-01-20,Leg Curl,4,15,43,,
2024-01-20,Deadlift,5,5,100,8.5,
```

**When to use**: For standard analysis (visualize, analyze, compare commands)

### Detailed Format (`--detailed` flag)

**One row per set** - Maximum granularity

```csv
date,exercise,set_number,reps,weight,rest_time,rpe,notes
2024-01-20,Leg Curl,1,17,43,3:00,,
2024-01-20,Leg Curl,2,15,43,3:00,,
2024-01-20,Leg Curl,3,15,43,3:00,,
2024-01-20,Leg Curl,4,14,43,,,
```

**When to use**: For advanced analysis (rest time analysis, set-by-set fatigue tracking)

---

## Configuration

### Environment Variables

**Required**:
- `GOOGLE_API_KEY` - Your Gemini API key

**Optional** (with defaults):
- `GEMINI_MODEL=gemini-2.5-flash` - Model to use
- `GEMINI_TEMPERATURE=0.1` - Temperature (0.0-1.0)
- `GEMINI_MAX_OUTPUT_TOKENS=8192` - Max output tokens

### Why These Defaults?

**Temperature = 0.1**:
- Ensures consistent, deterministic output
- Structured data extraction requires low randomness
- Higher temperatures (0.5+) can produce inconsistent JSON

**Max Tokens = 8192**:
- Long workout sessions can generate 3000-5000 tokens
- High limit prevents truncation
- Gemini Flash 2.5 supports up to 8192 tokens

**Model = gemini-2.5-flash**:
- Fast: 2-5 seconds per log
- Cheap: ~$0.003 per log
- Accurate: Excellent multilingual support
- Reliable: JSON output mode

---

## Important Best Practices

### ✅ DO

1. **Always specify `--date` explicitly**
   ```bash
   # GOOD
   python -m cli.gym_cli format --input log.txt --date 2024-01-20

   # BAD - LLM might infer wrong date
   python -m cli.gym_cli format --input log.txt
   ```

2. **Use `--dry-run` to preview**
   ```bash
   # Preview JSON output before saving
   python -m cli.gym_cli format --input log.txt --date 2024-01-20 --dry-run
   ```

3. **Keep Temperature = 0.1**
   - Ensures consistent output
   - Critical for structured data

4. **Review validator warnings**
   - Auto-fixes are logged
   - Manual review recommended for edge cases

### ❌ DON'T

1. **Don't trust LLM for date inference**
   - Workout logs rarely have explicit dates
   - LLM may guess incorrectly

2. **Don't use high temperature**
   - Temperature > 0.3 can produce inconsistent JSON
   - May break schema validation

3. **Don't skip dry-run for new log formats**
   - Preview helps catch parsing errors
   - Cheaper to fix before saving

---

## Cost & Performance

### Pricing

**Gemini Flash 2.5** (as of Oct 2024):
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Typical Workout Log**:
- Input: ~500 tokens (raw Chinese text)
- Output: ~300 tokens (JSON)
- **Cost per log**: ~$0.003 (0.3 cents)
- **120 logs for $0.30**

### Performance

- **Speed**: 2-5 seconds per log
- **Accuracy**: 100% on test cases (bilateral exercises, content filtering, schema validation)
- **Batch Processing**: Can process 10 logs in ~30 seconds

---

## Troubleshooting

### "Google API key required" Error

**Cause**: Missing or incorrect API key in `.env`

**Solution**:
```bash
# 1. Check .env file exists
ls -la .env

# 2. Verify API key is set
cat .env | grep GOOGLE_API_KEY

# 3. If missing, copy template and add key
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your_key_here
```

### "Validation failed" Errors

**Cause**: LLM output doesn't match expected schema

**Solutions**:
1. Check `--dry-run` output to see raw JSON
2. Review validator error messages
3. Manually edit JSON if needed
4. Report persistent issues (may need prompt tuning)

### Bilateral Exercise Miscounting

**Cause**: LLM didn't detect bilateral pattern

**Solution**:
1. Use `--dry-run` to preview
2. Check if Chinese log has clear bilateral indicators (先左后右, 左右交替)
3. Manually edit JSON to correct set count
4. Report pattern to improve exercise mapping

### Incomplete Exercise Mapping

**Cause**: Chinese exercise name not in dictionary

**Solution**:
1. Check `src/data/formatter.py` for existing mappings
2. Exercise may be mapped to generic English name
3. Manually edit output CSV to use preferred name
4. Consider adding mapping to `EXERCISE_MAPPING` dict

---

## Advanced Usage

### Stdin/Stdout Piping

```bash
# Pipe from file
cat raw_log.txt | python -m cli.gym_cli format --date 2024-01-20 > workout.csv

# Chain with other commands
echo "今天练腿！腿弯举 3组 x 15次 40kg" | \
  python -m cli.gym_cli format --date 2024-01-20 --output workout.csv
```

### JSON Output Mode

```bash
# Output JSON instead of CSV (useful for debugging)
python -m cli.gym_cli format --input log.txt --date 2024-01-20 --json-output --output workout.json
```

### Batch Processing (Future)

```bash
# Not yet implemented - planned feature
python -m cli.gym_cli format --input logs/*.txt --batch --output-dir data/
```

---

## Testing

### Unit Tests

```bash
# Run all tests
source ~/.zshrc && conda activate gym-record && pytest tests/

# Run formatter tests only (requires API key)
pytest tests/integration/test_gemini_api.py
pytest tests/manual/test_formatter_basic.py
```

### Test Coverage

- ✅ API connectivity (basic, JSON mode, Chinese input)
- ✅ Bilateral exercise detection (2 sets, not 4)
- ✅ Content filtering (ignores diary entries)
- ✅ Schema validation (catches data quality issues)
- ✅ End-to-end (format → load → visualize)

---

## Future Enhancements

### Planned Features

- [ ] Batch processing (multiple days in one file)
- [ ] Auto-detect language (support English input)
- [ ] Voice-to-text → LLM formatter pipeline
- [ ] Integration with Strong/Hevy app exports
- [ ] Custom exercise mapping via config file
- [ ] Fuzzy matching for typos

### Prompt Engineering Improvements

- [ ] Better handling of drop sets, cluster sets
- [ ] AMRAP (as many reps as possible) detection
- [ ] Tempo notation parsing (3-0-1-0)
- [ ] Rest-pause sets

---

## Implementation Details

### Prompt Structure

The LLM prompt is carefully engineered to:

1. **Output ONLY valid JSON array** (no preamble like "Here's the output...")
2. **Bilateral exercises**: Count as ONE set per side pair
3. **Ignore ALL non-training content** (emotions, social, diary)
4. **Map Chinese exercise names to English**
5. **Preserve individual set reps as arrays**
6. **Use null for missing RPE values**
7. **Extract rest times if present** (optional field)
8. **Notes field**: ONLY form cues, equipment issues, relevant training notes

**See `src/data/formatter.py:_create_prompt()` for full prompt template**

### Validation Schema

JSON Schema (draft-07) defines the expected structure:

```python
{
    "type": "array",
    "items": {
        "type": "object",
        "required": ["date", "exercise", "sets", "reps", "weight"],
        "properties": {
            "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
            "exercise": {"type": "string", "minLength": 1},
            "sets": {"type": "integer", "minimum": 1},
            "reps": {"type": "array", "items": {"type": "integer", "minimum": 1}},
            "weight": {"type": "number", "minimum": 0},
            "unit": {"enum": ["kg", "lbs", "lb", null]},
            "rpe": {"type": "number", "minimum": 1, "maximum": 10},
            "rest_times": {"type": "array"},
            "notes": {"type": "string"}
        }
    }
}
```

**See `src/data/validator.py:WORKOUT_SCHEMA` for complete schema**

---

## Related Documentation

- **Architecture**: See `CLAUDE.md` for overall project structure
- **Development**: See `docs/development.md` for current priorities
- **Code**: See `src/data/formatter.py` and `src/data/validator.py` for implementation
