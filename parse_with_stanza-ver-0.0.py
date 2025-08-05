import stanza
from pathlib import Path

def load_stanza_pipeline():
    # Download if not present
    stanza.download('en', package='combined')  # combined = pos + depparse + constituency
    return stanza.Pipeline(lang='en', processors='tokenize,pos,depparse,constituency', use_gpu=False)

def process_file(input_path, dep_output_path, const_output_path):
    pipeline = load_stanza_pipeline()
    text = Path(input_path).read_text(encoding='utf-8')
    doc = pipeline(text)

    with open(dep_output_path, 'w', encoding='utf-8') as dep_out, \
         open(const_output_path, 'w', encoding='utf-8') as const_out:

        for i, sentence in enumerate(doc.sentences):
            # Dependency output in CoNLL-U format
            dep_out.write(sentence.to_conll())
            dep_out.write("\n")  # Separate sentences

            # Constituency tree as bracketed string
            if sentence.constituency:
                const_out.write(str(sentence.constituency))
                const_out.write("\n")

#if __name__ == "__main__":
#    input_file = "sentences.txt"  # Plain text: one sentence per line
#    dep_out = "parsed.conllu"
#    const_out = "constituency_trees.txt"

#    print("🔍 Running Stanza pipeline...")
#    process_file(input_file, dep_out, const_out)
#    print("✅ Dependency parses written to:", dep_out)
#    print("✅ Constituency parses written to:", const_out

def main():
    parser = argparse.ArgumentParser(description="Run Stanza for dependency and constituency parsing.")
    parser.add_argument("input", help="Path to input plain text file (one sentence per line).")
    parser.add_argument("--dep", default="output.conllu", help="Path to output CoNLL-U dependency file.")
    parser.add_argument("--const", default="constituency_trees.txt", help="Path to output constituency tree file.")

    args = parser.parse_args()

    print("🔍 Running Stanza pipeline on:", args.input)
    process_file(args.input, args.dep, args.const)
    print("✅ Dependency parses saved to:", args.dep)
    print("✅ Constituency parses saved to:", args.const)

if __name__ == "__main__":
    main()


