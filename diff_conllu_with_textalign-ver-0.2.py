import csv
from conllu import parse_incr
from collections import Counter, defaultdict
#import textalign
#from textalign.aligner import TextAligner
from textalign.aligner import Aligner
from textalign.scoring import SimpleScoring

def load_sentences(conllu_path):
    """Load all sentences from a CoNLL-U file as conllu Sentence objects."""
    with open(conllu_path, 'r', encoding='utf-8') as f:
        return list(parse_incr(f))

def extract_tokens(sentence):
    """Extract relevant info from each token in a sentence (skip multiword tokens)."""
    tokens = []
    for token in sentence:
        # Only include regular tokens (integer IDs), skip multiword tokens
        if isinstance(token['id'], int):
            lemma = token['lemma'] or token['form']
            tokens.append({
                'form': token['form'],
                'lemma': lemma.lower(),
                'upostag': token.get('upostag', ''),
                'feats': token.get('feats') or {},
                'deprel': token.get('deprel', ''),
                'head': token.get('head', 0),     # integer, 0=root
                'id': token['id']                 # 1-based index
            })
    return tokens

#def align_tokens_textalign(can_tokens, red_tokens):
#    """Use textalign for global token alignment on lemmas; returns list of (can_idx, red_idx) pairs."""
#    can_seq = [t['lemma'] for t in can_tokens]
#    red_seq = [t['lemma'] for t in red_tokens]
#
#    aligner = textalign.GlobalSequenceAligner(
#        can_seq, red_seq,
#        match_score=2,
#        mismatch_score=-1,
#        gap_score=-1,
#        alphabet=None  # all tokens from input sequences
#    )
#    alignment = aligner.align()
#
#    # alignment.alignedPairs is a list of (can_idx or -1, red_idx or -1)
#    aligned_pairs = alignment.alignedPairs
#
#    return aligned_pairs


#def align_tokens_textalign(can_tokens, red_tokens):
#    """
#    Aligns canonical and headline token lists using TextAligner by lemma (lowercased).
#    Returns: list of (can_idx or -1, red_idx or -1) alignment pairs.
#    """
#    can_seq = [t['lemma'] for t in can_tokens]
#    red_seq = [t['lemma'] for t in red_tokens]
#
#    # Set up alignment parameters: match=2, mismatch=-1, gap=-1 (can modify as needed)
#    aligner = Aligner(match=2, mismatch=-1, gap=-1)
#    score, trace = aligner.align(can_seq, red_seq)
#    alignment = aligner.trace2alignment(trace)
#    # Each element: (can_idx or None, red_idx or None)
#
#    # Replace None with -1 for backward compatibility if needed
#    aligned_pairs = []
#    for can_idx, red_idx in alignment:
#        ci = can_idx if can_idx is not None else -1
#        ri = red_idx if red_idx is not None else -1
#        aligned_pairs.append((ci, ri))
#    return aligned_pairs


def align_tokens_textalign(can_tokens, red_tokens):
    can_seq = [t['lemma'] for t in can_tokens]
    red_seq = [t['lemma'] for t in red_tokens]

    # Create a scoring scheme. For example: 2 for match, -1 for mismatch, -2 for gap penalty
    scoring = SimpleScoring(match_score=2, mismatch_score=-1, gap_score=-2)

    # Initialize aligner with scoring
    aligner = Aligner(scoring)

    # Run alignment
    score, trace = aligner.align(can_seq, red_seq)

    # Get alignment pairs
    alignment = aligner.trace2alignment(trace)

    # Convert None to -1 for easier handling downstream
    aligned_pairs = []
    for can_idx, red_idx in alignment:
        ci = can_idx if can_idx is not None else -1
        ri = red_idx if red_idx is not None else -1
        aligned_pairs.append((ci, ri))

    return aligned_pairs


def extract_diffs(can_tokens, red_tokens, aligned_pairs):
    """Extract detailed diffs of syntactic features and reorderings based on aligned tokens."""
    diffs = {
        'omitted_in_headline': [],   # canonical tokens not aligned to any headline token
        'inserted_in_headline': [],  # headline tokens not aligned to any canonical token
        'pos_diff': [],              # list of (token_form, canonical_POS, headline_POS)
        'deprel_diff': [],           # list of (token_form, canonical_deprel, headline_deprel)
        'head_diff': [],             # list of (token_form, canonical_head, headline_head)
        'feats_diff': [],            # list of (token_form, canonical_feats, headline_feats)
        'reordered_tokens': []       # list of (token_form, canonical_pos, headline_pos)
    }

    # Maps for alignment indexing: canonical idx -> headline idx and vice versa
    can_to_red = {}
    red_to_can = {}

    for c_idx, r_idx in aligned_pairs:
        if c_idx != -1:
            can_to_red[c_idx] = r_idx
        if r_idx != -1:
            red_to_can[r_idx] = c_idx

    # Omitted (canonical tokens unaligned)
    omitted = [can_tokens[i]['form'] for i in range(len(can_tokens)) if can_to_red.get(i, -1) == -1]
    diffs['omitted_in_headline'].extend(omitted)

    # Inserted (headline tokens unaligned)
    inserted = [red_tokens[i]['form'] for i in range(len(red_tokens)) if red_to_can.get(i, -1) == -1]
    diffs['inserted_in_headline'].extend(inserted)

    # Compare aligned tokens feature-wise
    for c_idx, r_idx in aligned_pairs:
        if c_idx == -1 or r_idx == -1:
            continue

        c_token = can_tokens[c_idx]
        r_token = red_tokens[r_idx]

        # POS tag diff
        if c_token['upostag'] != r_token['upostag']:
            diffs['pos_diff'].append((c_token['form'], c_token['upostag'], r_token['upostag']))

        # Deprel diff
        if c_token['deprel'] != r_token['deprel']:
            diffs['deprel_diff'].append((c_token['form'], c_token['deprel'], r_token['deprel']))

        # Feats diff
        if c_token['feats'] != r_token['feats']:
            diffs['feats_diff'].append((c_token['form'], c_token['feats'], r_token['feats']))

        # Head diff:
        # Heads are token IDs (1-based), 0 means root
        # Need to map canonical head ID through alignment to headline head ID position
        c_head = c_token['head']
        r_head = r_token['head']

        def canon_head_to_red_head(c_head):
            if c_head == 0:
                return 0  # ROOT
            else:
                c_head_idx = c_head - 1
                return can_to_red.get(c_head_idx, -1) + 1 if (can_to_red.get(c_head_idx, -1) != -1) else -1

        mapped_c_head = canon_head_to_red_head(c_head)

        if mapped_c_head != r_head:
            diffs['head_diff'].append((c_token['form'], c_head, r_head))

        # Reordering: token is considered reordered if its aligned indices differ
        if c_idx != r_idx:
            diffs['reordered_tokens'].append((c_token['form'], c_idx + 1, r_idx + 1))  # +1 for 1-based index reporting

    return diffs

def main(headlines_path, canonical_path, output_csv="pairwise_diffs_textalign.csv"):
    headline_sents = load_sentences(headlines_path)
    canonical_sents = load_sentences(canonical_path)

    assert len(headline_sents) == len(canonical_sents), "Number of sentences does not match."

    pair_diffs_rows = []
    freq_counters = defaultdict(Counter)

    for i, (red_sent, can_sent) in enumerate(zip(headline_sents, canonical_sents)):
        pair_id = f"sent{i+1:05d}"
        can_tokens = extract_tokens(can_sent)
        red_tokens = extract_tokens(red_sent)

        aligned_pairs = align_tokens_textalign(can_tokens, red_tokens)
        diffs = extract_diffs(can_tokens, red_tokens, aligned_pairs)

        # Update global counters
        freq_counters['omitted'].update(diffs['omitted_in_headline'])
        freq_counters['inserted'].update(diffs['inserted_in_headline'])
        freq_counters['pos_diff'].update([f"{w}:{c}->{r}" for w, c, r in diffs['pos_diff']])
        freq_counters['deprel_diff'].update([f"{w}:{c}->{r}" for w, c, r in diffs['deprel_diff']])
        freq_counters['feats_diff'].update([f"{w}:{str(c)}->{str(r)}" for w, c, r in diffs['feats_diff']])
        freq_counters['head_diff'].update([f"{w}:{c}->{r}" for w, c, r in diffs['head_diff']])
        freq_counters['reordered_tokens'].update([f"{w}:{c}->{r}" for w, c, r in diffs['reordered_tokens']])

        pair_diffs_rows.append({
            "pair_id": pair_id,
            "omitted_in_headline": ";".join(diffs['omitted_in_headline']),
            "inserted_in_headline": ";".join(diffs['inserted_in_headline']),
            "pos_diff": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['pos_diff']]),
            "deprel_diff": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['deprel_diff']]),
            "feats_diff": ";".join([f"{w}:{str(c)}->{str(r)}" for w, c, r in diffs['feats_diff']]),
            "head_diff": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['head_diff']]),
            "reordered_tokens": ";".join([f"{w}:{c}->{r}" for w, c, r in diffs['reordered_tokens']])
        })

    # Write CSV for pairwise diffs
    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        fieldnames = [
            "pair_id", "omitted_in_headline", "inserted_in_headline",
            "pos_diff", "deprel_diff", "feats_diff", "head_diff", "reordered_tokens"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pair_diffs_rows)

    print(f"\nPairwise differences saved to: {output_csv}\n")

    # Print corpus-level frequency summaries
    print("=== Corpus-level summary of differences ===")
    for feat, counter in freq_counters.items():
        print(f"\nTop 10 most frequent differences in feature '{feat}':")
        for val, count in counter.most_common(10):
            print(f"  {val}: {count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare reduced (headline) and canonical CoNLL-U parses with token alignment (textalign).")
    parser.add_argument('--headline', required=True, help="Path to reduced/headline CoNLL-U file")
    parser.add_argument('--canonical', required=True, help="Path to canonical CoNLL-U file")
    parser.add_argument('--output_csv', default="pairwise_diffs_textalign.csv", help="Output CSV for per-pair differences")

    args = parser.parse_args()
    main(args.headline, args.canonical, args.output_csv)

