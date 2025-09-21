from conllu import parse_incr

def count_sentences(conllu_file):
    with open(conllu_file, "r", encoding="utf-8") as f:
        return sum(1 for _ in parse_incr(f))

headline_file = "data/dependency-parsed/Hindustan-Times-2019-cleaned-orig-all-stanza-parsed-deps.conllu"
canonical_file = "data/dependency-parsed/Hindustan-Times-only-canonical-with-numbering-all-1148-stanza-parsed-deps.conllu"

print("Headline sentences:", count_sentences(headline_file))
print("Canonical sentences:", count_sentences(canonical_file))

