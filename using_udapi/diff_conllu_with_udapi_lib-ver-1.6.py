import json
import csv
import udapi
import scipy.optimize
from math import log
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt

### --- Statistical helpers --- ###

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

def compute_event_stats(event_count, total_headline, total_canonical):
    k11 = event_count["headline"]
    k12 = total_headline - k11
    k21 = event_count["canonical"]
    k22 = total_canonical - k21

    if min(k11, k12, k21, k22) == 0:
        return {
            "counts": {"k11": k11, "k12": k12, "k21": k21, "k22": k22},
            "chisq": float('nan'),
            "chisq_p": float('nan'),
            "cramers_v": float('nan'),
            "odds_ratio": float('nan'),
            "odds_ratio_direction": None,
            "log_likelihood_ratio": float('nan')
        }

    table = [[k11, k12], [k21, k22]]
    chisq, p, _, _ = chi2_contingency(table)
    n = total_headline + total_canonical
    v = cramers_v(chisq, n)
    odds = ((k11 / max(k12,1)) / (k21 / max(k22,1))) if k21 > 0 and k22 > 0 else float("inf")
    direction = "headline" if odds > 1 else "canonical"
    llr = log_likelihood(k11, k12, k21, k22)

    return {
        "counts": {"k11": k11, "k12": k12, "k21": k21, "k22": k22},
        "chisq": chisq,
        "chisq_p": p,
        "cramers_v": v,
        "odds_ratio": odds,
        "odds_ratio_direction": direction,
        "log_likelihood_ratio": llr
    }

### --- Cost function --- ###

def feature_overlap(feats1, feats2):
    if not feats1 and not feats2:
        return 0
    set1 = set(feats1.items()) if feats1 else set()
    set2 = set(feats2.items()) if feats2 else set()
    return 1 - len(set1 & set2) / max(1, len(set1 | set2))

def compute_cost(h, c):
    cost = 0
    if h['lemma'].lower() != c['lemma'].lower():
        cost += 1.5
    if h['upos'] != c['upos']:
        cost += 1
    if h.get('deprel') != c.get('deprel'):
        cost += 0.5
    cost += feature_overlap(h.get('feats'), c.get('feats'))
    return cost

### --- Hungarian alignment --- ###

def align_tokens(h_tokens, c_tokens):
    n = len(h_tokens)
    m = len(c_tokens)
    size = max(n, m)
    cost_matrix = [[3]*size for _ in range(size)]
    for i in range(n):
        for j in range(m):
            cost_matrix[i][j] = compute_cost(h_tokens[i], c_tokens[j])
    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
    mapping = {i: j if j < m and cost_matrix[i][j] < 3 else None for i,j in zip(row_ind, col_ind)}
    return mapping

### --- Compare one sentence pair --- ###

def compare_sentences(h_root, c_root):
    h_tokens = sorted([node for node in h_root.descendants if not node.is_root()], key=lambda n: n.ord)
    c_tokens = sorted([node for node in c_root.descendants if not node.is_root()], key=lambda n: n.ord)

    h_token_dicts = [{"id": n.ord, "form": n.form, "lemma": n.lemma, "upos": n.upos, "feats": n.feats, "deprel": n.deprel} for n in h_tokens]
    c_token_dicts = [{"id": n.ord, "form": n.form, "lemma": n.lemma, "upos": n.upos, "feats": n.feats, "deprel": n.deprel} for n in c_tokens]

    mapping = align_tokens(h_token_dicts, c_token_dicts)

    stats = {k: {"headline": 0, "canonical": 0} for k in [
        "tokens_added", "tokens_deleted", "tokens_reordered",
        "form_changes", "lemma_changes", "pos_changes", "feat_changes", "dep_changes"
    ]}
    token_diffs = []
    dep_diffs = []
    text_report = []

    for i, h in enumerate(h_token_dicts):
        j = mapping.get(i)
        if j is None:
            token_diffs.append({"type": "deleted", "form": h['form'], "lemma": h['lemma']})
            text_report.append(f"- Token missing in canonical: {h['form']} ({h['lemma']})")
            stats["tokens_deleted"]["headline"] += 1
            continue
        c = c_token_dicts[j]
        if i != j:
            token_diffs.append({"type": "reordered", "form": h['form'], "from": i+1, "to": j+1})
            text_report.append(f"* Token reordered: {h['form']} (pos {i+1} → {j+1})")
            stats["tokens_reordered"]["headline"] += 1
            stats["tokens_reordered"]["canonical"] += 1
        if h['form'] != c['form']:
            token_diffs.append({"type": "form_change", "from": h['form'], "to": c['form']})
            text_report.append(f"* FORM: {h['form']} → {c['form']}")
            stats["form_changes"]["headline"] += 1
            stats["form_changes"]["canonical"] += 1
        if h['lemma'] != c['lemma']:
            token_diffs.append({"type": "lemma_change", "from": h['lemma'], "to": c['lemma']})
            text_report.append(f"* LEMMA: {h['lemma']} → {c['lemma']}")
            stats["lemma_changes"]["headline"] += 1
            stats["lemma_changes"]["canonical"] += 1
        if h['upos'] != c['upos']:
            token_diffs.append({"type": "pos_change", "form": h['form'], "from": h['upos'], "to": c['upos']})
            text_report.append(f"* POS: {h['form']} {h['upos']} → {c['upos']}")
            stats["pos_changes"]["headline"] += 1
            stats["pos_changes"]["canonical"] += 1
        if h['feats'] != c['feats']:
            token_diffs.append({"type": "feat_change", "form": h['form'], "from": h['feats'], "to": c['feats']})
            text_report.append(f"* FEATS: {h['form']} {h['feats']} → {c['feats']}")
            stats["feat_changes"]["headline"] += 1
            stats["feat_changes"]["canonical"] += 1

    mapped_c = {j for j in mapping.values() if j is not None}
    for j, c in enumerate(c_token_dicts):
        if j not in mapped_c:
            token_diffs.append({"type": "added", "form": c['form'], "lemma": c['lemma']})
            text_report.append(f"+ Token added in canonical: {c['form']} ({c['lemma']})")
            stats["tokens_added"]["canonical"] += 1

    for i, h_node in enumerate(h_tokens):
        j = mapping.get(i)
        if j is None or j >= len(c_tokens):
            continue
        c_node = c_tokens[j]
        if h_node.parent.form != c_node.parent.form or h_node.deprel != c_node.deprel:
            dep_diffs.append({
                "form": h_node.form,
                "old_head": h_node.parent.form,
                "old_rel": h_node.deprel,
                "new_head": c_node.parent.form,
                "new_rel": c_node.deprel
            })
            text_report.append(f"* DEP: {h_node.form} {h_node.parent.form}({h_node.deprel}) → {c_node.parent.form}({c_node.deprel})")
            stats["dep_changes"]["headline"] += 1
            stats["dep_changes"]["canonical"] += 1

    token_count = {"headline": len(h_token_dicts), "canonical": len(c_token_dicts)}

    return {
        "token_diffs": token_diffs,
        "dep_diffs": dep_diffs,
        "stats": stats,
        "text_report": text_report,
        "token_count": token_count
    }

### --- Aggregate all pairs and compute local/global statistics --- ###

def aggregate_and_compare(h_doc, c_doc):
    h_trees = list(h_doc.trees)
    c_trees = list(c_doc.trees)
    assert len(h_trees) == len(c_trees), "Sentence count mismatch!"

    global_stats = {k: {"headline": 0, "canonical": 0} for k in [
        "tokens_added", "tokens_deleted", "tokens_reordered",
        "form_changes", "lemma_changes", "pos_changes", "feat_changes", "dep_changes"
    ]}
    global_token_counts = {"headline": 0, "canonical": 0}
    pair_results = []

    for h_root, c_root in zip(h_trees, c_trees):
        pair = compare_sentences(h_root, c_root)
        pair_results.append(pair)
        for stat_type in global_stats.keys():
            global_stats[stat_type]["headline"] += pair["stats"][stat_type]["headline"]
            global_stats[stat_type]["canonical"] += pair["stats"][stat_type]["canonical"]
        global_token_counts["headline"] += pair["token_count"]["headline"]
        global_token_counts["canonical"] += pair["token_count"]["canonical"]

    # Compute advanced statistics for each pair (local)
    for pair in pair_results:
        adv_stats = {}
        n_h = pair["token_count"]["headline"]
        n_c = pair["token_count"]["canonical"]
        for evt, counts in pair["stats"].items():
            adv_stats[evt] = compute_event_stats(counts, n_h, n_c)
        pair["advanced_stats"] = adv_stats

    # Compute advanced statistics globally
    global_adv_stats = {}
    n_h = global_token_counts["headline"]
    n_c = global_token_counts["canonical"]
    for evt, counts in global_stats.items():
        global_adv_stats[evt] = compute_event_stats(counts, n_h, n_c)

    return {
        "pairs": pair_results,
        "global": {
            "stats": global_stats,
            "token_count": global_token_counts,
            "advanced_stats": global_adv_stats
        }
    }

### --- Export functions --- ###

def export_global_stats_to_csv(global_data, filename):
    fieldnames = ["event", "count_headline", "count_canonical", "chi2", "p_value", "cramers_v",
                  "odds_ratio", "odds_ratio_direction", "log_likelihood_ratio"]
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for evt, stats in global_data["advanced_stats"].items():
            row = {
                "event": evt,
                "count_headline": global_data["stats"][evt]["headline"],
                "count_canonical": global_data["stats"][evt]["canonical"],
                "chi2": stats["chisq"],
                "p_value": stats["chisq_p"],
                "cramers_v": stats["cramers_v"],
                "odds_ratio": stats["odds_ratio"],
                "odds_ratio_direction": stats["odds_ratio_direction"],
                "log_likelihood_ratio": stats["log_likelihood_ratio"]
            }
            writer.writerow(row)

def export_local_stats_to_csv(pair_results, filename):
    # Export a summary of stats for each pair, each row is a pair + event combos
    fieldnames = ["pair_index", "event", "count_headline", "count_canonical",
                  "chi2", "p_value", "cramers_v", "odds_ratio", "odds_ratio_direction", "log_likelihood_ratio"]
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for idx, pair in enumerate(pair_results):
            adv_stats = pair.get("advanced_stats", {})
            for evt, stats in adv_stats.items():
                row = {
                    "pair_index": idx,
                    "event": evt,
                    "count_headline": pair["stats"][evt]["headline"],
                    "count_canonical": pair["stats"][evt]["canonical"],
                    "chi2": stats["chisq"],
                    "p_value": stats["chisq_p"],
                    "cramers_v": stats["cramers_v"],
                    "odds_ratio": stats["odds_ratio"],
                    "odds_ratio_direction": stats["odds_ratio_direction"],
                    "log_likelihood_ratio": stats["log_likelihood_ratio"]
                }
                writer.writerow(row)

### --- Visualization --- ###

def plot_global_stats(global_data):
    import matplotlib.pyplot as plt

    events = list(global_data["stats"].keys())
    counts_headline = [global_data["stats"][evt]["headline"] for evt in events]
    counts_canonical = [global_data["stats"][evt]["canonical"] for evt in events]

    x = range(len(events))
    width = 0.35

    plt.figure(figsize=(12,6))
    plt.bar(x, counts_headline, width, label="Headline")
    plt.bar([i + width for i in x], counts_canonical, width, label="Canonical")

    plt.xticks([i + width/2 for i in x], events, rotation=45, ha="right")
    plt.ylabel("Event Counts")
    plt.title("Global Event Counts: Headline vs Canonical")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_odds_ratios(global_data):
    import matplotlib.pyplot as plt

    events = list(global_data["advanced_stats"].keys())
    odds_ratios = [global_data["advanced_stats"][evt]["odds_ratio"] for evt in events]

    x = range(len(events))

    plt.figure(figsize=(12,6))
    plt.bar(x, odds_ratios, color='purple')
    plt.axhline(y=1, color='r', linestyle='--')
    plt.xticks(x, events, rotation=45, ha="right")
    plt.ylabel("Odds Ratio")
    plt.title("Global Odds Ratios of Events (Headline vs Canonical)")
    plt.tight_layout()
    plt.show()

### --- Main script --- ###

if __name__ == "__main__":
    headline_path = "/mnt/d/projects/Bhaashik/ReducedToCanonicalConvDiff/headline.conllu"
    canonical_path = "/mnt/d/projects/Bhaashik/ReducedToCanonicalConvDiff/canonical.conllu"

    h_doc = udapi.Document(headline_path)
    c_doc = udapi.Document(canonical_path)

    comparison = aggregate_and_compare(h_doc, c_doc)

    # Export CSVs
    export_global_stats_to_csv(comparison["global"], "global_stats.csv")
    export_local_stats_to_csv(comparison["pairs"], "local_stats.csv")

    print("Global and local statistics exported to 'global_stats.csv' and 'local_stats.csv' respectively.")

    # Visualize some outputs
    plot_global_stats(comparison["global"])
    plot_odds_ratios(comparison["global"])
