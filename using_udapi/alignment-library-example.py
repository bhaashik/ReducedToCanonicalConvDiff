from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

# Tokenize sentences as lists of strings (can use words, lemmas, etc.)
canonical = Sequence('the government announced a new policy today'.split())
headline  = Sequence('govt announced new policy'.split())

# Define a vocabulary and encode tokens as integers for efficient alignment
vocab = Vocabulary()
enc_canonical = vocab.encodeSequence(canonical)
enc_headline  = vocab.encodeSequence(headline)

# Set up scoring: match=2, mismatch=-1, gap=-2 (customizable to your task)
scoring = SimpleScoring(2, -1)
aligner = GlobalSequenceAligner(scoring, gap=-2)

# Run global alignment
score, alignments = aligner.align(enc_canonical, enc_headline, backtrace=True)

# Iterate over (possibly multiple optimal) alignments
for alignment in alignments:
    # Decode the SequenceAlignment object into readable output
    decoded = vocab.decodeSequenceAlignment(alignment)
    print(decoded)
    print("Score:", alignment.score)
    print("Percent identity:", alignment.percentIdentity())
    # Alignment info is available in decoded.alignment (list of (can_idx, hed_idx))

