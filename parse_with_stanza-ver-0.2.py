import stanza

def load_stanza_pipeline():
    stanza.download('en', package='combined')
    return stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse,constituency', use_gpu=False)

def process_file(input_file, dep_output, const_output):
    pipeline = load_stanza_pipeline()

    with open(input_file, 'r', encoding='utf-8') as f:
        sentences = [line.strip() for line in f if line.strip()]

    with open(dep_output, 'w', encoding='utf-8') as dep_out, open(const_output, 'w', encoding='utf-8') as const_out:
        for i, sentence in enumerate(sentences):
            doc = pipeline(sentence)
            # Write the full CoNLL-U format for the sentence
            dep_out.write(f"# sent_id = {i+1}\n")
            dep_out.write(f"# text = {sentence}\n")
            dep_out.write(doc.to_conll())
            dep_out.write("\n")

            # Constituency parse for each sentence in doc
            for const_sent in doc.sentences:
                if const_sent.constituency:
                    const_out.write(f"(sentence {i+1}) {sentence}\n")
                    const_out.write(f"{const_sent.constituency.to_string()}\n\n")

