import json
from math import log
from collections import Counter
from conllu import parse
from udapi.block.read.conllu import Conllu as UdapiReader
from scipy.optimize import linear_sum_assignment
from scipy.stats import chi2_contingency
from io import StringIO
import tempfile

### ---------- Statistical helpers ---------- ###

def read_conllu_with_udapi(conllu_text):
    from udapi.block.read.conllu import Conllu as UdapiReader
    import os

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".conllu") as tmp:
        tmp.write(conllu_text)
        tmp_path = tmp.name

    reader = UdapiReader()
    trees = reader.read_trees(tmp_path)

    os.unlink(tmp_path)
    return trees

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
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    mapping = {i: j if j < m and cost_matrix[i][j] < 3 else None for i,j in zip(row_ind, col_ind)}
    return mapping

### ---------- Main comparison ---------- ###

def compare_sentences(headline_conllu, canonical_conllu):
    h_sent = parse(headline_conllu)[0]
    c_sent = parse(canonical_conllu)[0]

    h_tokens = [tok for tok in h_sent if isinstance(tok["id"], int)]
    c_tokens = [tok for tok in c_sent if isinstance(tok["id"], int)]
    mapping = align_tokens(h_tokens, c_tokens)

    diffs = {
        "token_diffs": [],
        "dep_diffs": [],
        "stats": {"tokens_added": 0, "tokens_deleted": 0, "tokens_reordered": 0,
                  "form_changes": 0, "lemma_changes": 0, "pos_changes": 0, "feat_changes": 0,
                  "dep_changes": 0}
    }
    text_report = []

    for i, h in enumerate(h_tokens):
        j = mapping.get(i)
        if j is None:
            diffs["token_diffs"].append({"type": "deleted", "form": h['form'], "lemma": h['lemma']})
            text_report.append(f"- Token missing in canonical: {h['form']} ({h['lemma']})")
            diffs["stats"]["tokens_deleted"] += 1
            continue

        c = c_tokens[j]
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
    for j, c in enumerate(c_tokens):
        if j not in mapped_c:
            diffs["token_diffs"].append({"type": "added", "form": c['form'], "lemma": c['lemma']})
            text_report.append(f"+ Token added in canonical: {c['form']} ({c['lemma']})")
            diffs["stats"]["tokens_added"] += 1

    # Dependency diffs
#    h_doc = UdapiReader().read_string(headline_conllu)
#    c_doc = UdapiReader().read_string(canonical_conllu)
#    h_nodes = [n for n in h_doc[0].nodes if not n.is_root()]
#    c_nodes = [n for n in c_doc[0].nodes if not n.is_root()]

#    h_doc = UdapiReader().read_trees(StringIO(headline_conllu))
#    c_doc = UdapiReader().read_trees(StringIO(canonical_conllu))
#    h_nodes = [n for n in h_doc[0].nodes if not n.is_root()]
#    c_nodes = [n for n in c_doc[0].nodes if not n.is_root()]

#    h_doc = UdapiReader().from_string(headline_conllu)
#    c_doc = UdapiReader().from_string(canonical_conllu)
#    h_doc = UdapiReader().read_trees(StringIO(headline_conllu))
#    c_doc = UdapiReader().read_trees(StringIO(canonical_conllu))

    h_doc = read_conllu_with_udapi(headline_conllu)
    c_doc = read_conllu_with_udapi(canonical_conllu)

    h_nodes = [n for n in h_doc[0].nodes if not n.is_root()]
    c_nodes = [n for n in c_doc[0].nodes if not n.is_root()]


    for i, h in enumerate(h_nodes):
        j = mapping.get(i)
        if j is None or j >= len(c_nodes):
            continue
        c = c_nodes[j]
        if h.parent.form != c.parent.form or h.deprel != c.deprel:
            diffs["dep_diffs"].append({
                "form": h.form,
                "old_head": h.parent.form, "old_rel": h.deprel,
                "new_head": c.parent.form, "new_rel": c.deprel
            })
            text_report.append(f"* DEP: {h.form} {h.parent.form}({h.deprel}) → {c.parent.form}({c.deprel})")
            diffs["stats"]["dep_changes"] += 1

    # Advanced stats
    total_h = len(h_tokens)
    total_c = len(c_tokens)
    diffs["advanced_stats"] = {}
    for evt, count in diffs["stats"].items():
        ev = compute_event_stats({"headline": count, "canonical": count}, total_h, total_c)
        diffs["advanced_stats"][evt] = ev

    return diffs, text_report

### ---------- Example usage ---------- ###

if __name__ == "__main__":
    headline = """# sent_id = 1
# text = Govt announces new policy
1	Govt	govt	PROPN	_	Number=Sing	2	nsubj	_	_
2	announces	announce	VERB	_	Tense=Pres	0	root	_	_
3	new	new	ADJ	_	Degree=Pos	4	amod	_	_
4	policy	policy	NOUN	_	Number=Sing	2	obj	_	_
"""

    canonical = """# sent_id = 1
# text = The government has announced a new policy.
1	The	the	DET	_	Definite=Def	2	det	_	_
2	government	government	NOUN	_	Number=Sing	3	nsubj	_	_
3	has	have	AUX	_	Tense=Pres	4	aux	_	_
4	announced	announce	VERB	_	Tense=Past	0	root	_	_
5	a	a	DET	_	Definite=Ind	6	det	_	_
6	new	new	ADJ	_	Degree=Pos	7	amod	_	_
7	policy	policy	NOUN	_	Number=Sing	4	obj	_	_
8	.	.	PUNCT	_	_	4	punct	_	_
"""

    diffs, text = compare_sentences(headline, canonical)

    print("==== Plain Text Diff ====")
    print("\n".join(text))
    print("\n==== JSON Diff + Stats ====")
    print(json.dumps(diffs, indent=2))

