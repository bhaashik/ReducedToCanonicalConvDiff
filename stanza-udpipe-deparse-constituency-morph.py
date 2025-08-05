# 🔧 Install dependencies if needed:
# pip install stanza corpy.udpipe
# stanza.download('en')

import stanza
#from corpy.udpipe import Model

import spacy_udpipe

spacy_udpipe.download("en") # download English model


# Load UDPipe English-EWT model (download manually or via filepath)
# You can download from UFAL: e.g., english-ewt-ud-2.12-200830.udpipe
#udpipe = Model("english-ewt-ud-2.12-200830.udpipe")

# Load Stanza pipeline for dependency parsing
stanza.download('en')
nlp_stanza = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')

def combine(text):
    # Output list of merged sentences (CoNLL-U)
    merged_sentences = []

    # Run both pipelines
    # UDPipe output: yields Sentence objects with full FEATS, etc.
    udpipe_sents = list(udpipe.process(text, tag=True, parse=True, out_format="conllu"))

    # Stanza processing for dependency
    doc_stanza = nlp_stanza(text)
    stanza_sents = doc_stanza.sentences

    assert len(udpipe_sents) == len(stanza_sents), "Sentence count mismatch!"

    for udp_sent, st_sent in zip(udpipe_sents, stanza_sents):
        # Parse UDPipe sentence lines
        lines = [l for l in udp_sent.strip().split("\n") if l and not l.startswith("#")]

        output_lines = []
        for udp_line, st_word in zip(lines, st_sent.words):
            cols = udp_line.split("\t")
            # cols: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC

            # Replace HEAD and DEPREL with Stanza values
            cols[6] = str(st_word.head)
            cols[7] = st_word.deprel

            output_lines.append("\t".join(cols))

        merged_sentences.append("\n".join(output_lines))

    # Combine and return
    return "\n\n".join(merged_sentences) + "\n"

if __name__ == "__main__":
    text = "All human beings are born free and equal in dignity and rights. I like trains."
    conllu = combine(text)
    print(conllu)

