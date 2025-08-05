from conllu import parse_incr
#from text_alignment_tool.alignment import Alignment
#from text_alignment_tool.token import Token
from text_alignment_tool import Alignment
from text_alignment_tool import Token
import csv
from collections import Counter, defaultdict

def extract_tokens(sentence):
    """Extract tokens as dicts from a CONLL-U sentence (skip multiword tokens)."""
    tokens = []
    for tok in sentence:
        # Skip multiword tokens (id can be int or tuple)
        if isinstance(tok['id'], int):
            lemma = (tok.get('lemma') or tok['form']).lower()
            tokens.append({
                'form': tok['form'],
                'lemma': lemma,
                'upostag': tok.get('upostag', ''),
                'feats': tok.get('feats') or {},
                'deprel': tok.get('deprel', ''),
                'head': tok.get('head', 0),  # integer, 0 for root
                'id': tok['id']
            })
    return tokens

def build_token_list(tokens):
    """Wrap your token dicts as text_alignment_tool.Token objects, for alignment."""
    return [Token(t['lemma']) for t in tokens]  # lemma-based; change to form if needed

def align_sentence_pair(canonical_tokens, headline_tokens):
    can_seq = build_token_list(canonical_tokens)
    red_seq = build_token_list(headline_tokens)

    # Scoring: match lemma = 1.0, else -0.5
    def match_score(t1, t2):
        return 1.0 if t1.token == t2.token else -0.5
    gap_penalty = -0.5

    alignment = Alignment(can_seq, red_seq, match_score=match_score, gap_cost=gap_penalty)
    _, path = alignment.align()  # path: list of (i or None, j or None)
    return path  # [(canonical_index or None, headline_index or None), ...]

def extract_diffs(can_tokens, red_tokens, aligned_pairs):
    """Compare by alignment path."""
    diffs = {
        'omitted_in_headline': [],
        'inserted_in_headline': [],
        'pos_diff': [],
        'deprel_diff': [],
        'head_diff': [],
        'feats_diff': [],
        'reordered_tokens': []
    }

    can_to_red = {}
    red_to_can = {}
    for pair in aligned_pairs:
        can_idx, red_idx = pair
        if can_idx is not None:
            can_to_red[can_idx] = red_idx
        if red_idx is not None:
            red_to_can[red_idx] = can_idx

    # Omitted (canonical not aligned)
    omitted = [can_tokens[i]['form'] for i in range(len(can_tokens)) if can_to_red.get(i) is None]
    diffs['omitted_in_headline'] = omitted

    # Inserted (headline not aligned)
    inserted = [red_tokens[i]['form'] for i in range(len(red_tokens)) if red_to_can.get(i) is None]
    diffs['inserted_in_headline'] = inserted

    # Compare features for matched tokens
    for can_idx, red_idx in aligned_pairs:
        if can_idx is not None and red_idx is not None:
            c = can_tokens[can_idx]
            r = red_tokens[red_idx]
            if c['upostag'] != r['upostag']:
                diffs['pos_diff'].append((c['form'], c['upostag'], r['upostag']))
            if c['deprel'] != r['deprel']:
                diffs['deprel_diff'].append((c['form'], c['deprel'], r['deprel']))
            if c['feats'] != r['feats']:
                diffs['feats_diff'].append((c['form'], c['feats'], r['feats']))
            if c['head'] != r['head']:
                diffs['head_diff'].append((c['form'], c['head'], r['head']))
            # Reordering: if indices don't match, record movement
            if can_idx != red_idx:
                diffs['reordered_tokens'].append((c['form'], can_idx+1, red_idx+1))
    return diffs

def main(headlines_file, canonical_file, output_csv="pairwise_diffs.csv"):
    with open(headlines_file, 'r', encoding='utf-8') as fh:
        headline_sents = list(parse_incr(fh))
    with open(canonical_file, 'r', encoding='utf-8') as fc:
        canonical_sents = list(parse_incr(fc))

    if len(headline_sents) != len(canonical_sents):
        raise ValueError(f"Sentence counts do not match: headlines={len(headline_sents)}, canonical={len(canonical_sents)}.")

    print(f"Processing {len(headline_sents)} sentence pairs...")

    pair_diffs_rows = []
    freq_counters = defaultdict(Counter)

    for i, (head_sent, can_sent) in enumerate(zip(headline_sents, canonical_sents)):
        can_tokens = extract_tokens(can_sent)
        red_tokens = extract_tokens(head_sent)

        aligned_pairs = align_sentence_pair(can_tokens, red_tokens)
        diffs = extract_diffs(can_tokens, red_tokens, aligned_pairs)

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

    with open(output_csv, "w", newline='', encoding='utf-8') as fcsv:
        fieldnames = [
            "pair_id", "omitted_in_headline", "inserted_in_headline",
            "pos_diff", "deprel_diff", "feats_diff", "head_diff", "reordered_tokens"
        ]
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pair_diffs_rows)
    print(f"\nPairwise differences saved to: {output_csv}")

    print("\n=== Top corpus-level difference frequencies ===")
    for feat, counter in freq_counters.items():
        print(f"\nTop 8 for '{feat}':")
        for val, count in counter.most_common(8):
            print(f"  {val}: {count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare reduced and canonical CoNLL-U parses using text-alignment-tool.")
    parser.add_argument('--headline', required=True, help="Path to reduced/headline CoNLL-U file")
    parser.add_argument('--canonical', required=True, help="Path to canonical CoNLL-U file")
    parser.add_argument('--output_csv', default="pairwise_diffs.csv", help="Output CSV for per-pair differences")
    args = parser.parse_args()
    main(args.headline, args.canonical, args.output_csv)

