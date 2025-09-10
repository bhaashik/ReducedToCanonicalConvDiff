# Version 1

# from pathlib import Path
#
# # Base data directory (adjust if needed)
# BASE_DIR = Path(__file__).resolve().parent / "data"
#
# # Feature schema path
# SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-3.0.json"
#
# # Newspaper names
# NEWSPAPERS = ["Hindustan-Times", "The-Hindu", "Times-of-India"]
#
# # Registers
# REGISTERS = {
#     "canonical": "canonical",
#     "headlines": "headlines"
# }
#
# # File mapping
# TEXT_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "Hindustan-Times-canonical.txt",
#         "headlines": BASE_DIR / "Hindustan-Times-headlines.txt"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "The-Hindu-corrected-canonical.txt",
#         "headlines": BASE_DIR / "The-Hindu-corrected-headlines.txt"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "Times-of-India-corrected-canonical.txt",
#         "headlines": BASE_DIR / "Times-of-India-corrected-headlines.txt"
#     }
# }
#
# CONLLU_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-deps.conllu"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-deps.conllu"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-deps.conllu"
#     }
# }
#
# CONST_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-constituency.txt"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-constituency.txt"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-constituency.txt"
#     }
# }

# Version 2

from pathlib import Path

# Base data directory (adjust if needed)
BASE_DIR = Path(__file__).resolve().parent / "data"

# Feature schema path
SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-3.0.json"

# Newspaper names
NEWSPAPERS = ["Hindustan-Times", "The-Hindu", "Times-of-India"]

# Registers
REGISTERS = {
    "canonical": "canonical",
    "headlines": "headlines"
}

# File mapping for plain texts
TEXT_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "Hindustan-Times-canonical.txt",
        "headlines": BASE_DIR / "Hindustan-Times-headlines.txt"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "The-Hindu-corrected-canonical.txt",
        "headlines": BASE_DIR / "The-Hindu-corrected-headlines.txt"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "Times-of-India-corrected-canonical.txt",
        "headlines": BASE_DIR / "Times-of-India-corrected-headlines.txt"
    }
}

# File mapping for CoNLL-U dependency parses
CONLLU_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-deps.conllu"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-deps.conllu"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-deps.conllu"
    }
}

# File mapping for constituency parses (bracketed format)
CONST_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-constituency.txt"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-constituency.txt"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-constituency.txt"
    }
}

# Version 2

