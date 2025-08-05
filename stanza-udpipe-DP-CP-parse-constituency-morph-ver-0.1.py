import stanza
from stanza.models.constituency import download as download_constituency, ConstituencyPipeline
import tempfile
import subprocess
import os

# Load Stanza dependency and constituency pipelines
stanza.download('en')
download_constituency('en')
dp_pipeline = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
cp_pipeline = ConstituencyPipeline(lang='en')

def stanza_parse(sentence):
    doc = dp_pipeline(sentence)
    sent = doc.sentences[0]
    return [{
        "id": str(tok.id),
        "form": tok.text,
        "lemma": tok.lemma or "_",
        "upos": tok.upos,
        "xpos": tok.xpos or "_",
        "feats": "_",  # placeholder
        "head": str(tok.head),
        "deprel": tok.deprel,
        "deps": "_",
        "misc": "_"
    } for tok in sent.words]

def stanza_constituency(sentence):
    tree = cp_pipeline.parse(sentence)
    return tree

def run_udpipe2(model_dir, sentence):
    # Temp files for input/output
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as f_in, \
         tempfile.NamedTemporaryFile(mode='r', suffix='.conllu', delete=False) as f_out:
        f_in.write(sentence)
        f_in.flush()

        cmd = [
            'python', '/path/to/udpipe2/udpipe2.py',
            model_dir, '--predict',
            '--input', f_in.name,
            '--output', f_out.name
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"UDPipe2 failed:\n{result.stderr}")

        # Read conllu output lines
        f_out.seek(0)
        lines = [line.strip() for line in f_out if line.strip() and not line.startswith("#")]

    return lines

def merge_morphology(stanza_rows, udpipe_lines):
    for i, line in enumerate(udpipe_lines):
        cols = line.split('\t')
        if len(cols) >= 6:
            stanza_rows[i]["feats"] = cols[5]
    return stanza_rows

def format_conllu(rows):
    return "\n".join([
        "\t".join([
            row["id"], row["form"], row["lemma"], row["upos"], row["xpos"],
            row["feats"], row["head"], row["deprel"], row["deps"], row["misc"]
        ]) for row in rows
    ]) + "\n"

def full_parse(sentence, udpipe_model_dir):
    print("→ Constituency Tree:")
    print(stanza_constituency(sentence).pretty_print())

    stanza_rows = stanza_parse(sentence)
    udpipe_lines = run_udpipe2(udpipe_model_dir, sentence)
    merged_rows = merge_morphology(stanza_rows, udpipe_lines)
    return format_conllu(merged_rows)

# Example usage
# Make sure to replace with actual UDPipe2 model path
# conllu_output = full_parse("The quick brown fox jumps over the lazy dog.", "/path/to/udpipe2/models/en-ewt")
# print(conllu_output)

