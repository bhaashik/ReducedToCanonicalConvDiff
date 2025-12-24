# Cross-Newspaper Comparative Analysis Report
## Task 1: Register Differences Analysis (v4.0 Schema)

**Generated:** 2025-12-23 15:57:35
**Schema Version:** 4.0 (20 morphological features)
**Newspapers Analyzed:** Times-of-India, Hindustan-Times, The-Hindu

---

## Executive Summary

This report presents a comprehensive comparative analysis of morphosyntactic differences between **reduced register (headlines)** and **canonical register (full sentences)** across three major Indian English newspapers.

### Total Events Detected

| Newspaper | Total Events | Percentage |
|-----------|-------------|-----------|
| Times-of-India | 33,525 | 35.3% |
| Hindustan-Times | 39,998 | 42.1% |
| The-Hindu | 21,381 | 22.5% |
| **TOTAL** | **94,907** | **100.0%** |

---

## 1. Feature Diversity Analysis

**Shannon Entropy** measures the diversity of register differences. Higher values indicate more varied transformation patterns.

| Newspaper | Entropy (bits) | Interpretation |
|-----------|----------------|----------------|
| Times-of-India | 2.819 | Lower Diversity |
| Hindustan-Times | 2.840 | Lower Diversity |
| The-Hindu | 3.195 | Moderate Diversity |

---

## 2. Top 15 Features Globally

| Rank | Feature ID | Total Events | Description |
|------|-----------|--------------|-------------|
| 1 | CONST-MOV | 30,289 | - |
| 2 | DEP-REL-CHG | 26,935 | - |
| 3 | CLAUSE-TYPE-CHG | 7,636 | - |
| 4 | FW-DEL | 7,112 | - |
| 5 | TED-RTED | 3,316 | - |
| 6 | LENGTH-CHG | 3,276 | - |
| 7 | TED-SIMPLE | 3,234 | - |
| 8 | TED-ZHANG-SHASHA | 2,713 | - |
| 9 | TED-KLEIN | 2,713 | - |
| 10 | C-DEL | 2,572 | - |
| 11 | C-ADD | 1,430 | - |
| 12 | CONST-REM | 1,008 | - |
| 13 | HEAD-CHG | 760 | - |
| 14 | FW-ADD | 485 | - |
| 15 | FEAT-CHG | 408 | - |

---

## 3. Feature Coverage Across Newspapers

Features appearing in all vs. subset of newspapers:

- **Universal Features** (in all 3 newspapers): 21 features
- **Partial Features** (in 2 newspapers): 0 features
- **Unique Features** (in 1 newspaper): 1 features


---

## 4. Parse Type Distribution

| Newspaper | Dependency Parse Events | Constituency Parse Events |
|-----------|------------------------|---------------------------|
| Times-of-India | 15,253 | 18,272 |
| Hindustan-Times | 19,051 | 20,947 |
| The-Hindu | 9,362 | 12,019 |

---

## 5. Top Features by Newspaper

### Times-of-India

| Rank | Feature ID | Count | % of Newspaper Total |
|------|-----------|-------|---------------------|
| 1 | CONST-MOV | 11,485 | 34.3% |
| 2 | DEP-REL-CHG | 9,892 | 29.5% |
| 3 | CLAUSE-TYPE-CHG | 2,728 | 8.1% |
| 4 | FW-DEL | 2,241 | 6.7% |
| 5 | TED-RTED | 1,035 | 3.1% |

### Hindustan-Times

| Rank | Feature ID | Count | % of Newspaper Total |
|------|-----------|-------|---------------------|
| 1 | CONST-MOV | 13,099 | 32.7% |
| 2 | DEP-REL-CHG | 11,759 | 29.4% |
| 3 | CLAUSE-TYPE-CHG | 3,408 | 8.5% |
| 4 | FW-DEL | 3,210 | 8.0% |
| 5 | C-DEL | 1,405 | 3.5% |

### The-Hindu

| Rank | Feature ID | Count | % of Newspaper Total |
|------|-----------|-------|---------------------|
| 1 | CONST-MOV | 5,705 | 26.7% |
| 2 | DEP-REL-CHG | 5,284 | 24.7% |
| 3 | FW-DEL | 1,661 | 7.8% |
| 4 | CLAUSE-TYPE-CHG | 1,500 | 7.0% |
| 5 | TED-RTED | 1,139 | 5.3% |

---

## 6. Key Findings

### Morphological Feature Changes (FEAT-CHG)

The v4.0 schema captures **20 morphological features**:
- **Original 7**: Tense, Number, Aspect, Voice, Mood, Case, Degree
- **NEW 13**: Person, Gender, Definite, PronType, Poss, NumType, NumForm, Polarity, Reflex, VerbForm, Abbr, ExtPos, Foreign

**Total FEAT-CHG events across all newspapers**: 408

- Times-of-India: 160 morphological feature changes
- Hindustan-Times: 126 morphological feature changes
- The-Hindu: 122 morphological feature changes


### Register-Specific Patterns

1. **Function Word Deletion (FW-DEL)**: Most common transformation indicating headline compression
2. **Dependency Relation Changes (DEP-REL-CHG)**: Syntactic restructuring for brevity
3. **Constituent Movement (CONST-MOV)**: Word order changes for emphasis
4. **Clause Type Changes (CLAUSE-TYPE-CHG)**: Finite to non-finite transformations

---

## 7. Statistical Significance

See individual newspaper outputs for detailed chi-square and Fisher exact tests.

---

## Conclusion

This cross-newspaper analysis reveals **systematic morphosyntactic differences** between headline and canonical registers across all three newspapers, with variations in:
- Event frequency
- Feature diversity
- Transformation patterns

The enriched v4.0 schema with 20 morphological features provides comprehensive coverage of register differences.

---

**Next Steps:**
- ✅ Task 1 completed: Comparative analysis across all newspapers
- ⏭️ Task 2: Transformation study with rule extraction
- ⏭️ Task 3: Complexity & similarity analysis

