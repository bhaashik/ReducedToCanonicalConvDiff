#!/usr/bin/env python3
"""
Script to create diff-ontology-ver-5.0.json from v4.0 by adding:

Priority 1 (Critical features):
1. PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST - punctuation transformation
2. H-STRUCT, H-TYPE, F-TYPE - headline typology
3. TREE-DEPTH-DIFF - tree complexity
4. CONST-COUNT-DIFF - syntactic complexity
5. DEP-DIST-DIFF - dependency complexity
6. BRANCH-DIFF - branching complexity

Priority 2 (Length features - calculated anyway):
7. TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF - simple length metrics

Based on SCHEMA_GAP_ANALYSIS.md
"""

import json
from pathlib import Path

# Load current schema v4.0
schema_v4_path = Path(__file__).parent / "data" / "diff-ontology-ver-4.0.json"
with open(schema_v4_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Create new features to add

# ===== PRIORITY 1: Critical Features =====

# 1. PUNCT-DEL: Punctuation Deletion
punct_del = {
    "name": "Punctuation Deletion",
    "mnemonic_code": "PUNCT-DEL",
    "group": "lexical/punctuation",
    "description": "Deletion of punctuation marks from the reduced register relative to the canonical.",
    "category": "lexical",
    "parse_types": ["dependency", "constituency"],
    "values": [
        "comma deletion",
        "colon deletion",
        "semicolon deletion",
        "dash deletion",
        "hyphen deletion",
        "period deletion",
        "exclamation mark deletion",
        "question mark deletion",
        "quote deletion",
        "parenthesis deletion",
        "slash deletion",
        "apostrophe deletion"
    ],
    "value_mnemonics": {
        "comma deletion": "COMMA-DEL",
        "colon deletion": "COLON-DEL",
        "semicolon deletion": "SEMICOLON-DEL",
        "dash deletion": "DASH-DEL",
        "hyphen deletion": "HYPHEN-DEL",
        "period deletion": "PERIOD-DEL",
        "exclamation mark deletion": "EXCL-DEL",
        "question mark deletion": "QUEST-DEL",
        "quote deletion": "QUOTE-DEL",
        "parenthesis deletion": "PAREN-DEL",
        "slash deletion": "SLASH-DEL",
        "apostrophe deletion": "APOS-DEL"
    },
    "extra": ["deleted_punctuation", "position", "context"]
}

# 2. PUNCT-ADD: Punctuation Addition
punct_add = {
    "name": "Punctuation Addition",
    "mnemonic_code": "PUNCT-ADD",
    "group": "lexical/punctuation",
    "description": "Addition of punctuation marks in canonical form relative to headline.",
    "category": "lexical",
    "parse_types": ["dependency", "constituency"],
    "values": [
        "comma addition",
        "colon addition",
        "semicolon addition",
        "dash addition",
        "hyphen addition",
        "period addition",
        "exclamation mark addition",
        "question mark addition",
        "quote addition",
        "parenthesis addition",
        "slash addition",
        "apostrophe addition"
    ],
    "value_mnemonics": {
        "comma addition": "COMMA-ADD",
        "colon addition": "COLON-ADD",
        "semicolon addition": "SEMICOLON-ADD",
        "dash addition": "DASH-ADD",
        "hyphen addition": "HYPHEN-ADD",
        "period addition": "PERIOD-ADD",
        "exclamation mark addition": "EXCL-ADD",
        "question mark addition": "QUEST-ADD",
        "quote addition": "QUOTE-ADD",
        "parenthesis addition": "PAREN-ADD",
        "slash addition": "SLASH-ADD",
        "apostrophe addition": "APOS-ADD"
    },
    "extra": ["added_punctuation", "position", "context"]
}

# 3. PUNCT-SUBST: Punctuation Substitution (MOST CRITICAL)
punct_subst = {
    "name": "Punctuation Substitution",
    "mnemonic_code": "PUNCT-SUBST",
    "group": "lexical/punctuation",
    "description": "Substitution between punctuation marks and function words. Headlines use punctuation to compensate for deleted function words (colon for conjunctions, comma for 'and', dash for relative clauses, quotes for reported speech markers).",
    "category": "lexical",
    "parse_types": ["dependency", "constituency"],
    "values": [
        "colon to conjunction",
        "conjunction to colon",
        "comma to conjunction",
        "conjunction to comma",
        "dash to relative clause",
        "relative clause to dash",
        "dash to conjunction",
        "conjunction to dash",
        "semicolon to conjunction",
        "conjunction to semicolon",
        "quote to reported speech",
        "reported speech to quote",
        "comma to preposition",
        "preposition to comma",
        "slash to conjunction",
        "conjunction to slash",
        "slash to disjunction",
        "disjunction to slash",
        "other punctuation substitution"
    ],
    "value_mnemonics": {
        "colon to conjunction": "COLON2CONJ",
        "conjunction to colon": "CONJ2COLON",
        "comma to conjunction": "COMMA2CONJ",
        "conjunction to comma": "CONJ2COMMA",
        "dash to relative clause": "DASH2REL",
        "relative clause to dash": "REL2DASH",
        "dash to conjunction": "DASH2CONJ",
        "conjunction to dash": "CONJ2DASH",
        "semicolon to conjunction": "SEMI2CONJ",
        "conjunction to semicolon": "CONJ2SEMI",
        "quote to reported speech": "QUOTE2RS",
        "reported speech to quote": "RS2QUOTE",
        "comma to preposition": "COMMA2PREP",
        "preposition to comma": "PREP2COMMA",
        "slash to conjunction": "SLASH2CONJ",
        "conjunction to slash": "CONJ2SLASH",
        "slash to disjunction": "SLASH2DISJ",
        "disjunction to slash": "DISJ2SLASH",
        "other punctuation substitution": "PUNCT-SUBST-OTHER"
    },
    "extra": ["source_element", "target_element", "transformation_type", "context"]
}

# 4. H-STRUCT: Headline Structure
h_struct = {
    "name": "Headline Structure",
    "mnemonic_code": "H-STRUCT",
    "group": "register/headline-typology",
    "description": "Overall structural classification of headlines based on discourse complexity.",
    "category": "register",
    "parse_types": ["dependency", "constituency"],
    "values": [
        "single-line",
        "micro-discourse"
    ],
    "value_mnemonics": {
        "single-line": "SG-LINE",
        "micro-discourse": "MICRO-DISC"
    },
    "extra": ["num_sentences", "num_clauses", "length_difference", "tree_depth_diff"],
    "definitions": {
        "single-line": "Single sentence or clause headline (most common type)",
        "micro-discourse": "Multi-sentence or multi-clause headlines with discourse structure, e.g., 'Looking to retire? Want music too? Here's where to go'"
    }
}

# 5. H-TYPE: Headline Type
h_type = {
    "name": "Headline Type",
    "mnemonic_code": "H-TYPE",
    "group": "register/headline-typology",
    "description": "Classification of headlines by completeness of predication.",
    "category": "register",
    "parse_types": ["dependency", "constituency"],
    "values": [
        "fragment",
        "non-fragment"
    ],
    "value_mnemonics": {
        "fragment": "FRAG",
        "non-fragment": "NON-FRAG"
    },
    "extra": ["length_difference", "tree_depth_diff", "has_predicate"],
    "definitions": {
        "fragment": "Incomplete sentence without full predication, e.g., 'Answers for Chakravyuh'",
        "non-fragment": "Complete sentence with full SVO structure, e.g., 'Hospital issues special cards'"
    }
}

# 6. F-TYPE: Fragment Type
f_type = {
    "name": "Fragment Type",
    "mnemonic_code": "F-TYPE",
    "group": "register/headline-typology",
    "description": "Classification of fragment types (only applies when H-TYPE = fragment).",
    "category": "register",
    "parse_types": ["dependency", "constituency"],
    "values": [
        "complex-compound",
        "phrase"
    ],
    "value_mnemonics": {
        "complex-compound": "CMPD",
        "phrase": "PHRASE"
    },
    "extra": ["phrase_type", "length_difference", "tree_depth_diff"],
    "definitions": {
        "complex-compound": "Noun-noun compounds and complex nominals, e.g., 'Dark charm'",
        "phrase": "Phrasal fragments (NP, PP, VP, etc.), e.g., 'A burning issue', 'At his best'"
    }
}

# 7. TREE-DEPTH-DIFF: Tree Depth Difference (PRIORITY 1 - Complexity)
tree_depth_diff = {
    "name": "Tree Depth Difference",
    "mnemonic_code": "TREE-DEPTH-DIFF",
    "group": "structural/complexity",
    "description": "Difference in parse tree depth between canonical and headline forms (both constituency and dependency).",
    "category": "structural",
    "parse_types": ["dependency", "constituency"],
    "values": ["numeric"],
    "value_mnemonics": {"numeric": "DEPTH-DIFF"},
    "extra": ["headline_depth", "canonical_depth", "depth_ratio", "parse_type"]
}

# 8. CONST-COUNT-DIFF: Constituent Count Difference (PRIORITY 1 - Complexity)
constituent_count_diff = {
    "name": "Constituent Count Difference",
    "mnemonic_code": "CONST-COUNT-DIFF",
    "group": "structural/complexity",
    "description": "Difference in number of syntactic constituents between canonical and headline constituency parses.",
    "category": "structural",
    "parse_types": ["constituency"],
    "values": ["numeric"],
    "value_mnemonics": {"numeric": "CONST-CNT-DIFF"},
    "extra": ["headline_constituent_count", "canonical_constituent_count", "reduction_ratio"]
}

# 9. DEP-DIST-DIFF: Dependency Distance Difference (PRIORITY 1 - Complexity)
dep_distance_diff = {
    "name": "Dependency Distance Difference",
    "mnemonic_code": "DEP-DIST-DIFF",
    "group": "structural/complexity",
    "description": "Difference in average dependency distance between canonical and headline dependency parses.",
    "category": "structural",
    "parse_types": ["dependency"],
    "values": ["numeric"],
    "value_mnemonics": {"numeric": "DEP-DIST-DIFF"},
    "extra": ["headline_avg_dep_distance", "canonical_avg_dep_distance", "distance_ratio"]
}

# 10. BRANCHING-FACTOR-DIFF: Branching Factor Difference (PRIORITY 1 - Complexity)
branching_factor_diff = {
    "name": "Branching Factor Difference",
    "mnemonic_code": "BRANCH-DIFF",
    "group": "structural/complexity",
    "description": "Difference in average branching factor between canonical and headline parse trees.",
    "category": "structural",
    "parse_types": ["constituency", "dependency"],
    "values": ["numeric"],
    "value_mnemonics": {"numeric": "BRANCH-DIFF"},
    "extra": ["headline_avg_branching", "canonical_avg_branching", "branching_ratio", "parse_type"]
}

# ===== PRIORITY 2: Simple Length Features =====

# 11. TOKEN-COUNT-DIFF: Token Count Difference (PRIORITY 2 - Simple length)
token_count_diff = {
    "name": "Token Count Difference",
    "mnemonic_code": "TOKEN-COUNT-DIFF",
    "group": "statistical/length",
    "description": "Difference in number of tokens between canonical and headline forms.",
    "category": "statistical",
    "parse_types": ["dependency", "constituency"],
    "values": ["numeric"],
    "value_mnemonics": {"numeric": "TOK-CNT-DIFF"},
    "extra": ["headline_token_count", "canonical_token_count", "reduction_ratio"]
}

# 12. CHAR-COUNT-DIFF: Character Count Difference (PRIORITY 2 - Simple length)
char_count_diff = {
    "name": "Character Count Difference",
    "mnemonic_code": "CHAR-COUNT-DIFF",
    "group": "statistical/length",
    "description": "Difference in character count between canonical and headline forms.",
    "category": "statistical",
    "parse_types": ["dependency", "constituency"],
    "values": ["numeric"],
    "value_mnemonics": {"numeric": "CHAR-CNT-DIFF"},
    "extra": ["headline_char_count", "canonical_char_count", "reduction_ratio"]
}

# Insert new features into schema
features = schema["diff-schema"]["features"]

# Strategy:
# - PUNCT features (3) after FORM-CHG (index 6) → positions 7, 8, 9
# - Headline typology (3) after VERB-FORM-CHG (index 15+3=18) → positions 18, 19, 20
# - Complexity features (4) before TED (index 16+6=22) → positions 21, 22, 23, 24
# - Simple length features (2) at the very end (after current LENGTH-CHG)

# Insert punctuation features after FORM-CHG (position 7)
features.insert(7, punct_del)
features.insert(8, punct_add)
features.insert(9, punct_subst)

# Insert headline typology features after VERB-FORM-CHG (position 18+3=21-3=18)
# VERB-FORM-CHG is at index 15 originally, now at 15+3=18
# Insert after position 18
features.insert(18, h_struct)
features.insert(19, h_type)
features.insert(20, f_type)

# Insert complexity features before TED
# TED was at index 16, now at 16+3+3=22
# Insert at position 21 (before TED)
features.insert(21, tree_depth_diff)
features.insert(22, constituent_count_diff)
features.insert(23, dep_distance_diff)
features.insert(24, branching_factor_diff)

# Append simple length features at the end (after current LENGTH-CHG)
features.append(token_count_diff)
features.append(char_count_diff)

# Update version and changelog
schema["version"] = "5.0.0"
schema["changelog"]["5.0.0"] = "Added critical missing features: Priority 1 - (1) Punctuation features (PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST) to capture punctuation-function word transformations; (2) Headline typology (H-STRUCT, H-TYPE, F-TYPE) for register classification; (3) Structural complexity features (TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF). Priority 2 - Simple length features (TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF) for statistical analysis."
schema["changelog"]["4.0.0"] = "Enriched FEAT-CHG with all morphological features from Stanza: Person, Gender, Definite, PronType, Poss, NumType, NumForm, Polarity, Reflex, Abbr, ExtPos, Foreign. Complete morphosyntactic coverage."

# Write new schema v5.0
output_path = Path(__file__).parent / "data" / "diff-ontology-ver-5.0.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print(f"✅ Created schema v5.0: {output_path}")
print(f"\n📊 Schema Statistics:")
print(f"   Version: {schema['version']}")
print(f"   Total features: {len(features)}")
print(f"\n✨ Priority 1 features added:")
print(f"   Punctuation (3):")
print(f"     1. PUNCT-DEL (position 7)")
print(f"     2. PUNCT-ADD (position 8)")
print(f"     3. PUNCT-SUBST (position 9) - MOST CRITICAL")
print(f"   Headline Typology (3):")
print(f"     4. H-STRUCT (position 18)")
print(f"     5. H-TYPE (position 19)")
print(f"     6. F-TYPE (position 20)")
print(f"   Structural Complexity (4):")
print(f"     7. TREE-DEPTH-DIFF (position 21)")
print(f"     8. CONST-COUNT-DIFF (position 22)")
print(f"     9. DEP-DIST-DIFF (position 23)")
print(f"     10. BRANCH-DIFF (position 24)")
print(f"\n✨ Priority 2 features added (simple length):")
print(f"     11. TOKEN-COUNT-DIFF")
print(f"     12. CHAR-COUNT-DIFF")
print(f"\n📝 Feature count: v4.0 (18) → v5.0 ({len(features)})")
print(f"   - Priority 1: 10 features")
print(f"   - Priority 2: 2 features")
print(f"\n✅ Schema v5.0 created successfully!")
