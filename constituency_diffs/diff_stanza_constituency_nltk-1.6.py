import nltk
from nltk import Tree
import zss
import numpy as np
from collections import Counter
import json
import csv
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, fisher_exact, ttest_1samp

# --- Read trees (w/ metadata) ---
def read_trees_with_metadata(filename):
    result = []
    current_lines = []
    current_metadata = None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line_strip = line.strip()
            if line_strip.startswith("(sentence"):
                if current_lines:
                    tree_str = "\n".join(current_lines)
                    try:
                        tree = Tree.fromstring(tree_str)
                        result.append((current_metadata, tree))
                    except Exception as e:
                        print(f"Skipping malformed tree:\n{tree_str[:80]}... due to {e}")
                    current_lines = []
                current_metadata = line_strip
                continue
            if not line_strip:
                if current_lines:
                    tree_str = "\n".join(current_lines)
                    try:
                        tree = Tree.fromstring(tree_str)
                        result.append((current_metadata, tree))
                    except Exception as e:
                        print(f"Skipping malformed tree:\n{tree_str[:80]}... due to {e}")
                    current_lines = []
                    current_metadata = None
                continue
            if line_strip.startswith('('):
                current_lines.append(line.rstrip())
        if current_lines:
            tree_str = "\n".join(current_lines)
            try:
                tree = Tree.fromstring(tree_str)
                result.append((current_metadata, tree))
            except Exception as e:
                print(f"Skipping malformed tree:\n{tree_str[:80]}... due to {e}")
    return result

# --- Tree edit distance via ZSS ---
class ZssNode(object):
    def __init__(self, label):
        self.label = label
        self.children = []
    def get_children(self):
        return self.children
    def get_label(self):
        return self.label

def nltk_to_zss(node):
    znode = ZssNode(node.label() if isinstance(node, Tree) else str(node))
    if isinstance(node, Tree):
        for child in node:
            if isinstance(child, Tree):
                znode.children.append(nltk_to_zss(child))
            else:
                znode.children.append(ZssNode(str(child)))
    return znode

def tree_edit_distance(t1, t2):
    zn1 = nltk_to_zss(t1)
    zn2 = nltk_to_zss(t2)
    return zss.simple_distance(
        zn1, zn2,
        get_children=lambda node: node.get_children(),
        get_label=lambda node: node.get_label()
    )

# --- Event/context extraction ---
def get_word_pos_lists(tree):
    return [(w, pos, i) for i, (w, pos) in enumerate(tree.pos())]

def constituent_spans(tree):
    spans = []
    def helper(t, start, parent_label):
        if isinstance(t, str):
            return start + 1
        end = start
        for child in t:
            end = helper(child, end, t.label())
        if t.height() > 2:
            spans.append((start, end, t.label(), parent_label, t.leaves()))
        return end
    helper(tree, 0, None)
    return spans

def word_context(tree, target_word):
    contexts = []
    def traverse(t, parent_label=None, grandparent_label=None):
        if isinstance(t, str):
            return
        for child in t:
            if isinstance(child, Tree) and child.height() == 2 and target_word in child.leaves():
                siblings = [sib for sib in t if sib != child]
                context = {
                    "pos": child.label(),
                    "parent": t.label(),
                    "grandparent": parent_label,
                    "siblings": [sib.leaves() if isinstance(sib, Tree) else [sib] for sib in siblings]
                }
                contexts.append(context)
            traverse(child, parent_label=t.label(), grandparent_label=parent_label)
    traverse(tree)
    return contexts

def compare_pair(head_tree, canon_tree):
    h_words = get_word_pos_lists(head_tree)
    c_words = get_word_pos_lists(canon_tree)
    h_word_set = set(w for w, _, _ in h_words)
    c_word_set = set(w for w, _, _ in c_words)

    added_words = c_word_set - h_word_set
    removed_words = h_word_set - c_word_set

    word_to_pos_h = {w: pos for w, pos, _ in h_words}
    word_to_pos_c = {w: pos for w, pos, _ in c_words}
    common_words = h_word_set & c_word_set
    pos_changes = []
    for w in common_words:
        if word_to_pos_h[w] != word_to_pos_c[w]:
            pos_changes.append({
                "word": w,
                "pos_headline": word_to_pos_h[w],
                "pos_canonical": word_to_pos_c[w],
                "h_context": word_context(head_tree, w),
                "c_context": word_context(canon_tree, w)
            })

    h_spans = set((a, b, l) for a, b, l, _, _ in constituent_spans(head_tree))
    c_spans = set((a, b, l) for a, b, l, _, _ in constituent_spans(canon_tree))

    removed_constituents = []
    for a, b, l, parent, words in constituent_spans(head_tree):
        if (a, b, l) not in c_spans:
            removed_constituents.append({
                "span": (a, b),
                "label": l,
                "parent": parent,
                "words": words
            })
    added_constituents = []
    for a, b, l, parent, words in constituent_spans(canon_tree):
        if (a, b, l) not in h_spans:
            added_constituents.append({
                "span": (a, b),
                "label": l,
                "parent": parent,
                "words": words
            })

    words_removed = [{
        "word": w,
        "pos": word_to_pos_h[w],
        "context": word_context(head_tree, w)
    } for w in removed_words]
    words_added = [{
        "word": w,
        "pos": word_to_pos_c[w],
        "context": word_context(canon_tree, w)
    } for w in added_words]

    return {
        "words_removed": words_removed,
        "words_added": words_added,
        "pos_changes": pos_changes,
        "constituents_removed": removed_constituents,
        "constituents_added": added_constituents
    }

# --- Statistics and plotting ---
def simple_statistical_table(event_headline, event_canonical, total_h, total_c):
    k11 = event_headline
    k12 = total_h - event_headline
    k21 = event_canonical
    k22 = total_c - event_canonical
    table = [[k11, k12], [k21, k22]]
    try:
        chisq, p, _, _ = chi2_contingency(table)
    except Exception:
        chisq, p = float('nan'), float('nan')
    try:
        odds, fisher_p = fisher_exact(table)
    except Exception:
        odds, fisher_p = float('nan'), float('nan')
    direction = "headline" if odds > 1 else "canonical"
    return {
        "chisq": chisq,
        "chisq_p": p,
        "fisher_odds_ratio": odds,
        "fisher_p_value": fisher_p,
        "direction": direction
    }

def accumulate_global_stats(all_events):
    global_counts = {
        "words_added": {"headline": 0, "canonical": 0},
        "words_removed": {"headline": 0, "canonical": 0},
        "pos_changes": {"headline": 0, "canonical": 0},
        "constituents_added": {"headline": 0, "canonical": 0},
        "constituents_removed": {"headline": 0, "canonical": 0}
    }
    total_headline_tokens = 0
    total_canonical_tokens = 0

    for ev_wrapper in all_events:
        ev = ev_wrapper["comparison_event"]
        global_counts["words_added"]["canonical"] += len(ev["words_added"])
        global_counts["words_removed"]["headline"] += len(ev["words_removed"])
        global_counts["pos_changes"]["headline"] += len(ev["pos_changes"])
        global_counts["pos_changes"]["canonical"] += len(ev["pos_changes"])
        global_counts["constituents_added"]["canonical"] += len(ev["constituents_added"])
        global_counts["constituents_removed"]["headline"] += len(ev["constituents_removed"])
        total_headline_tokens += len(ev["words_removed"]) + len(ev["pos_changes"])
        total_canonical_tokens += len(ev["words_added"]) + len(ev["pos_changes"])
    global_counts["words_added"]["headline"] = 0
    global_counts["words_removed"]["canonical"] = 0
    global_counts["constituents_added"]["headline"] = 0
    global_counts["constituents_removed"]["canonical"] = 0
    return global_counts, total_headline_tokens, total_canonical_tokens

def export_global_stats_to_csv(global_counts, stats_results, filename):
    fieldnames = ['event', 'count_headline', 'count_canonical', 'chi2', 'p_value', 'fisher_odds_ratio', 'fisher_p_value', 'direction']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for event in global_counts:
            row = {
                'event': event,
                'count_headline': global_counts[event]['headline'],
                'count_canonical': global_counts[event]['canonical'],
                'chi2': stats_results[event]['chisq'],
                'p_value': stats_results[event]['chisq_p'],
                'fisher_odds_ratio': stats_results[event]['fisher_odds_ratio'],
                'fisher_p_value': stats_results[event]['fisher_p_value'],
                'direction': stats_results[event]['direction']
            }
            writer.writerow(row)

def export_local_events_to_csv(all_events, filename):
    # Main events with TED and metadata.
    fieldnames = ["pair_index", "headline_metadata", "canonical_metadata", "tree_edit_distance",
                  "event_type", "word/constituent", "pos_label", "parent_label", "grandparent_label", "additional_context"]
    with open(filename, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for idx, ev_wrapper in enumerate(all_events):
            ev = ev_wrapper["comparison_event"]
            meta_h = ev_wrapper["headline_metadata"]
            meta_c = ev_wrapper["canonical_metadata"]
            ted = ev_wrapper.get("tree_edit_distance")
            for item in ev['words_removed']:
                writer.writerow({
                    "pair_index": idx,
                    "headline_metadata": meta_h,
                    "canonical_metadata": meta_c,
                    "tree_edit_distance": ted,
                    "event_type": "word_removed",
                    "word/constituent": item['word'],
                    "pos_label": item['pos'],
                    "parent_label": item['context'][0]['parent'] if item['context'] else None,
                    "grandparent_label": item['context'][0]['grandparent'] if item['context'] else None,
                    "additional_context": ', '.join([str(sib) for sib in item['context'][0]['siblings']]) if item['context'] else None
                })
            for item in ev['words_added']:
                writer.writerow({
                    "pair_index": idx,
                    "headline_metadata": meta_h,
                    "canonical_metadata": meta_c,
                    "tree_edit_distance": ted,
                    "event_type": "word_added",
                    "word/constituent": item['word'],
                    "pos_label": item['pos'],
                    "parent_label": item['context'][0]['parent'] if item['context'] else None,
                    "grandparent_label": item['context'][0]['grandparent'] if item['context'] else None,
                    "additional_context": ', '.join([str(sib) for sib in item['context'][0]['siblings']]) if item['context'] else None
                })
            for item in ev['pos_changes']:
                writer.writerow({
                    "pair_index": idx,
                    "headline_metadata": meta_h,
                    "canonical_metadata": meta_c,
                    "tree_edit_distance": ted,
                    "event_type": "pos_change",
                    "word/constituent": item['word'],
                    "pos_label": f"headline: {item['pos_headline']} | canonical: {item['pos_canonical']}",
                    "parent_label": item['h_context'][0]['parent'] if item['h_context'] else None,
                    "grandparent_label": item['h_context'][0]['grandparent'] if item['h_context'] else None,
                    "additional_context": ', '.join([str(sib) for sib in item['h_context'][0]['siblings']]) if item['h_context'] else None
                })
            for item in ev['constituents_added']:
                writer.writerow({
                    "pair_index": idx,
                    "headline_metadata": meta_h,
                    "canonical_metadata": meta_c,
                    "tree_edit_distance": ted,
                    "event_type": "constituent_added",
                    "word/constituent": ' '.join(item['words']),
                    "pos_label": item['label'],
                    "parent_label": item['parent'],
                    "grandparent_label": None,
                    "additional_context": None
                })
            for item in ev['constituents_removed']:
                writer.writerow({
                    "pair_index": idx,
                    "headline_metadata": meta_h,
                    "canonical_metadata": meta_c,
                    "tree_edit_distance": ted,
                    "event_type": "constituent_removed",
                    "word/constituent": ' '.join(item['words']),
                    "pos_label": item['label'],
                    "parent_label": item['parent'],
                    "grandparent_label": None,
                    "additional_context": None
                })

def export_ted_scores_csv(all_events, filename):
    # Export just TEDs and metadata per pair
    with open(filename, "w", newline='', encoding='utf-8') as csvfile:
        w = csv.writer(csvfile)
        w.writerow(["pair_index", "headline_metadata", "canonical_metadata", "tree_edit_distance"])
        for idx, ev in enumerate(all_events):
            w.writerow([idx, ev["headline_metadata"], ev["canonical_metadata"], ev["tree_edit_distance"]])

def plot_global_counts(global_counts):
    events = list(global_counts.keys())
    headline_counts = [global_counts[evt]['headline'] for evt in events]
    canonical_counts = [global_counts[evt]['canonical'] for evt in events]

    x = range(len(events))
    width = 0.35

    plt.figure(figsize=(12,6))
    plt.bar(x, headline_counts, width, label='Headline', color='skyblue')
    plt.bar([i + width for i in x], canonical_counts, width, label='Canonical', color='orange')
    plt.xticks([i + width/2 for i in x], events, rotation=45, ha='right')
    plt.ylabel('Counts of Events')
    plt.title('Global Counts of Constituency Tree Events')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_odds_ratios(stats_results):
    events = list(stats_results.keys())
    odds = [stats_results[e]['fisher_odds_ratio'] for e in events]
    plt.figure(figsize=(10,5))
    plt.bar(events, odds, color='purple')
    plt.axhline(1, color='red', linestyle='dashed')
    plt.ylabel('Odds Ratio (Fisher Exact)')
    plt.title('Odds Ratios of Events: Headlines vs Canonical')
    plt.xticks(rotation=45, ha='right')
    plt.yscale('log')
    plt.tight_layout()
    plt.show()

def plot_ted_histogram(ted_scores, shuffled_scores=None):
    plt.figure(figsize=(8,5))
    plt.hist(ted_scores, bins=20, alpha=0.7, label="Headline–Canonical pairs", color='slateblue', edgecolor='black')
    if shuffled_scores is not None:
        plt.hist(shuffled_scores, bins=20, alpha=0.5, label="Shuffled baseline", color='gray', edgecolor='black')
    plt.title("Distribution of Tree Edit Distance")
    plt.xlabel("Tree Edit Distance")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    headline_file = "headline_trees.txt"
    canonical_file = "canonical_trees.txt"

    headline_trees = read_trees_with_metadata(headline_file)
    canonical_trees = read_trees_with_metadata(canonical_file)
    assert len(headline_trees) == len(canonical_trees), "Tree count mismatch!"

    all_events = []
    edit_distances = []

    for (h_meta, h_tree), (c_meta, c_tree) in zip(headline_trees, canonical_trees):
        event = compare_pair(h_tree, c_tree)
        ted = tree_edit_distance(h_tree, c_tree)
        all_events.append({
            "headline_metadata": h_meta,
            "canonical_metadata": c_meta,
            "comparison_event": event,
            "tree_edit_distance": ted
        })
        edit_distances.append(ted)

    # Event/global stats
    global_counts, total_h, total_c = accumulate_global_stats(all_events)
    stats_results = {}
    for evt, counts in global_counts.items():
        stats_results[evt] = simple_statistical_table(counts["headline"], counts["canonical"], total_h, total_c)

    # Tree edit distance statistics and plot
    edit_distances_np = np.array(edit_distances)
    mean_ted = np.mean(edit_distances_np)
    median_ted = np.median(edit_distances_np)
    print(f"Mean TED: {mean_ted:.2f}, Median TED: {median_ted:.2f}")
    stat, p = ttest_1samp(edit_distances_np, 0)
    print(f"One-sample t-test vs 0: t={stat:.2f}, p={p:.4g}")

    # (Optional) baseline with shuffled canonicals
    np.random.seed(1)
    shuffled = np.random.permutation([x[1] for x in canonical_trees])
    shuffled_teds = [tree_edit_distance(h_tree, s_tree) for (_, h_tree), s_tree in zip(headline_trees, shuffled)]
    stat2, p2 = ttest_1samp(edit_distances_np - np.array(shuffled_teds), 0)
    print(f"Paired t-test true pairs vs shuffled: t={stat2:.2f}, p={p2:.4g}")

    # Export
    export_global_stats_to_csv(global_counts, stats_results, "constituency_global_stats.csv")
    export_local_events_to_csv(all_events, "constituency_local_events.csv")
    export_ted_scores_csv(all_events, "constituency_tree_edit_distances.csv")

    # Plots
    plot_global_counts(global_counts)
    plot_odds_ratios(stats_results)
    plot_ted_histogram(edit_distances, shuffled_teds)

    print("Analysis complete. CSV files and plots generated.")
