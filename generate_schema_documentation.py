#!/usr/bin/env python3
"""
Generate comprehensive LaTeX documentation for diff-ontology schema v5.0
Organized by: Lexical, Morphological, Syntactic, Punctuation, Aggregate
"""

import json
from pathlib import Path
from collections import defaultdict

# Load schema
schema_path = Path('data/diff-ontology-ver-5.0.json')
with open(schema_path, 'r') as f:
    schema = json.load(f)

features = schema['diff-schema']['features']

# Reorganize features by user-requested categories
categories = {
    'Lexical': {
        'description': 'Addition, deletion, and positional changes of words',
        'subcategories': {
            'Addition': ['FW-ADD', 'C-ADD'],
            'Deletion': ['FW-DEL', 'C-DEL'],
            'Position Change': ['TOKEN-REORDER']
        }
    },
    'Morphological': {
        'description': 'Morphological features, lemma, word form, and POS changes',
        'subcategories': {
            'General': ['POS-CHG', 'LEMMA-CHG', 'FORM-CHG', 'FEAT-CHG', 'VERB-FORM-CHG']
        }
    },
    'Syntactic': {
        'description': 'Syntactic structure changes at constituency and dependency levels',
        'subcategories': {
            'Constituency': ['CONST-REM', 'CONST-ADD', 'CONST-MOV', 'CLAUSE-TYPE-CHG'],
            'Dependency': ['DEP-REL-CHG', 'HEAD-CHG']
        }
    },
    'Punctuation': {
        'description': 'Punctuation-related transformations and substitutions',
        'subcategories': {
            'General': ['PUNCT-DEL', 'PUNCT-ADD', 'PUNCT-SUBST']
        }
    },
    'Aggregate': {
        'description': 'Holistic features including length, structural complexity, and register typology',
        'subcategories': {
            'Register Typology': ['H-STRUCT', 'H-TYPE', 'F-TYPE'],
            'Structural Complexity': ['TREE-DEPTH-DIFF', 'CONST-COUNT-DIFF', 'DEP-DIST-DIFF', 'BRANCH-DIFF'],
            'Length Metrics': ['LENGTH-CHG', 'TOKEN-COUNT-DIFF', 'CHAR-COUNT-DIFF'],
            'Edit Distance': ['TED']
        }
    }
}

# Create feature lookup dictionary
feature_dict = {f['mnemonic_code']: f for f in features}

# Generate LaTeX document
latex = []

# Document header
latex.append(r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}

% Custom column types
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}

% Title information
\title{\textbf{Feature Schema for Canonical-Reduced Register Comparison}\\
\large{Diff-Ontology Version 5.0}}
\author{Schema Documentation}
\date{January 2, 2026}

\begin{document}

\maketitle

\begin{abstract}
This document provides comprehensive documentation for the diff-ontology schema version 5.0, which defines 30 linguistic features for analyzing morphosyntactic differences between canonical (full sentence) and reduced (headline) text registers in Indian English newspapers. Features are organized into five broad categories: Lexical, Morphological, Syntactic, Punctuation, and Aggregate. The schema supports dual parsing (constituency and dependency) and captures transformations at multiple linguistic levels.
\end{abstract}

\tableofcontents
\clearpage

\section{Schema Overview}

\subsection{Version Information}
''')

latex.append(f'''
\\begin{{itemize}}
\\item \\textbf{{Version}}: {schema['version']}
\\item \\textbf{{Total Features}}: {len(features)}
\\item \\textbf{{Repository}}: \\url{{{schema['repository']['url']}}}
\\end{{itemize}}
''')

latex.append(r'''
\subsection{Version History}
''')

for version, description in schema['changelog'].items():
    latex.append(f'\\subsubsection*{{Version {version}}}\n{description}\n')

# Category summary
latex.append(r'''
\subsection{Feature Categories}

The 30 features are organized into 5 broad categories:

\begin{table}[h]
\centering
\begin{tabular}{@{}llr@{}}
\toprule
\textbf{Category} & \textbf{Description} & \textbf{Count} \\
\midrule
''')

for cat_name, cat_info in categories.items():
    count = sum(len(codes) for codes in cat_info['subcategories'].values())
    latex.append(f"{cat_name} & {cat_info['description'][:40]}... & {count} \\\\\n")

latex.append(r'''\bottomrule
\end{tabular}
\caption{Feature categories in schema v5.0}
\end{table}

\subsection{Parse Type Requirements}

Features require either dependency parsing, constituency parsing, or both:

\begin{itemize}
\item \textbf{Dependency only}: FEAT-CHG, DEP-REL-CHG, HEAD-CHG, DEP-DIST-DIFF
\item \textbf{Constituency only}: CONST-COUNT-DIFF, TED
\item \textbf{Both}: All other features (24 features)
\end{itemize}

\clearpage

\section{Feature Categories}
''')

# Generate detailed descriptions for each category
for cat_name, cat_info in categories.items():
    latex.append(f'''
\\subsection{{{cat_name} Features}}

{cat_info['description']}

''')

    for subcat_name, feat_codes in cat_info['subcategories'].items():
        if len(cat_info['subcategories']) > 1:
            latex.append(f'\\subsubsection{{{subcat_name}}}\n\n')

        for feat_code in feat_codes:
            if feat_code not in feature_dict:
                continue

            feat = feature_dict[feat_code]

            latex.append(f'''
\\paragraph{{{feat['mnemonic_code']}: {feat['name']}}}
\\label{{feat:{feat['mnemonic_code']}}}

\\textbf{{Description}}: {feat['description']}

\\textbf{{Parse Types}}: {', '.join(feat['parse_types'])}

\\textbf{{Category}}: {feat.get('category', 'N/A')}

''')

            # Values table
            if feat['values'][0] == 'numeric':
                latex.append('\\textbf{Values}: Numeric (quantitative measure)\n\n')
            else:
                num_values = len(feat['values'])
                latex.append(f'\\textbf{{Values}} ({num_values} total):\n\n')

                latex.append('\\begin{small}\n')
                latex.append('\\begin{longtable}{@{}llL{7cm}@{}}\n')
                latex.append('\\toprule\n')
                latex.append('\\textbf{\\#} & \\textbf{Mnemonic} & \\textbf{Value} \\\\\n')
                latex.append('\\midrule\n')
                latex.append('\\endfirsthead\n')
                latex.append('\\multicolumn{3}{c}{{\\tablename\\ \\thetable\\ -- continued from previous page}} \\\\\n')
                latex.append('\\toprule\n')
                latex.append('\\textbf{\\#} & \\textbf{Mnemonic} & \\textbf{Value} \\\\\n')
                latex.append('\\midrule\n')
                latex.append('\\endhead\n')
                latex.append('\\midrule\n')
                latex.append('\\multicolumn{3}{r}{{Continued on next page}} \\\\\n')
                latex.append('\\endfoot\n')
                latex.append('\\bottomrule\n')
                latex.append('\\endlastfoot\n')

                for i, val in enumerate(feat['values'], 1):
                    mnem = feat['value_mnemonics'].get(val, 'N/A')
                    # Escape LaTeX special characters
                    val_escaped = val.replace('&', '\\&').replace('_', '\\_')
                    mnem_escaped = mnem.replace('&', '\\&').replace('_', '\\_')
                    latex.append(f'{i} & \\texttt{{{mnem_escaped}}} & {val_escaped} \\\\\n')

                latex.append('\\end{longtable}\n')
                latex.append('\\end{small}\n\n')

            # Extra fields
            if 'extra' in feat:
                latex.append(f"\\textbf{{Extra Fields}}: {', '.join(feat['extra'])}\n\n")

            # Definitions if available
            if 'definitions' in feat:
                latex.append('\\textbf{Definitions}:\n\\begin{itemize}\n')
                for key, defn in feat['definitions'].items():
                    latex.append(f'\\item \\texttt{{{key}}}: {defn}\n')
                latex.append('\\end{itemize}\n\n')

            # Feature definitions for FEAT-CHG
            if 'feature_definitions' in feat:
                latex.append('\\textbf{Morphological Feature Definitions}:\n\\begin{small}\n')
                latex.append('\\begin{longtable}{@{}lL{10cm}@{}}\n')
                latex.append('\\toprule\n')
                latex.append('\\textbf{Feature} & \\textbf{Definition} \\\\\n')
                latex.append('\\midrule\n')
                for fname, fdef in feat['feature_definitions'].items():
                    latex.append(f'\\texttt{{{fname}}} & {fdef} \\\\\n')
                latex.append('\\bottomrule\n')
                latex.append('\\end{longtable}\n')
                latex.append('\\end{small}\n\n')

# Summary tables section
latex.append(r'''
\clearpage
\section{Summary Tables}

\subsection{All Features by Category}

\begin{small}
\begin{longtable}{@{}rllllr@{}}
\caption{Complete feature list with categories and value counts} \\
\toprule
\textbf{\#} & \textbf{Code} & \textbf{Name} & \textbf{Category} & \textbf{Parse} & \textbf{Values} \\
\midrule
\endfirsthead
\multicolumn{6}{c}{{\tablename\ \thetable\ -- continued from previous page}} \\
\toprule
\textbf{\#} & \textbf{Code} & \textbf{Name} & \textbf{Category} & \textbf{Parse} & \textbf{Values} \\
\midrule
\endhead
\midrule
\multicolumn{6}{r}{{Continued on next page}} \\
\endfoot
\bottomrule
\endlastfoot
''')

for i, feat in enumerate(features, 1):
    code = feat['mnemonic_code'].replace('_', '\\_')
    name = feat['name'][:30] + ('...' if len(feat['name']) > 30 else '')
    cat = feat['category']
    parse = feat['parse_types'][0] if len(feat['parse_types']) == 1 else 'both'
    val_count = 1 if feat['values'][0] == 'numeric' else len(feat['values'])

    latex.append(f'{i} & \\texttt{{{code}}} & {name} & {cat} & {parse} & {val_count} \\\\\n')

latex.append(r'''\end{longtable}
\end{small}

\subsection{Features by Broad Category}
''')

# Features by broad category table
latex.append(r'''
\begin{table}[h]
\centering
\begin{tabular}{@{}lL{8cm}r@{}}
\toprule
\textbf{Category} & \textbf{Features} & \textbf{Count} \\
\midrule
''')

for cat_name, cat_info in categories.items():
    all_codes = []
    for codes in cat_info['subcategories'].values():
        all_codes.extend(codes)
    codes_str = ', '.join([f'\\texttt{{{c}}}' for c in all_codes])
    latex.append(f'{cat_name} & {codes_str} & {len(all_codes)} \\\\\n')

latex.append(r'''\bottomrule
\end{tabular}
\caption{Features organized by broad categories}
\end{table}

\clearpage

\subsection{Value Count Statistics}

\begin{table}[h]
\centering
\begin{tabular}{@{}lr@{}}
\toprule
\textbf{Statistic} & \textbf{Value} \\
\midrule
''')

# Calculate statistics
total_values = sum(1 if f['values'][0] == 'numeric' else len(f['values']) for f in features)
numeric_features = len([f for f in features if f['values'][0] == 'numeric'])
categorical_features = len(features) - numeric_features
max_values = max((len(f['values']) for f in features if f['values'][0] != 'numeric'), default=0)
max_values_feat = next((f['mnemonic_code'] for f in features if f['values'][0] != 'numeric' and len(f['values']) == max_values), 'N/A')

latex.append(f'''Total features & {len(features)} \\\\
Total categorical values & {total_values} \\\\
Numeric features & {numeric_features} \\\\
Categorical features & {categorical_features} \\\\
Maximum values per feature & {max_values} (\\texttt{{{max_values_feat}}}) \\\\
''')

latex.append(r'''\bottomrule
\end{tabular}
\caption{Schema statistics}
\end{table}

\section{Usage Guidelines}

\subsection{Feature Extraction Pipeline}

The schema is designed to be used with a modular extraction pipeline:

\begin{enumerate}
\item \textbf{Load Schema}: Parse the JSON schema file
\item \textbf{Load Data}: Read parallel canonical-headline pairs with parses
\item \textbf{Align}: Word-level alignment between pairs
\item \textbf{Extract}: Detect features from aligned pairs
\item \textbf{Aggregate}: Collect events across dimensions
\item \textbf{Analyze}: Statistical and visual analysis
\end{enumerate}

\subsection{Parse Type Selection}

\begin{itemize}
\item Use \textbf{dependency parsing} for: function word operations, morphological changes, dependency relation changes, dependency-based metrics
\item Use \textbf{constituency parsing} for: constituent operations, tree edit distance, constituent count metrics
\item Use \textbf{both} for: comprehensive analysis and cross-validation
\end{itemize}

\subsection{Critical Features}

The following features are most critical for headline analysis:

\begin{enumerate}
\item \texttt{PUNCT-SUBST}: Captures how headlines use punctuation to replace function words (e.g., colon $\rightarrow$ "and")
\item \texttt{FW-DEL}: Function word deletion is the most frequent transformation
\item \texttt{CONST-MOV}: Constituent movement captures word order changes
\item \texttt{H-TYPE}: Fragment vs. non-fragment classification enables stratified analysis
\item \texttt{FEAT-CHG}: Morphological feature changes capture verb tense, number, aspect, etc.
\end{enumerate}

\section{Implementation Notes}

\subsection{Backward Compatibility}

Schema v5.0 is fully backward compatible with v4.0. All 18 features from v4.0 are unchanged; v5.0 adds 12 new features.

\subsection{Data Requirements}

\begin{itemize}
\item \textbf{Plain text}: UTF-8 encoded, one sentence per line
\item \textbf{Dependency parses}: CoNLL-U format (Stanza parser)
\item \textbf{Constituency parses}: Bracketed tree format (NLTK/Stanza)
\item \textbf{Alignment}: Parallel files with matching line counts
\end{itemize}

\subsection{Validation}

After extracting features:
\begin{itemize}
\item Verify all 30 features appear in output
\item Check punctuation events are detected
\item Validate headline typology classification
\item Compare feature frequencies across newspapers
\end{itemize}

\section{References}

\begin{itemize}
\item Schema file: \texttt{data/diff-ontology-ver-5.0.json}
\item Changelog: \texttt{SCHEMA\_CHANGELOG\_v5.0.md}
\item Implementation: \texttt{SCHEMA\_V5\_IMPLEMENTATION\_SUMMARY.md}
\item Quick start: \texttt{SCHEMA\_V5\_QUICK\_START.md}
\end{itemize}

\end{document}
''')

# Write LaTeX file
output_path = Path('LaTeX/Schema-Documentation/diff-ontology-v5.0-documentation.tex')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(latex))

print(f"✅ LaTeX documentation created: {output_path}")
print(f"\n📄 Document structure:")
print(f"   - Section 1: Schema Overview (version, history, categories)")
print(f"   - Section 2: Feature Categories (detailed descriptions)")
print(f"     * 2.1 Lexical (6 features)")
print(f"     * 2.2 Morphological (5 features)")
print(f"     * 2.3 Syntactic (6 features)")
print(f"     * 2.4 Punctuation (3 features)")
print(f"     * 2.5 Aggregate (10 features)")
print(f"   - Section 3: Summary Tables")
print(f"   - Section 4: Usage Guidelines")
print(f"   - Section 5: Implementation Notes")
print(f"\n📊 Features documented:")
for cat_name, cat_info in categories.items():
    count = sum(len(codes) for codes in cat_info['subcategories'].values())
    print(f"   {cat_name}: {count} features")
print(f"\n✅ Total: {len(features)} features fully documented")
print(f"\nCompile with: pdflatex diff-ontology-v5.0-documentation.tex")
