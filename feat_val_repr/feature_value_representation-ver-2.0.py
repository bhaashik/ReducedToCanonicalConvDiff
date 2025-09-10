import csv
import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

# -------- Mnemonic Linguistic Feature-to-Principle Mapping --------

# Example compressed tagset: map short tags to full linguistic principle explanations.
# This can be updated programmatically by calling add_feature_mapping.
feature_to_principle_map = {
    "FW-DEL": "Function Word Omission: Telegrapic style, reduced register; e.g., determiner, auxiliary omission.",
    "TOKEN-REORDER": "Token Reordering: Information structure shift; topicalization and focus marking.",
    "FORM-CHG": "Form Change: Morphosyntactic simplification; nominalizations and part-of-speech shifts.",
    "LEMMA-CHG": "Lemma Change: Lexical selection and register variation.",
    "POS-CHG": "POS Change: Structural class shifting emphasizing headline brevity.",
    "FEAT-CHG": "Feature Change: Morphological economy, tense/aspect simplification.",
    "DEP-REL-CHG": "Dependency Relation Change: Syntactic simplification and foregrounding.",
    "CONST-REM": "Constituent Removal: Phrase structure compression, omitted subordinate clauses / adjuncts.",
    "WORD-REM": "Word Removal: Token deletion of content/function words; corresponds to ellipsis.",
    "WORD-ADD": "Word Addition: Tokens present in canonical only; fuller expression.",
    "TED": "Tree Edit Distance: Global structural divergence metric.",
}

def add_feature_mapping(tag: str, description: str):
    """Add or update feature-to-principle mapping with short mnemonic tag."""
    feature_to_principle_map[tag] = description

def get_principle_description(tag: str) -> str:
    """Retrieve principle description for a mnemonic tag."""
    return feature_to_principle_map.get(tag, "Unknown Feature")

# -------- Load and Aggregate Examples --------

def load_local_events(file_path: str) -> List[Dict]:
    """Load local events from CSV into dict list."""
    with open(file_path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def aggregate_examples(events: List[Dict], relevant_fields: List[str], group_by: str) -> Dict[str, Dict]:
    """
    Aggregate example frequencies grouped by event type.

    Params:
        events: list of dict rows from CSV
        relevant_fields: list of fields containing example textual data (e.g., form, lemma)
        group_by: column name to group examples by (usually 'event_type')

    Returns:
        Dict[event_type, Dict[example_text, count]]
    """
    agg = defaultdict(lambda: defaultdict(int))
    for ev in events:
        evt_type = ev.get(group_by)
        if not evt_type:
            continue
        # Compose an example key by joining relevant fields, ignore empty strings
        example_key = "; ".join(ev[field] for field in relevant_fields if ev.get(field))
        agg[evt_type][example_key] += 1
    return agg

def format_examples(example_counts: Dict[str, int], max_examples=5) -> List[Tuple[str, int]]:
    """Return top-N (example, count) sorted descending."""
    counter = Counter(example_counts)
    return counter.most_common(max_examples)

# -------- Report Generation --------

def generate_feature_report(dep_example_file: str, const_example_file: str, max_examples=5) -> str:
    """
    Generate a human-readable report linking feature examples with principles.

    Params:
        dep_example_file: Path to dependency local events CSV
        const_example_file: Path to constituency local events CSV
        max_examples: max examples per event to show

    Returns:
        Formatted multiline string report.
    """
    dep_events = load_local_events(dep_example_file)
    const_events = load_local_events(const_example_file)

    # These fields contain info relevant for examples — adjust as needed
    dep_fields = ["form", "lemma", "upos"]
    const_fields = ["word/constituent", "pos_label"]

    dep_agg = aggregate_examples(dep_events, dep_fields, "event_type")
    const_agg = aggregate_examples(const_events, const_fields, "event_type")

    report_lines = []
    report_lines.append("=== Data-Driven Feature-to-Principle Mapping Report ===\n")

    # Process dependency event features
    report_lines.append("== Dependency Parse Features ==")
    for evt_type, examples in sorted(dep_agg.items()):
        mnemonic = lookup_mnemonic(evt_type, dep=True)
        principle_desc = get_principle_description(mnemonic)
        report_lines.append(f"\n[{mnemonic}] Event: {evt_type}")
        report_lines.append(f"Principle: {principle_desc}")
        top_examples = format_examples(examples, max_examples)
        for ex, cnt in top_examples:
            report_lines.append(f"  - Example ({cnt}x): {ex}")

    # Process constituency event features
    report_lines.append("\n== Constituency Parse Features ==")
    for evt_type, examples in sorted(const_agg.items()):
        mnemonic = lookup_mnemonic(evt_type, dep=False)
        principle_desc = get_principle_description(mnemonic)
        report_lines.append(f"\n[{mnemonic}] Event: {evt_type}")
        report_lines.append(f"Principle: {principle_desc}")
        top_examples = format_examples(examples, max_examples)
        for ex, cnt in top_examples:
            report_lines.append(f"  - Example ({cnt}x): {ex}")

    return "\n".join(report_lines)

def lookup_mnemonic(event_type: str, dep: bool) -> str:
    """
    Map the raw event_type strings from CSVs to mnemonic codes (keys in feature_to_principle_map).

    You can extend this as per your CSV event type naming conventions.
    """
    # Example dependecy CSV event_type to mnemonic mappings
    if dep:
        mapping = {
            "tokens_added": "WORD-ADD",
            "tokens_deleted": "FW-DEL",
            "tokens_reordered": "TOKEN-REORDER",
            "form_changes": "FORM-CHG",
            "lemma_changes": "LEMMA-CHG",
            "pos_changes": "POS-CHG",
            "feat_changes": "FEAT-CHG",
            "dep_changes": "DEP-REL-CHG",
        }
        return mapping.get(event_type, "UNK-DEP")
    else:
        mapping = {
            "word_added": "WORD-ADD",
            "word_removed": "WORD-REM",
            "pos_change": "POS-CHG",
            "constituent_added": "CONST-ADD",
            "constituent_removed": "CONST-REM",
            "tree_edit_distance": "TED",
        }
        return mapping.get(event_type, "UNK-CONST")

# -------- Incremental Update Function for Mapping --------

def update_feature_mapping_with_new_features(new_features: Dict[str, str]):
    """
    Add or override entries in the feature-to-principle map.

    new_features: dict of {mnemonic_tag: description}
    """
    for tag, desc in new_features.items():
        add_feature_mapping(tag, desc)
    print(f"Updated feature-to-principle map with {len(new_features)} items.")

# -------- Example usage --------

if __name__ == "__main__":
    dep_csv_path = "dependency_local_events.csv"
    const_csv_path = "constituency_local_events.csv"

    # Generate report with top 5 examples each
    report = generate_feature_report(dep_csv_path, const_csv_path, max_examples=5)
    print(report)

    # Example: dynamically add a new feature mapping
    new_features = {
        "CONST-ADD": "Constituent Addition: Complexifying the phrase structure in canonical.",
    }
    update_feature_mapping_with_new_features(new_features)
