import json
import csv
from math import log
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, fisher_exact, ttest_1samp
import numpy as np
import udapi

# --- Statistical helpers ---
def cramers_v(chisq, n, k=2):
    return (chisq / (n * (k-1))) ** 0.5 if n > 0 else 0.0

def log_likelihood(k11, k12, k21, k22):
    def safe_log(x): return log(x) if x > 0 else 0
    n = k11 + k12 + k21 + k22
    row1 = k11 + k12
    row2 = k21 + k22
    col1 = k11 + k21
    col2 = k12 + k22
    E11 = row1 * col1 / n
    E12 = row1 * col2 / n
    E21 = row2 * col1 / n
    E22 = row2 * col2 / n
    ll = 2 * (k11 * safe_log(k11/E11) +
              k12 * safe_log(k12/E12) +
              k21 * safe_log(k21/E21) +
              k22 * safe_log(k22/E22))
    return ll

def compute_event_stats(event_count, total_reduced, total_canonical):
    k11 = event_count["reduced"]
    k12 = total_reduced - k11
    k21 = event_count["canonical"]
    k22 = total_canonical - k21
    table = [[k11, k12], [k21, k22]]
    try:
        chisq, p, _, _ = chi2_contingency(table)
    except Exception:
        chisq, p = float('nan'), float('nan')
    try:
        odds, fisher_p = fisher_exact(table)
    except Exception:
        odds, fisher_p = float('nan'), float('nan')
    direction = "reduced" if odds > 1 else "canonical"
    v = cramers_v(chisq, total_reduced + total_canonical)
    llr = log_likelihood(k11, k12, k21, k22)
    return {
        "counts": {"k11": k11, "k12": k12, "k21": k21, "k22": k22},
        "chisq": chisq,
        "chisq_p": p,
        "fisher_odds_ratio": odds,
        "fisher_p": fisher_p,
        "cramers_v": v,
        "odds_ratio_direction": direction,
        "log_likelihood_ratio": llr
    }

# --- Cost and alignment (same as previous script) ---
import scipy.optimize
def feature_overlap(feats1, feats2):
    if not feats1 and not feats2:
        return 0
    set1 = set(feats1.items()) if feats1 else set()
    set2 = set(feats2.items()) if feats2 else set()
    return 1 - len(set1 & set2) / max(1, len(set1 | set2))

def compute_cost(r, c):
    cost = 0
    if r['lemma'].lower() != c['lemma'].lower():
        cost += 1.5
    if r['upos'] != c['upos']:
        cost += 1
    if r.get('deprel') != c.get('deprel'):
        cost += 0.5
    cost += feature_overlap(r.get('feats'), c.get('feats'))
    return cost

def align_tokens(reduced_tokens, canonical_tokens):
    n = len(reduced_tokens)
    m = len(canonical_tokens)
    size = max(n, m)
    cost_matrix = [[3]*size for _ in range(size)]

    for i in range(n):
        for j in range(m):
            cost_matrix[i][j] = compute_cost(reduced_tokens[i], canonical_tokens[j])
    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
    mapping = {i: j if j < m and cost_matrix[i][j] < 3 else None for i,j in zip(row_ind, col_ind)}

    return mapping

# --- Main comparison: single pair ---
def compare_sentences(r_root, c_root):
    r_tokens = sorted([node for node in r_root.descendants if not node.is_root()], key=lambda n: n.ord)
    c_tokens = sorted([node for node in c_root.descendants if not node.is_root()], key=lambda n: n.ord)
    r_token_dicts = [{"id": n.ord, "form": n.form, "lemma": n.lemma, "upos": n.upos, "feats": n.feats, "deprel": n.deprel} for n in r_tokens]
    c_token_dicts = [{"id": n.ord, "form": n.form, "lemma": n.lemma, "upos": n.upos, "feats": n.feats, "deprel": n.deprel} for n in c_tokens]
    mapping = align_tokens(r_token_dicts, c_token_dicts)

    # Local event lists
    event_instances = {
        "tokens_added": [],
        "tokens_deleted": [],
        "tokens_reordered": [],
        "form_changes": [],
        "lemma_changes": [],
        "pos_changes": [],
        "feat_changes": [],
        "dep_changes": []
    }
    stats = {k: {"reduced": 0, "canonical": 0} for k in event_instances}
    text_report = []
    for i, r in enumerate(r_token_dicts):
        j = mapping.get(i)
        if j is None:
            event_instances["tokens_deleted"].append({"form": r['form'], "lemma": r['lemma'], "upos": r['upos'], "context": r})
            stats["tokens_deleted"]["reduced"] += 1
            text_report.append(f"- Token deleted from reduced: {r['form']} ({r['lemma']})")
            continue
        c = c_token_dicts[j]
        if i != j:
            event_instances["tokens_reordered"].append({"form": r['form'], "from": i+1, "to": j+1, "upos": r['upos'], "context": r})
            stats["tokens_reordered"]["reduced"] += 1
            stats["tokens_reordered"]["canonical"] += 1
            text_report.append(f"* Token reordered: {r['form']} (pos {i+1} → {j+1})")
        if r['form'] != c['form']:
            event_instances["form_changes"].append({"from": r['form'], "to": c['form'], "upos_r": r['upos'], "upos_c": c['upos']})
            stats["form_changes"]["reduced"] += 1
            stats["form_changes"]["canonical"] += 1
            text_report.append(f"* FORM: {r['form']} → {c['form']}")
        if r['lemma'] != c['lemma']:
            event_instances["lemma_changes"].append({"from": r['lemma'], "to": c['lemma'], "upos_r": r['upos'], "upos_c": c['upos']})
            stats["lemma_changes"]["reduced"] += 1
            stats["lemma_changes"]["canonical"] += 1
            text_report.append(f"* LEMMA: {r['lemma']} → {c['lemma']}")
        if r['upos'] != c['upos']:
            event_instances["pos_changes"].append({"form": r['form'], "from": r['upos'], "to": c['upos']})
            stats["pos_changes"]["reduced"] += 1
            stats["pos_changes"]["canonical"] += 1
            text_report.append(f"* POS: {r['form']} {r['upos']} → {c['upos']}")
        if r['feats'] != c['feats']:
            event_instances["feat_changes"].append({"form": r['form'], "from": r['feats'], "to": c['feats']})
            stats["feat_changes"]["reduced"] += 1
            stats["feat_changes"]["canonical"] += 1
            text_report.append(f"* FEATS: {r['form']} {r['feats']} → {c['feats']}")

    mapped_c = {j for j in mapping.values() if j is not None}
    for j, c in enumerate(c_token_dicts):
        if j not in mapped_c:
            event_instances["tokens_added"].append({"form": c['form'], "lemma": c['lemma'], "upos": c['upos'], "context": c})
            stats["tokens_added"]["canonical"] += 1
            text_report.append(f"+ Token added in canonical: {c['form']} ({c['lemma']})")

    for i, r_node in enumerate(r_tokens):
        j = mapping.get(i)
        if j is None or j >= len(c_tokens):
            continue
        c_node = c_tokens[j]
        # Compare head word and rel
        if r_node.parent.form != c_node.parent.form or r_node.deprel != c_node.deprel:
            event_instances["dep_changes"].append({
                "form": r_node.form, "old_head": r_node.parent.form, "old_rel": r_node.deprel,
                "new_head": c_node.parent.form, "new_rel": c_node.deprel
            })
            stats["dep_changes"]["reduced"] += 1
            stats["dep_changes"]["canonical"] += 1
            text_report.append(f"* DEP: {r_node.form} {r_node.parent.form}({r_node.deprel}) → {c_node.parent.form}({c_node.deprel})")

    return {
        "event_instances": event_instances,
        "stats": stats,
        "text_report": text_report,
        "token_count": {
            "reduced": len(r_token_dicts),
            "canonical": len(c_token_dicts)
        }
    }

# --- Aggregate and analyze all pairs ---
def aggregate_and_compare(r_doc, c_doc):
    r_trees = list(r_doc.trees)
    c_trees = list(c_doc.trees)
    assert len(r_trees) == len(c_trees), "Tree count mismatch"
    global_stats = {k: {"reduced": 0, "canonical": 0} for k in [
        "tokens_added", "tokens_deleted", "tokens_reordered",
        "form_changes", "lemma_changes", "pos_changes", "feat_changes", "dep_changes"
    ]}
    global_token_counts = {"reduced": 0, "canonical": 0}
    all_pair_results = []

    # Prepare for event-specific lists for global reporting
    global_events_lists = {k: [] for k in global_stats}

    for r_root, c_root in zip(r_trees, c_trees):
        pair = compare_sentences(r_root, c_root)
        all_pair_results.append(pair)
        for stat_type in global_stats:
            global_stats[stat_type]["reduced"] += pair["stats"][stat_type]["reduced"]
            global_stats[stat_type]["canonical"] += pair["stats"][stat_type]["canonical"]
            # For detailed event instance lists
            global_events_lists[stat_type].extend(pair["event_instances"][stat_type])
        global_token_counts["reduced"] += pair["token_count"]["reduced"]
        global_token_counts["canonical"] += pair["token_count"]["canonical"]

    # Per-pair (local) stats
    for pair in all_pair_results:
        adv_stats = {}
        n_r = pair["token_count"]["reduced"]
        n_c = pair["token_count"]["canonical"]
        for evt, counts in pair["stats"].items():
            adv_stats[evt] = compute_event_stats(counts, n_r, n_c)
        pair["advanced_stats"] = adv_stats

    # Global stats and tests
    global_advanced_stats = {}
    n_r = global_token_counts["reduced"]
    n_c = global_token_counts["canonical"]
    for evt, counts in global_stats.items():
        global_advanced_stats[evt] = compute_event_stats(counts, n_r, n_c)

    return {
        "pairs": all_pair_results,
        "global": {
            "stats": global_stats,
            "token_count": global_token_counts,
            "advanced_stats": global_advanced_stats,
            "events_lists": global_events_lists
        }
    }

# --- CSV Exports ---
def export_global_stats_to_csv(global_data, filename):
    fieldnames = ["event", "count_reduced", "count_canonical", "chi2", "p_value", "fisher_odds_ratio",
                  "fisher_p", "cramers_v", "odds_ratio_direction", "log_likelihood_ratio"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for evt, stats in global_data["advanced_stats"].items():
            row = {
                "event": evt,
                "count_reduced": global_data["stats"][evt]["reduced"],
                "count_canonical": global_data["stats"][evt]["canonical"],
                "chi2": stats["chisq"],
                "p_value": stats["chisq_p"],
                "fisher_odds_ratio": stats["fisher_odds_ratio"],
                "fisher_p": stats["fisher_p"],
                "cramers_v": stats["cramers_v"],
                "odds_ratio_direction": stats["odds_ratio_direction"],
                "log_likelihood_ratio": stats["log_likelihood_ratio"]
            }
            writer.writerow(row)

def export_local_events_to_csv(all_pairs, filename):
    fieldnames = ["pair_index", "event_type", "form", "lemma", "upos", "from", "to", "context", "extra"]
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, pair in enumerate(all_pairs):
            for evt, inst_list in pair["event_instances"].items():
                for inst in inst_list:
                    row = {"pair_index": idx, "event_type": evt}
                    row.update({
                        "form": inst.get("form"),
                        "lemma": inst.get("lemma"),
                        "upos": inst.get("upos"),
                        "from": inst.get("from"),
                        "to": inst.get("to"),
                        "context": json.dumps(inst.get("context", ""), ensure_ascii=False) if "context" in inst else "",
                        "extra": json.dumps(inst, ensure_ascii=False)
                    })
                    writer.writerow(row)

# --- Plots ---
def plot_global_counts(global_stats):
    events = list(global_stats.keys())
    reduced_counts = [global_stats[evt]["reduced"] for evt in events]
    canonical_counts = [global_stats[evt]["canonical"] for evt in events]
    x = range(len(events))
    width = 0.35
    plt.figure(figsize=(12, 6))
    plt.bar(x, reduced_counts, width, label='Reduced', color='steelblue')
    plt.bar([i + width for i in x], canonical_counts, width, label='Canonical', color='orange')
    plt.xticks([i + width/2 for i in x], events, rotation=45, ha="right")
    plt.ylabel("Event Counts")
    plt.title("Global Event Counts: Reduced vs Canonical")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_odds_ratios(global_advanced_stats):
    events = list(global_advanced_stats.keys())
    odds = [global_advanced_stats[e]['fisher_odds_ratio'] for e in events]
    plt.figure(figsize=(10, 5))
    plt.bar(events, odds, color='purple')
    plt.axhline(1, color='red', linestyle='dashed')
    plt.ylabel("Odds Ratio (Fisher)")
    plt.title("Global Odds Ratios: Reduced vs Canonical")
    plt.xticks(rotation=45, ha="right")
    plt.yscale("log")
    plt.tight_layout()
    plt.show()

# --- Main ---
if __name__ == "__main__":
    # Point these to your files
    reduced_path = "reduced.conllu"
    canonical_path = "canonical.conllu"
    r_doc = udapi.Document(reduced_path)
    c_doc = udapi.Document(canonical_path)

    comparison = aggregate_and_compare(r_doc, c_doc)

    # Save CSVs with detailed/local and global events
    export_local_events_to_csv(comparison["pairs"], "dependency_local_events.csv")
    export_global_stats_to_csv(comparison["global"], "dependency_global_stats.csv")

    # Plots
    plot_global_counts(comparison["global"]["stats"])
    plot_odds_ratios(comparison["global"]["advanced_stats"])

    # Print summary and locations of data files
    print("Local events (with context) saved to dependency_local_events.csv")
    print("Global stats and tests saved to dependency_global_stats.csv")

    print("Analysis complete.")
