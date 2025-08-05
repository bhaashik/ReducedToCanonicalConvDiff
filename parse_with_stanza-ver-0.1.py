from nltk import Tree as NLTKTree  # Make sure it's the NLTK Tree
#from nltk import Tree  # Add this import at the top
import stanza
import argparse
import conllu
from pathlib import Path

def load_stanza_pipeline():
    # Download if not already present
    stanza.download('en', package='combined')
    return stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse,constituency', use_gpu=False, tokenize_no_ssplit=True)
#return stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse,constituency', use_gpu=False)

#def process_file(input_path, dep_output_path, const_output_path):
#    pipeline = load_stanza_pipeline()
#    text = Path(input_path).read_text(encoding='utf-8')
#    doc = pipeline(text)
#
#    with open(dep_output_path, 'w', encoding='utf-8') as dep_out, \
#         open(const_output_path, 'w', encoding='utf-8') as const_out:
#
#        for sentence in doc.sentences:
#            # Write dependency parse in CoNLL-U format
#            dep_out.write(sentence.to_conll())
#            dep_out.write("\n")  # Separate sentences
#
#            # Write constituency parse as bracketed string
#            if sentence.constituency:
#                const_out.write(str(sentence.constituency))
#                const_out.write("\n")

#def process_file(input_file, dep_output, const_output):
#    pipeline = load_stanza_pipeline()
#
#    with open(input_file, 'r', encoding='utf-8') as f:
#        sentences = [line.strip() for line in f if line.strip()]
#
#    with open(dep_output, 'w', encoding='utf-8') as dep_out, open(const_output, 'w', encoding='utf-8') as const_out:
#        for i, sentence in enumerate(sentences):
#            doc = pipeline(sentence)
#            # Write the full CoNLL-U format for the sentence
#            dep_out.write(f"# sent_id = {i+1}\n")
#            dep_out.write(f"# text = {sentence}\n")
#            dep_out.write(doc.to_conll())
#            dep_out.write("\n")
#
#            # Constituency parse for each sentence in doc
#            for const_sent in doc.sentences:
#                if const_sent.constituency:
#                    const_out.write(f"(sentence {i+1}) {sentence}\n")
#                    const_out.write(f"{const_sent.constituency.to_string()}\n\n")

from conllu import TokenList

def write_conllu(sent, output_file, sent_id):
    tokens = []
    for word in sent.words:
        token = {
            "id": word.id,
            "form": word.text,
            "lemma": word.lemma or "_",
            "upos": word.upos or "_",
            "xpos": word.xpos or "_",
            "feats": word.feats if word.feats else "_",
            "head": word.head,
            "deprel": word.deprel or "_",
            "deps": "_",
            "misc": "_"
        }
        tokens.append(token)

    token_list = TokenList(tokens, metadata={"sent_id": str(sent_id), "text": sent.text})
    output_file.write(token_list.serialize())
    output_file.write("\n")  # Blank line between sentences


def process_file(input_file, dep_output, const_output):
    pipeline = load_stanza_pipeline()

    with open(input_file, 'r', encoding='utf-8') as f:
        sentences = [line.strip() for line in f if line.strip()]

    with open(dep_output, 'w', encoding='utf-8') as dep_out, open(const_output, 'w', encoding='utf-8') as const_out:
        for i, sentence in enumerate(sentences):
            doc = pipeline(sentence)
    
            for j, sent in enumerate(doc.sentences):
                write_conllu(sent, dep_out, sent_id=f"{i+1}.{j+1}")
    
                # Constituency parsing output
                if sent.constituency:
                    const_out.write(f"(sentence {i+1}.{j+1}) {sent.text}\n")
#                    const_out.write(f"{sent.constituency.to_string()}\n\n")
#                    const_out.write(f"{sent.constituency.pformat(margin=100)}\n\n")
#                    tree = Tree.convert(sent.constituency)
#                    const_out.write(tree.pformat(margin=100) + "\n\n")
                    tree = NLTKTree.fromstring(str(sent.constituency))
                    const_out.write(tree.pformat(margin=100) + "\n\n")


#    with open(dep_output, 'w', encoding='utf-8') as dep_out, open(const_output, 'w', encoding='utf-8') as const_out:
#        for i, sentence in enumerate(sentences):
#            doc = pipeline(sentence)
#
#            for j, sent in enumerate(doc.sentences):
#                dep_out.write(f"# sent_id = {i+1}.{j+1}\n")
#                dep_out.write(f"# text = {sent.text}\n")
#                dep_out.write(sent.to_conll().strip() + "\n\n")
#
#                if sent.constituency:
#                    const_out.write(f"(sentence {i+1}.{j+1}) {sent.text}\n")
#                    const_out.write(f"{sent.constituency.to_string()}\n\n")


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

