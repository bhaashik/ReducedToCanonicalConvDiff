import csv
from collections import defaultdict

def load_event_counts(dep_event_file, const_event_file):
    """
    Loads per-pair event counts from dependency and constituency event CSVs.
    Returns a dict: {pair_index: {feature_name: count, ...}, ...}
    """

    feature_data = defaultdict(lambda: defaultdict(int))

    # Dependency features mapping from event_type in dep CSV
    dep_feature_map = {
        "tokens_added": "dep_tokens_added",
        "tokens_deleted": "dep_tokens_deleted",
        "tokens_reordered": "dep_tokens_reordered",
        "form_changes": "dep_form_changes",
        "lemma_changes": "dep_lemma_changes",
        "pos_changes": "dep_pos_changes",
        "feat_changes": "dep_feat_changes",
        "dep_changes": "dep_dep_rel_changes"
    }

    with open(dep_event_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pair_idx = int(row["pair_index"])
            evt_type = row["event_type"]
            feature_name = dep_feature_map.get(evt_type)
            if feature_name:
                feature_data[pair_idx][feature_name] += 1

    # Constituency features mapping
    const_feature_map = {
        "word_added": "const_words_added",
        "word_removed": "const_words_removed",
        "pos_change": "const_pos_tag_changes",
        "constituent_added": "const_constituents_added",
        "constituent_removed": "const_constituents_removed"
    }

    with open(const_event_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pair_idx = int(row["pair_index"])
            evt_type = row["event_type"]
            feature_name = const_feature_map.get(evt_type)
            if feature_name:
                feature_data[pair_idx][feature_name] += 1
            # You can also capture tree edit distance if present
            ted = row.get("tree_edit_distance")
            if ted:
                try:
                    ted_val = float(ted)
                    feature_data[pair_idx]["tree_edit_distance"] = ted_val
                except:
                    pass

    return feature_data

def save_features_csv(feature_data, output_file):
    # Collect all feature names for consistent columns
    all_features = set()
    for feats in feature_data.values():
        all_features.update(feats.keys())
    feature_list = sorted(all_features)

    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ["pair_index"] + feature_list
        writer.writerow(header)

        for pair_idx in sorted(feature_data.keys()):
            row = [pair_idx]
            feats = feature_data[pair_idx]
            for feat in feature_list:
                row.append(feats.get(feat, 0))
            writer.writerow(row)

def main():
    dep_event_file = "dependency_local_events.csv"       # Your dependency events CSV
    const_event_file = "constituency_local_events.csv"   # Your constituency events CSV
    output_feature_file = "unified_feature_matrix.csv"

    feature_data = load_event_counts(dep_event_file, const_event_file)
    save_features_csv(feature_data, output_feature_file)

    print(f"Unified feature matrix saved to {output_feature_file}")

if __name__ == "__main__":
    main()
