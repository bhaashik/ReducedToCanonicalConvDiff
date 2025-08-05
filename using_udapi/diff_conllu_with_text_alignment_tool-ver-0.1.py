from conllu import parse_incr
from text_alignment_tool import AlignmentBuilder, Token
import csv
from collections import Counter, defaultdict

def extract_tokens(sentence):
    """
    Returns list of dicts with form, lemma, upostag, fea, deprel, head, id for each token in a CoNLL-U sentence.
    """
    tokens = []
    for tok in sentence:
        if isinstance(tok['id'], int):
            lemma = tok['lemma'] or tok['form']
            tokens.append({
                'form': tok['form'],
                'lemma': lemma.lower(),
                'upostag': tok.get('upostag', ''),
                'feats': tok.get('feats') or {},
                'deprel': tok.get('deprel', ''),
                'head': tok.get('head', 0),  # integer, 0 for root
                'id': tok['id']
            })
    return tokens

def build_token_list(tokens):
    """
    Map your token dicts to text_alignment_tool.Token objects (used for alignment).
    Align on lemma (lowercased), but store surface form for reporting.
    """
    return [Token(t['lemma'], text=t['form']) for t in tokens]

def align_sentence_pair(canonical_tokens, headline_tokens):
    can_seq = build_token_list(canonical_tokens)
    red_seq = build_token_list(headline_tokens)

    builder = AlignmentBuilder()
    # Simple match: token text exact match = 1, else -1 (customize as needed for your needs)
    def match_score(t1, t2):
        return 1.0 if t1.text == t2.text else -1.0
    gap_penalty = -0.5

    alignment = builder.create_alignment(
        can_seq, red_seq,
        match_score=match_score,
        gap_cost=gap_penalty
    )
    alignment.run()
    # Each aligned pair: (index into can_seq or None, index into red_seq or None)
    return alignment.aligned_pairs

def extract_diffs(can_tokens, red_tokens, aligned_pairs):
    """
    Given tokens from both sentences and the aligned_pairs, extract all key differences.
    """
    diffs = {
        'omitted_in_headline': [],
        'inserted_in_headline': [],
        'pos_diff': [],
        'deprel_diff': [],
        'head_diff': [],
        'feats_diff': [],
        'reordered_tokens': []
    }

    # Build maps for quick lookup
    can_to_red = {}
    red_to_can = {}

    for i, (can_idx, red_idx) in enumerate(aligned_pairs):
        if can_idx is not None:
            can_to_red[can_idx] = red_idx
        if red_idx is not None:
            red_to_can[red_idx] = can_idx

    # Omitted (canonical tokens without alignment)
    omitted = [can_tokens[i]['form'] for i in range(len(can_tokens)) if can_to_red.get(i) is None]
    diffs['omitted_in_headline'] = omitted
    # Inserted (headline tokens without alignment)
    inserted = [red_tokens[i]['form'] for i in range(len(red_tokens)) if red_to_can.get(i) is None]
    diffs['inserted_in_headline'] = inserted

    # Compare matched tokens feature-wise
    for pair in aligned_pairs:
        can_idx, red_idx = pair
        if can_idx is not None and red_idx is not None:
            c_token = can_tokens[can_idx]
            r_token = red_tokens[red_idx]
            if c_token['upostag'] != r_token['upostag']:
                diffs['pos_diff'].append((c_token['form'], c_token['upostag'], r_token['upostag']))
            if c_token['deprel'] != r_token['deprel']:
                diffs['deprel_diff'].append((c_token['form'], c_token['deprel'], r_token['deprel']))
            if c_token['feats'] != r_token['feats']:
                diffs['feats_diff'].append((c_token['form'], c_token['feats'], r_token['feats']))
            # Head diff: best effort (head is token id, so we check if the alignment moves the head's referent)
            if c_token['head'] != r_token['head']:
                diffs['head_diff'].append((c_token['form'], c_token['head'], r_token['head']))
            # Reordering: check if aligned token has moved in position
            if can_idx != red_idx:
                diffs['reordered_tokens'].append((c_token['form'], can_idx+1, red_idx+1))
    return diffs

def main(headlines_file, canonical_file, output_csv="pairwise_diffs.csv"):
    with open(headlines_file, 'r', encoding='utf-8') as fh:
        headline_sents = list(parse_incr(fh))
    with open(canonical_file, 'r', encoding='utf-8') as fc:
        canonical_sents = list(parse_incr(fc))

    assert len(headline_sents) == len(canonical_sents), "Sentence counts do not match!"

    print(f"Aligned processing of {len(headline_sents)} sentence pairs...")

    pair_diffs_rows = []
    freq_counters = defaultdict(Counter)

    for i, (head_sent, can_sent) in enumerate(zip(headline_sents, canonical_sents)):
        can_tokens = extract_tokens(can_sent)
        red_tokens = extract_tokens(head_sent)
        aligned_pairs = align_sentence_pair(can_tokens, red_tokens)
        diffs = extract_diffs(can_tokens, red_tokens, aligned_pairs)
        # Global aggregates
        freq_counters['omitted'].update(diffs['omitted_in_headline'])
        freq_counters['inserted'].update(diffs['inserted_in_headline'])
        freq_counters['pos_diff'].update([f"{w}:{c}->{r}" for w,c,r in diffs['pos_diff']])
        freq_counters['deprel_diff'].update([f"{w}:{c}->{r}" for w,c,r in diffs['deprel_diff']])
        freq_counters['feats_diff'].update([f"{w}:{str(c)}->{str(r)}" for w,c,r in diffs['feats_diff']])
        freq_counters['head_diff'].update([f"{w}:{c}->{r}" for w,c,r in diffs['head_diff']])
        freq_counters['reordered_tokens'].update([f"{w}:{c}->{r}" for w,c,r in diffs['reordered_tokens']])

        pair_id = f"sent{i+1:05d}"
        pair_diffs_rows.append({
            "pair_id": pair_id,
            "omitted_in_headline": ";".join(diffs['omitted_in_headline']),
            "inserted_in_headline": ";".join(diffs['inserted_in_headline']),
            "pos_diff": ";".join([f"{w}:{c}->{r}" for w,c,r in diffs['pos_diff']]),
            "deprel_diff": ";".join([f"{w}:{c}->{r}" for w,c,r in diffs['deprel_diff']]),
            "feats_diff": ";".join([f"{w}:{str(c)}->{str(r)}" for w,c,r in diffs['feats_diff']]),
            "head_diff": ";".join([f"{w}:{c}->{r}" for w,c,r in diffs['head_diff']]),
            "reordered_tokens": ";".join([f"{w}:{c}->{r}" for w,c,r in diffs['reordered_tokens']])
        })

    # Write CSV for pairwise diffs
    with open(output_csv, "w", newline='', encoding='utf-8') as fcsv:
        fieldnames = [
            "pair_id", "omitted_in_headline", "inserted_in_headline",
            "pos_diff", "deprel_diff", "feats_diff", "head_diff", "reordered_tokens"
        ]
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pair_diffs_rows)
    print(f"\nPairwise differences saved to: {output_csv}")

    # Print top corpus-level frequency summaries
    print("\n=== Top corpus-level difference frequencies ===")
    for feat, counter in freq_counters.items():
        print(f"\nTop 8 for '{feat}':")
        for val, count in counter.most_common(8):
            print(f"  {val}: {count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare reduced and canonical CoNLL-U parses using text_alignment_tool.")
    parser.add_argument('--headline', required=True, help="Path to reduced/headline CoNLL-U file")
    parser.add_argument('--canonical', required=True, help="Path to canonical CoNLL-U file")
    parser.add_argument('--output_csv', default="pairwise_diffs.csv", help="Output CSV for per-pair differences")
    args = parser.parse_args()
    main(args.headline, args.canonical, args.output_csv)

