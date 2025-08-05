from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

seq1 = Sequence('the government announced a new policy today'.split())
seq2 = Sequence('govt announced new policy'.split())

vocab = Vocabulary()
enc1 = vocab.encodeSequence(seq1)
enc2 = vocab.encodeSequence(seq2)

scoring = SimpleScoring(2, -1)
gap_score = -2

aligner = GlobalSequenceAligner(scoring, gap_score)

score, alignments = aligner.align(enc1, enc2, backtrace=True)

for alignment in alignments:
    print(vocab.decodeSequenceAlignment(alignment))
    print("Score:", alignment.score)
    print("Percent identity:", alignment.percentIdentity())

