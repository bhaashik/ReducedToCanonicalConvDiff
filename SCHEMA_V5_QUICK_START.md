# Schema v5.0 Quick Start Guide

**Status**: ✅ Schema created and ready to use
**Date**: January 2, 2026

---

## What Was Done

✅ **Created schema v5.0** with 12 new features (18 → 30 total)
- 3 punctuation features (PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST) ⭐ **CRITICAL**
- 3 headline typology features (H-STRUCT, H-TYPE, F-TYPE)
- 4 structural complexity features (TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF)
- 2 simple length features (TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF)

✅ **Created comprehensive documentation**:
- `SCHEMA_GAP_ANALYSIS.md` - Gap analysis (updated with resolution)
- `SCHEMA_CHANGELOG_v5.0.md` - Complete changelog
- `SCHEMA_V5_IMPLEMENTATION_SUMMARY.md` - Detailed implementation notes
- `SCHEMA_V5_QUICK_START.md` - This quick start guide

---

## Files Created

```
data/diff-ontology-ver-5.0.json           ← NEW SCHEMA (30 features)
create_schema_v5_0.py                     ← Generation script
SCHEMA_CHANGELOG_v5.0.md                  ← Complete documentation
SCHEMA_V5_IMPLEMENTATION_SUMMARY.md       ← Implementation details
SCHEMA_V5_QUICK_START.md                  ← This file
SCHEMA_GAP_ANALYSIS.md                    ← Updated with resolution status
```

---

## How to Use Schema v5.0

### Step 1: Update Schema Path

**Check which schema is currently being used**:
```bash
grep -r "diff-ontology" register_comparison/meta_data/schema.py
```

**Option A - Update paths_config.py** (if that's what the pipeline uses):
```python
# In paths_config.py, line 75:
SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-5.0.json"  # Changed from 3.0
```

**Option B - Update schema loader directly** (if pipeline loads schema elsewhere):
Find the file that loads the schema and update the path.

**Option C - Rename v5.0 to current version** (quick test):
```bash
cp data/diff-ontology-ver-4.0.json data/diff-ontology-ver-4.0-backup.json
cp data/diff-ontology-ver-5.0.json data/diff-ontology-ver-4.0.json
```

### Step 2: Run Pipeline

**Test with single newspaper first**:
```bash
# Edit register_comparison/compare_registers.py line 233 to select newspaper
python register_comparison/compare_registers.py
```

**Run for all newspapers**:
```bash
python run_task1_all_newspapers.py
```

### Step 3: Verify New Features

**Check output for new feature events**:
```bash
# Look for punctuation events
head -50 output/Times-of-India/events_global.csv | grep "PUNCT"

# Look for headline typology
head -50 output/Times-of-India/events_global.csv | grep "H-STRUCT\|H-TYPE\|F-TYPE"

# Look for complexity metrics
head -50 output/Times-of-India/events_global.csv | grep "DEPTH-DIFF\|COUNT-DIFF\|DIST-DIFF"
```

**Check feature frequencies**:
```bash
grep "PUNCT\|H-STRUCT\|H-TYPE\|F-TYPE" output/Times-of-India/feature_freq_global.csv
```

---

## Expected New Results

### Punctuation Events (Example)

**Input**:
- Headline: `Modi in US: Discusses trade`
- Canonical: `Modi is in the US and discusses trade`

**Expected Events**:
```
PUNCT-SUBST,colon to conjunction,COLON2CONJ
FW-ADD,article addition,the
FW-ADD,auxiliary addition,is
```

### Headline Typology (Example)

**Fragment Headline**: `Answers for Chakravyuh`
```
H-STRUCT,single-line,SG-LINE
H-TYPE,fragment,FRAG
F-TYPE,phrase,PHRASE
```

**Complete Headline**: `Hospital issues special cards`
```
H-STRUCT,single-line,SG-LINE
H-TYPE,non-fragment,NON-FRAG
```

### Complexity Metrics (Example)

```
TREE-DEPTH-DIFF,numeric,DEPTH-DIFF,{"headline_depth": 4, "canonical_depth": 6}
CONST-COUNT-DIFF,numeric,CONST-CNT-DIFF,{"reduction_ratio": 0.67}
DEP-DIST-DIFF,numeric,DEP-DIST-DIFF,{"distance_ratio": 0.75}
```

---

## Troubleshooting

### Problem: "Schema not found" error
**Solution**: Check that `data/diff-ontology-ver-5.0.json` exists and path is correct

### Problem: No new features in output
**Solutions**:
1. Verify schema was loaded: Add debug print in schema loader
2. Check if extractor is schema-aware: Look at `register_comparison/extractors/extractor.py`
3. Verify data has punctuation: Check raw headline files for colons, commas, dashes

### Problem: Pipeline crashes
**Solutions**:
1. Test with small sample (10-20 pairs)
2. Check error message for feature-specific issues
3. Verify all 30 features have proper structure in schema
4. Fall back to v4.0 and report issue

---

## Quick Validation Checklist

After running pipeline:

- [ ] Pipeline completes without errors
- [ ] Output CSV files are generated
- [ ] New features appear in `feature_freq_global.csv`
- [ ] Punctuation events detected (grep "PUNCT")
- [ ] Headline typology assigned (grep "H-TYPE")
- [ ] Complexity metrics computed (grep "DIFF")
- [ ] Total feature count is 30 (not 18)
- [ ] No unexpected warnings in logs

---

## Documentation

### For detailed information, see:

1. **SCHEMA_CHANGELOG_v5.0.md**
   - Complete feature specifications
   - All 12 new features with values
   - Backward compatibility notes

2. **SCHEMA_V5_IMPLEMENTATION_SUMMARY.md**
   - Implementation details
   - Testing recommendations
   - Success criteria

3. **SCHEMA_GAP_ANALYSIS.md**
   - Why these features were needed
   - Original gap identification
   - Resolution status

### For implementation help:

- Feature extraction: `register_comparison/extractors/extractor.py`
- Schema loading: `register_comparison/meta_data/schema.py`
- Pipeline: `register_comparison/compare_registers.py`

---

## Key Points to Remember

1. **Backward Compatible**: All v4.0 features unchanged, v5.0 is purely additive
2. **Most Critical**: PUNCT-SUBST captures punctuation ↔ function word substitution
3. **Parse Requirements**: Some features need dependency parses, others need constituency
4. **Validation Required**: Manually check sample outputs after first run

---

## Next Actions

1. ✅ Schema created (DONE)
2. ⏳ Update schema path in pipeline
3. ⏳ Run pipeline with v5.0
4. ⏳ Verify new features detected
5. ⏳ Validate with sample data
6. ⏳ Run full analysis on all newspapers
7. ⏳ Update research papers with new findings

**Current Step**: Step 2 (Update schema path)

---

## Quick Commands

```bash
# Find where schema is loaded
grep -r "SCHEMA_PATH\|schema.json" register_comparison/*.py

# Test schema loads correctly
python -c "from register_comparison.meta_data.schema import FeatureSchema; s = FeatureSchema('data/diff-ontology-ver-5.0.json'); print(f'Features: {len(s.features)}')"

# Run single newspaper test
python register_comparison/compare_registers.py

# Run all newspapers
python run_task1_all_newspapers.py

# Check results
ls -lh output/Times-of-India/*.csv
```

---

**Need Help?** Check the error logs and refer to `SCHEMA_V5_IMPLEMENTATION_SUMMARY.md` for detailed troubleshooting.

---

✅ **Schema v5.0 is ready to use!**
