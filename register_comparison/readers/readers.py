# Version 2

# from pathlib import Path
# from typing import List
# from conllu import parse_incr
# from nltk.tree import Tree
#
# def read_plain_text(path: Path) -> List[str]:
#     """Reads a plain text file and returns a list of sentences (stripped)."""
#     with open(path, 'r', encoding='utf-8') as f:
#         return [line.strip() for line in f if line.strip()]
#
# def read_conllu(path: Path):
#     """Reads a CoNLL-U file and yields TokenList objects."""
#     with open(path, 'r', encoding='utf-8') as f:
#         for tokenlist in parse_incr(f):
#             yield tokenlist
#
# def read_constituency(path: Path) -> List[Tree]:
#     """Reads bracketed constituency parse strings into NLTK Tree objects."""
#     trees = []
#     with open(path, 'r', encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
#             trees.append(Tree.fromstring(line))
#     return trees

# Version 2

from pathlib import Path
from typing import List
from conllu import parse_incr
from nltk.tree import Tree

def read_plain_text(path: Path) -> List[str]:
    """Reads a plain text file and returns a list of sentences (stripped)."""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def read_conllu(path: Path):
    """Reads a CoNLL-U file and yields TokenList objects for each sentence."""
    with open(path, 'r', encoding='utf-8') as f:
        for tokenlist in parse_incr(f):
            yield tokenlist

def read_constituency(path: Path) -> List[Tree]:
    """Reads bracketed constituency parse strings into NLTK Tree objects."""
    trees = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            trees.append(Tree.fromstring(line))
    return trees

# Version 2