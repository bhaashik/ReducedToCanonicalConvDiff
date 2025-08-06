import json
from math import log
from collections import Counter
from conllu import parse
from io import open
import udapi
import scipy.optimize
from scipy.stats import chi2_contingency

### ---------- Statistical helpers ---------- ###

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

    table = [[k11, k12], [k21, k22]]
    chisq, p, _, _ = chi2_contingency(table)
    n = total_headline + total_canonical
    v = cramers_v(chisq, n)
    odds = ((k11 / max(k12,1)) / (k21 / max(k22,1))) if k21 > 0 and k22 > 0 else float("inf")
    direction = "headline" if odds > 1 else "canonical"
    llr = log_likelihood(k11, k12, k21, k22)

    return {
        "chisq": chisq,
        "chisq_p": p,
        "cramers_v": v,
        "odds_ratio": odds,
        "odds_ratio_direction": direction,
        "log_likelihood_ratio": llr
    }

### ---------- Cost function with lemma+POS+FEATS+deprel ---------- ###

def feature_overlap(feats1, feats2):
    if not feats1 and not feats2:
        return 0
    set1 = set(feats1.items()) if feats1 else set()
    set2 = set(feats2.items()) if feats2 else set()
    return 1 - len(set1 & set2) / max(1, len(set1 | set2))

def compute_cost(h, c):
    cost = 0

    # Lemma similarity
    if h['lemma'].lower() != c['lemma'].lower():
        cost += 1.5

    # POS penalty
    if h['upos'] != c['upos']:
        cost += 1

    # Dependency relation penalty
    if h.get('deprel') != c.get('deprel'):
        cost += 0.5

    # Morphological feature penalty
    cost += feature_overlap(h.get('feats'), c.get('feats'))

    return cost

### ---------- Hungarian alignment ---------- ###

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

### ---------- Main comparison ---------- ###

def compare_sentences(h_doc, c_doc):
    # Extract sentences (trees) from udapi.Document objects
    h_sentence = list(h_doc.trees)[0]
    c_sentence = list(c_doc.trees)[0]

    # Tokens as conllu-like dicts for alignment
    h_tokens = [token for token in h_sentence if not token.is_root()]
    c_tokens = [token for token in c_sentence if not token.is_root()]

    # Convert nodes to dicts for token alignment
    h_token_dicts = []
    for n in h_tokens:
        h_token_dicts.append({
            "id": n.id,
            "form": n.form,
            "lemma": n.lemma,
            "upos": n.upos,
            "feats": n.feats,
            "deprel": n.deprel
        })

    c_token_dicts = []
    for n in c_tokens:
        c_token_dicts.append({
            "id": n.id,
            "form": n.form,
            "lemma": n.lemma,
            "upos": n.upos,
            "feats": n.feats,
            "deprel": n.deprel
        })

    mapping = align_tokens(h_token_dicts, c_token_dicts)

    diffs = {
        "token_diffs": [],
        "dep_diffs": [],
        "stats": {
            "tokens_added": 0, "tokens_deleted": 0, "tokens_reordered": 0,
            "form_changes": 0, "lemma_changes": 0, "pos_changes": 0, "feat_changes": 0,
            "dep_changes": 0
        }
    }
    text_report = []

    for i, h in enumerate(h_token_dicts):
        j = mapping.get(i)
        if j is None:
            diffs["token_diffs"].append({"type": "deleted", "form": h['form'], "lemma": h['lemma']})
            text_report.append(f"- Token missing in canonical: {h['form']} ({h['lemma']})")
            diffs["stats"]["tokens_deleted"] += 1
            continue

        c = c_token_dicts[j]
        if i != j:
            diffs["token_diffs"].append({"type": "reordered", "form": h['form'], "from": i+1, "to": j+1})
            text_report.append(f"* Token reordered: {h['form']} (pos {i+1} → {j+1})")
            diffs["stats"]["tokens_reordered"] += 1

        if h['form'] != c['form']:
            diffs["token_diffs"].append({"type": "form_change", "from": h['form'], "to": c['form']})
            text_report.append(f"* FORM: {h['form']} → {c['form']}")
            diffs["stats"]["form_changes"] += 1
        if h['lemma'] != c['lemma']:
            diffs["token_diffs"].append({"type": "lemma_change", "from": h['lemma'], "to": c['lemma']})
            text_report.append(f"* LEMMA: {h['lemma']} → {c['lemma']}")
            diffs["stats"]["lemma_changes"] += 1
        if h['upos'] != c['upos']:
            diffs["token_diffs"].append({"type": "pos_change", "form": h['form'], "from": h['upos'], "to": c['upos']})
            text_report.append(f"* POS: {h['form']} {h['upos']} → {c['upos']}")
            diffs["stats"]["pos_changes"] += 1
        if h['feats'] != c['feats']:
            diffs["token_diffs"].append({"type": "feat_change", "form": h['form'], "from": h['feats'], "to": c['feats']})
            text_report.append(f"* FEATS: {h['form']} {h['feats']} → {c['feats']}")
            diffs["stats"]["feat_changes"] += 1

    mapped_c = {j for j in mapping.values() if j is not None}
    for j, c in enumerate(c_token_dicts):
        if j not in mapped_c:
            diffs["token_diffs"].append({"type": "added", "form": c['form'], "lemma": c['lemma']})
            text_report.append(f"+ Token added in canonical: {c['form']} ({c['lemma']})")
            diffs["stats"]["tokens_added"] += 1

    # Dependency diffs
    for i, h in enumerate(h_tokens):
        j = mapping.get(i)
        if j is None or j >= len(c_tokens):
            continue
        c = c_tokens[j]
        # Compare parent form and deprel
        if h.parent.form != c.parent.form or h.deprel != c.deprel:
            diffs["dep_diffs"].append({
                "form": h.form,
                "old_head": h.parent.form, "old_rel": h.deprel,
                "new_head": c.parent.form, "new_rel": c.deprel
            })
            text_report.append(f"* DEP: {h.form} {h.parent.form}({h.deprel}) → {c.parent.form}({c.deprel})")
            diffs["stats"]["dep_changes"] += 1

    # Advanced stats
    total_h = len(h_token_dicts)
    total_c = len(c_token_dicts)
    diffs["advanced_stats"] = {}
    for evt, count in diffs["stats"].items():
        ev = compute_event_stats({"headline": count, "canonical": count}, total_h, total_c)
        diffs["advanced_stats"][evt] = ev

    return diffs, text_report

### ---------- Example usage ---------- ###

if __name__ == "__main__":
    headline = "/mnt/d/projects/Bhaashik/ReducedToCanonicalConvDiff/headline.conllu"
    canonical = "/mnt/d/projects/Bhaashik/ReducedToCanonicalConvDiff/canonical.conllu"

    h_doc = udapi.Document(headline)
    c_doc = udapi.Document(canonical)

    diffs, text = compare_sentences(h_doc, c_doc)

    print("==== Plain Text Diff ====")
    print("\n".join(text))
    print("\n==== JSON Diff + Stats ====")
    print(json.dumps(diffs, indent=2))
