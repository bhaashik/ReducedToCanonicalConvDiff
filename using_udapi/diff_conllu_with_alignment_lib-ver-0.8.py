import csv
from collections import Counter, defaultdict
from conllu import parse_incr
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

def extract_tokens(sentence):
    """
    Extract tokens from a conllu sentence, skipping multiword tokens.
    Returns: list of token dicts with lemma (lowercased), form, POS, head, deprel, feats, id.
    """
    tokens = []
    for token in sentence:
        if isinstance(token['id'], int):
            lemma = token.get('lemma') or token['form']
            tokens.append({
                'form': token['form'],
                'lemma': lemma.lower(),
                'upostag': token.get('upostag', ''),
                'feats': token.get('feats') or {},
                'deprel': token.get('deprel', ''),
                'head': token.get('head', 0),
                'id': token['id']
            })
    return tokens

def align_tokens(can_tokens, red_tokens, match_score=2, mismatch_score=-1, gap_score=-2):
    """
    Align tokens of two sentences by lemma using the alignment library.
    Uses a fresh Vocabulary instance per sentence pair for consistent local encoding.
    Returns list of (can_idx or None, red_idx or None) alignment pairs.
    """
    vocab = Vocabulary()  # Fresh vocab per sentence pair

    can_seq = Sequence([t['lemma'] for t in can_tokens])
    red_seq = Sequence([t['lemma'] for t in red_tokens])

    enc_can = vocab.encodeSequence(can_seq)
    enc_red = vocab.encodeSequence(red_seq)

    scoring = SimpleScoring(match_score, mismatch_score)
    aligner = GlobalSequenceAligner(scoring, gap_score)

    score, alignments = aligner.align(enc_can, enc_red, backtrace=True)

    alignment = alignments[0]  # best alignment

    alignment_path = [
        (i if i != -1 else None, j if j != -1 else None)
        for i, j in zip(alignment.first, alignment.second)
    ]

    return alignment_path

def extract_diffs(can_tokens, red_tokens, alignment_path):
    """
    Given tokens and the alignment path (list of (can_idx or None, red_idx or None)),
    extract differences: omissions, insertions, POS/DEPREL/HEAD/FEATS diffs, reorderings.
    Handles out-of-range indices safely.
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

    can_to_red = {}
    red_to_can = {}

    for can_idx, red_idx in alignment_path:
        if can_idx is not None:
            can_to_red[can_idx] = red_idx
        if red_idx is not None:
            red_to_can[red_idx] = can_idx

    for can_idx, red_idx in alignment_path:
        if can_idx is not None and red_idx is not None:
            if not (0 <= can_idx < len(can_tokens)):
                print(f"Warning: canonical index {can_idx} out of range (len {len(can_tokens)})")
                continue
            if not (0 <= red_idx < len(red_tokens)):
                print(f"Warning: headline index {red_idx} out of range (len {len(red_tokens)})")
                continue

            c = can_tokens[can_idx]
            r = red_tokens[red_idx]

            if c['upostag'] != r['upostag']:
                diffs['pos_diff'].append((c['form'], c['upostag'], r['upostag']))

            if c['deprel'] != r['deprel']:
                diffs['deprel_diff'].append((c['form'], c['deprel'], r['deprel']))

            if c['feats'] != r['feats']:
                diffs['feats_diff'].append((c['form'], c['feats'], r['feats']))

            c_head = c['head']
            r_head = r['head']

            # Map canonical head token index (1-based ID) to headline token index (0-based)
            if c_head == 0 and r_head == 0:
                pass
            else:
                c_head_idx = c_head - 1 if c_head > 0 else None
                mapped_head = can_to_red.get(c_head_idx)

                if mapped_head is None:
                    diffs['head_diff'].append((c['form'], c_head, r_head))
                else:
                    if mapped_head != (r_head - 1):
                        diffs['head_diff'].append((c['form'], c_head, r_head))

            # Detect reorderings based on token indices
            if can_idx != red_idx:
                diffs['reordered_tokens'].append((c['form'], can_idx + 1, red_idx + 1))

        elif can_idx is not None and red_idx is None:
            if 0 <= can_idx < len(can_tokens):
                diffs['omitted_in_headline'].append(can_tokens[can_idx]['form'])

        elif red_idx is not None and can_idx is None:
            if 0 <= red_idx < len(red_tokens):
                diffs['inserted_in_headline'].append(red_tokens[red_idx]['form'])

    return diffs

def main(headlines_path, canonical_path, output_csv="pairwise_diffs.csv"):
    with open(headlines_path, 'r', encoding='utf-8') as fh, open(canonical_path, 'r', encoding='utf-8') as fc:
        headline_sents = list(parse_incr(fh))
        canonical_sents = list(parse_incr(fc))

    if len(headline_sents) != len(canonical_sents):
        raise ValueError(f"Sentence counts differ: headlines={len(headline_sents)}, canonical={len(canonical_sents)}")

    print(f"Processing {len(headline_sents)} sentence pairs ...")

    overall_counters = defaultdict(Counter)
    output_rows = []

    for idx, (head_sent, can_sent) in enumerate(zip(headline_sents, canonical_sents), start=1):
        can_tokens = extract_tokens(can_sent)
        red_tokens = extract_tokens(head_sent)

        alignment_path = align_tokens(can_tokens, red_tokens)

        diffs = extract_diffs(can_tokens, red_tokens, alignment_path)

        # Track global differences frequencies
        overall_counters['omitted'].update(diffs['omitted_in_headline'])
        overall_counters['inserted'].update(diffs['inserted_in_headline'])
        overall_counters['pos_diff'].update([f"{w}:{c}->{r}" for w, c, r in diffs['pos_diff']])
        overall_counters['deprel_diff'].update([f"{w}:{c}->{r}" for w, c, r in diffs['deprel_diff']])
        overall_counters['feats_diff'].update([f"{w}:{str(c)}->{str(r)}" for w, c, r in diffs['feats_diff']])
        overall_counters['head_diff'].update([f"{w}:{c}->{r}" for w, c, r in diffs['head_diff']])
        overall_counters['reordered_tokens'].update([f"{w}:{c}->{r}" for w, c, r in diffs['reordered_tokens']])

        pair_id = f"sent{idx:05d}"

        output_rows.append({
            "pair_id": pair_id,
            "omitted_in_headline": ";".join(diffs['omitted_in_headline']),
            "inserted_in_headline": ";".join(diffs['inserted_in_headline']),
            "pos_diff": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['pos_diff']]),
            "deprel_diff": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['deprel_diff']]),
            "feats_diff": ";".join([f"{w}:{str(c)}->{str(r)}" for w, c, r in diffs['feats_diff']]),
            "head_diff": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['head_diff']]),
            "reordered_tokens": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['reordered_tokens']])
        })

    # Write CSV output
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ["pair_id", "omitted_in_headline", "inserted_in_headline",
                      "pos_diff", "deprel_diff", "feats_diff", "head_diff", "reordered_tokens"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nPairwise differences saved to: {output_csv}")

    # Print corpus-level summaries
    print("\n=== Corpus-level difference frequencies (top 10) ===")
    for feat, counter in overall_counters.items():
        print(f"\nFeature: {feat}")
        for val, count in counter.most_common(10):
            print(f"  {val}: {count}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Compare reduced and canonical CoNLL-U parses with token alignment and detailed diffs.")
    parser.add_argument('--headline', required=True, help="Path to reduced (headline) CoNLL-U file")
    parser.add_argument('--canonical', required=True, help="Path to canonical CoNLL-U file")
    parser.add_argument('--output_csv', default='pairwise_diffs.csv', help="Output CSV path")
    args = parser.parse_args()

    main(args.headline, args.canonical, args.output_csv)

