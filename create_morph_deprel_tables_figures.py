#!/usr/bin/env python3
"""
Create FEAT-CHG and DEP-REL-CHG tables and figures for all three research tasks.

Generates:
  Task 1 (Comparative Study):  6 tables + 6 figures
  Task 2 (Transformation Study): 3 tables + 3 figures
  Task 3 (Complexity & Similarity): 4 tables + 4 figures

Outputs CSV + PNG to output/{task}/morph-deprel-analysis/,
converts CSVs to LaTeX .tex, and copies to appropriate LaTeX directories.

Usage:
  python create_morph_deprel_tables_figures.py
  python create_morph_deprel_tables_figures.py --task task1
  python create_morph_deprel_tables_figures.py --task task2
  python create_morph_deprel_tables_figures.py --task task3
"""

import argparse
import shutil
import sys
import os
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR
from paths_config import NEWSPAPERS

OUTPUT_DIR = BASE_DIR / 'output'

# LaTeX targets
LATEX_TASK1_DIR = BASE_DIR / 'LaTeX' / 'Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR'
LATEX_TASK2_BASE = BASE_DIR / 'LaTeX' / 'Canonical_Reduced_Register_Complexity_Part_2_ACL_ARR_short_not_submitted' / 'latex'
LATEX_TASK3_BASE = BASE_DIR / 'LaTeX' / 'Canonical_Reduced_Register_Complexity_Part_3_ACL_ARR_short_submiited'

# Matplotlib defaults
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'font.size': 10,
})
NEWSPAPER_COLORS = {
    'Times-of-India': '#1f77b4',
    'Hindustan-Times': '#ff7f0e',
    'The-Hindu': '#2ca02c',
}
NEWSPAPER_SHORT = {
    'Times-of-India': 'TOI',
    'Hindustan-Times': 'HT',
    'The-Hindu': 'TH',
}


# ============================================================================
# Utility: CSV -> LaTeX longtable
# ============================================================================

def csv_to_latex_longtable(csv_path: Path, caption: str, label: str,
                           max_rows: Optional[int] = None) -> str:
    """Convert a CSV to a LaTeX longtable wrapped in a table environment."""
    df = pd.read_csv(csv_path)
    df = df.dropna(axis=1, how='all')

    # Drop numeric columns that are all zeros
    for col in df.select_dtypes(include=['number']).columns:
        if (df[col].fillna(0).abs() == 0).all():
            df = df.drop(columns=[col])

    if max_rows is not None and len(df) > max_rows:
        df = df.head(max_rows)

    if df.empty:
        return ''

    latex_body = df.to_latex(index=False, escape=True, na_rep='--', longtable=True)
    return '\n'.join([
        '\\begin{table}[htbp]',
        '\\centering',
        latex_body,
        f'\\caption{{{caption}}}',
        f'\\label{{{label}}}',
        '\\end{table}',
    ])


def save_tex(csv_path: Path, task: str, tex_dir: Path) -> Path:
    """Generate .tex from CSV and write to *tex_dir*. Returns the .tex path."""
    tex_dir.mkdir(parents=True, exist_ok=True)
    stem = csv_path.stem
    caption = stem.replace('_', ' ').replace('-', ' ').title()
    label = f'tab:{task}-{stem.replace("_", "-")}'
    content = csv_to_latex_longtable(csv_path, caption, label)
    if not content.strip():
        return None
    tex_path = tex_dir / f'{stem}.tex'
    tex_path.write_text(content, encoding='utf-8')
    return tex_path


# ============================================================================
# Main Analyzer
# ============================================================================

class MorphDepRelAnalyzer:
    """Generate FEAT-CHG and DEP-REL-CHG tables & figures for all tasks."""

    def __init__(self):
        self.newspapers = NEWSPAPERS  # ['Hindustan-Times', 'The-Hindu', 'Times-of-India']
        self.project_root = BASE_DIR

        # Per-task output dirs (task-oriented structure post-reorganization)
        self.task1_dir = OUTPUT_DIR / 'task-1-comparative-study' / 'morph-deprel-analysis'
        self.task2_dir = OUTPUT_DIR / 'task-2-transformation-study' / 'morph-deprel-analysis'
        self.task3_dir = OUTPUT_DIR / 'task-3-complexity-similarity-study' / 'morph-deprel-analysis'

        # Raw event data
        self.feat_events: List[Dict] = []
        self.deprel_events: List[Dict] = []

        # CoNLL-U distributions for Task 3
        self.morph_distributions: Dict[str, Dict[str, Counter]] = {}  # {newspaper: {register: Counter}}
        self.deprel_distributions: Dict[str, Dict[str, Counter]] = {}

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_all_events(self):
        """Read events_global.csv from each newspaper, filter FEAT-CHG + DEP-REL-CHG."""
        print(f"\n{'='*80}")
        print('LOADING EVENTS')
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            csv_path = OUTPUT_DIR / 'task-1-comparative-study' / 'per-newspaper' / newspaper / 'events_global.csv'
            if not csv_path.exists():
                print(f'  WARNING: missing {csv_path}')
                continue
            df = pd.read_csv(csv_path, low_memory=False)
            for _, row in df.iterrows():
                rec = row.to_dict()
                fid = str(rec.get('feature_id', ''))
                if fid == 'FEAT-CHG':
                    self.feat_events.append(rec)
                elif fid == 'DEP-REL-CHG':
                    self.deprel_events.append(rec)

        print(f'  FEAT-CHG events:    {len(self.feat_events):,}')
        print(f'  DEP-REL-CHG events: {len(self.deprel_events):,}')

    def load_conllu_distributions(self):
        """Parse CoNLL-U files to get morphological feature and deprel distributions."""
        print(f"\n{'='*80}")
        print('LOADING CoNLL-U DISTRIBUTIONS (for Task 3 entropy)')
        print(f"{'='*80}\n")

        try:
            import conllu
        except ImportError:
            print('  WARNING: conllu package not installed. Task 3 entropy tables will be skipped.')
            return

        dep_dir = self.project_root / 'data' / 'input' / 'dependecy-parsed'

        for newspaper in self.newspapers:
            self.morph_distributions[newspaper] = {}
            self.deprel_distributions[newspaper] = {}

            for register, suffix in [('canonical', 'canonical'), ('headline', 'headlines')]:
                conllu_path = dep_dir / f'{newspaper}-{suffix}-stanza-parsed-deps.conllu'
                if not conllu_path.exists():
                    print(f'  WARNING: missing {conllu_path}')
                    continue

                morph_counter = Counter()
                deprel_counter = Counter()

                with open(conllu_path, 'r', encoding='utf-8') as f:
                    for tokenlist in conllu.parse_incr(f):
                        for token in tokenlist:
                            # Skip multi-word tokens
                            if isinstance(token['id'], tuple):
                                continue

                            # Morphological features
                            feats = token.get('feats')
                            if feats and isinstance(feats, dict):
                                for feat_name, feat_val in feats.items():
                                    morph_counter[f'{feat_name}={feat_val}'] += 1

                            # Dependency relations
                            deprel = token.get('deprel')
                            if deprel:
                                deprel_counter[deprel] += 1

                self.morph_distributions[newspaper][register] = morph_counter
                self.deprel_distributions[newspaper][register] = deprel_counter
                print(f'  {newspaper} {register}: {sum(morph_counter.values()):,} morph features, '
                      f'{sum(deprel_counter.values()):,} deprels')

    # ------------------------------------------------------------------
    # Helper: extract feature type from FEAT-CHG canonical/headline value
    # ------------------------------------------------------------------

    @staticmethod
    def _feat_type(value: str) -> str:
        """Extract feature type from value like 'Tense=Past' -> 'Tense'."""
        if '=' in str(value):
            return str(value).split('=')[0]
        return str(value)

    # ------------------------------------------------------------------
    # Task 1: Comparative Study (6 tables + 6 figures)
    # ------------------------------------------------------------------

    def generate_task1_tables(self):
        """Generate 6 CSV tables for Task 1."""
        out = self.task1_dir / 'tables'
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*80}")
        print('TASK 1: Generating tables')
        print(f"{'='*80}\n")

        # --- 1. morph_feature_type_distribution ---
        rows = []
        for newspaper in self.newspapers:
            type_counts = Counter()
            for ev in self.feat_events:
                if ev.get('newspaper') == newspaper:
                    ft = self._feat_type(ev.get('canonical_value', ''))
                    type_counts[ft] += 1
            for ft, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
                rows.append({'Feature_Type': ft, 'Newspaper': newspaper, 'Count': cnt})
        df = pd.DataFrame(rows)
        if not df.empty:
            pivot = df.pivot_table(index='Feature_Type', columns='Newspaper',
                                   values='Count', fill_value=0, aggfunc='sum')
            pivot['Total'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('Total', ascending=False)
            pivot.to_csv(out / 'morph_feature_type_distribution.csv')
            print(f'  morph_feature_type_distribution.csv ({len(pivot)} rows)')

        # --- 2. morph_feature_top_transformations ---
        trans_counts = Counter()
        for ev in self.feat_events:
            cv = ev.get('canonical_value', '')
            hv = ev.get('headline_value', '')
            trans_counts[f'{cv} -> {hv}'] += 1
        rows = [{'Transformation': k, 'Count': v, 'Percentage': 0.0}
                for k, v in trans_counts.most_common(20)]
        total = sum(trans_counts.values()) or 1
        for r in rows:
            r['Percentage'] = round(r['Count'] / total * 100, 2)
        pd.DataFrame(rows).to_csv(out / 'morph_feature_top_transformations.csv', index=False)
        print(f'  morph_feature_top_transformations.csv ({len(rows)} rows)')

        # --- 3. morph_feature_cross_newspaper ---
        rows = []
        for newspaper in self.newspapers:
            type_counts = Counter()
            np_total = 0
            for ev in self.feat_events:
                if ev.get('newspaper') == newspaper:
                    ft = self._feat_type(ev.get('canonical_value', ''))
                    type_counts[ft] += 1
                    np_total += 1
            for ft, cnt in type_counts.items():
                rows.append({
                    'Feature_Type': ft,
                    'Newspaper': newspaper,
                    'Count': cnt,
                    'Proportion': round(cnt / max(np_total, 1) * 100, 2)
                })
        pd.DataFrame(rows).to_csv(out / 'morph_feature_cross_newspaper.csv', index=False)
        print(f'  morph_feature_cross_newspaper.csv ({len(rows)} rows)')

        # --- 4. deprel_top_transformations ---
        # Per-newspaper counts for top 30 globally
        global_counts = Counter()
        np_counts = {n: Counter() for n in self.newspapers}
        for ev in self.deprel_events:
            cv = ev.get('canonical_value', '')
            hv = ev.get('headline_value', '')
            key = f'{cv} -> {hv}'
            global_counts[key] += 1
            np_counts[ev.get('newspaper', '')][key] += 1

        top30 = [k for k, _ in global_counts.most_common(30)]
        rows = []
        total_dep = sum(global_counts.values()) or 1
        for t in top30:
            row = {'Transformation': t, 'Total': global_counts[t],
                   'Percentage': round(global_counts[t] / total_dep * 100, 2)}
            for n in self.newspapers:
                row[NEWSPAPER_SHORT[n]] = np_counts[n][t]
            rows.append(row)
        pd.DataFrame(rows).to_csv(out / 'deprel_top_transformations.csv', index=False)
        print(f'  deprel_top_transformations.csv ({len(rows)} rows)')

        # --- 5. deprel_source_grouped ---
        source_data = defaultdict(lambda: {'count': 0, 'targets': Counter()})
        for ev in self.deprel_events:
            src = str(ev.get('canonical_value', ''))
            tgt = str(ev.get('headline_value', ''))
            source_data[src]['count'] += 1
            source_data[src]['targets'][tgt] += 1

        rows = []
        for src in sorted(source_data, key=lambda s: -source_data[s]['count']):
            d = source_data[src]
            top_tgt = d['targets'].most_common(1)[0] if d['targets'] else ('', 0)
            rows.append({
                'Source_Relation': src,
                'Total_Count': d['count'],
                'Unique_Targets': len(d['targets']),
                'Top_Target': top_tgt[0],
                'Top_Target_Count': top_tgt[1],
            })
        pd.DataFrame(rows).to_csv(out / 'deprel_source_grouped.csv', index=False)
        print(f'  deprel_source_grouped.csv ({len(rows)} rows)')

        # --- 6. deprel_cross_newspaper ---
        top15_global = [k for k, _ in global_counts.most_common(15)]
        rows = []
        for n in self.newspapers:
            np_total = sum(np_counts[n].values()) or 1
            for t in top15_global:
                rows.append({
                    'Transformation': t,
                    'Newspaper': n,
                    'Count': np_counts[n][t],
                    'Proportion': round(np_counts[n][t] / np_total * 100, 2),
                })
        pd.DataFrame(rows).to_csv(out / 'deprel_cross_newspaper.csv', index=False)
        print(f'  deprel_cross_newspaper.csv ({len(rows)} rows)')

    def generate_task1_figures(self):
        """Generate 6 PNG figures for Task 1."""
        out = self.task1_dir / 'figures'
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*80}")
        print('TASK 1: Generating figures')
        print(f"{'='*80}\n")

        # --- 1. morph_feature_type_distribution (grouped bar) ---
        csv = self.task1_dir / 'tables' / 'morph_feature_type_distribution.csv'
        if csv.exists():
            df = pd.read_csv(csv, index_col=0)
            if 'Total' in df.columns:
                df = df.drop(columns=['Total'])
            fig, ax = plt.subplots(figsize=(12, 6))
            df.plot(kind='bar', ax=ax, color=[NEWSPAPER_COLORS.get(c, '#999') for c in df.columns])
            ax.set_title('Morphological Feature Type Distribution by Newspaper')
            ax.set_xlabel('Feature Type')
            ax.set_ylabel('Count')
            ax.legend(title='Newspaper')
            plt.xticks(rotation=45, ha='right')
            fig.savefig(out / 'morph_feature_type_distribution.png')
            plt.close(fig)
            print('  morph_feature_type_distribution.png')

        # --- 2. morph_feature_transformation_heatmap ---
        canonical_types = Counter()
        headline_types = Counter()
        pair_counts = Counter()
        for ev in self.feat_events:
            ct = self._feat_type(ev.get('canonical_value', ''))
            ht = self._feat_type(ev.get('headline_value', ''))
            cv = str(ev.get('canonical_value', ''))
            hv = str(ev.get('headline_value', ''))
            canonical_types[cv] += 1
            headline_types[hv] += 1
            pair_counts[(cv, hv)] += 1

        top_c = [k for k, _ in canonical_types.most_common(12)]
        top_h = [k for k, _ in headline_types.most_common(12)]
        matrix = pd.DataFrame(0, index=top_c, columns=top_h)
        for (c, h), cnt in pair_counts.items():
            if c in matrix.index and h in matrix.columns:
                matrix.loc[c, h] = cnt

        if not matrix.empty:
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(matrix, annot=True, fmt='d', cmap='YlOrRd', ax=ax,
                        linewidths=0.5, cbar_kws={'label': 'Count'})
            ax.set_title('FEAT-CHG: Canonical (Full) vs Reduced (Headline) Value Matrix')
            ax.set_xlabel('Reduced Register Value')
            ax.set_ylabel('Canonical Register Value')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            fig.savefig(out / 'morph_feature_transformation_heatmap.png')
            plt.close(fig)
            print('  morph_feature_transformation_heatmap.png')

        # --- 3. morph_feature_cross_newspaper (stacked bar) ---
        csv = self.task1_dir / 'tables' / 'morph_feature_cross_newspaper.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            pivot = df.pivot_table(index='Newspaper', columns='Feature_Type',
                                   values='Proportion', fill_value=0)
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
            ax.set_title('Feature Type Proportions per Newspaper')
            ax.set_ylabel('Proportion (%)')
            ax.set_xlabel('Newspaper')
            ax.legend(title='Feature Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            plt.xticks(rotation=0)
            fig.savefig(out / 'morph_feature_cross_newspaper.png')
            plt.close(fig)
            print('  morph_feature_cross_newspaper.png')

        # --- 4. deprel_top_transformations (horizontal bar) ---
        csv = self.task1_dir / 'tables' / 'deprel_top_transformations.csv'
        if csv.exists():
            df = pd.read_csv(csv).head(25)
            fig, ax = plt.subplots(figsize=(12, 10))
            y_pos = np.arange(len(df))
            ax.barh(y_pos, df['Total'], color='steelblue')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(df['Transformation'], fontsize=8)
            ax.invert_yaxis()
            ax.set_xlabel('Count')
            ax.set_title('Top 25 DEP-REL-CHG Transformations')
            # Add percentage labels
            for i, (cnt, pct) in enumerate(zip(df['Total'], df['Percentage'])):
                ax.text(cnt + 10, i, f'{pct:.1f}%', va='center', fontsize=7)
            fig.savefig(out / 'deprel_top_transformations.png')
            plt.close(fig)
            print('  deprel_top_transformations.png')

        # --- 5. deprel_transformation_heatmap ---
        src_counter = Counter()
        tgt_counter = Counter()
        pair_dep = Counter()
        for ev in self.deprel_events:
            s = str(ev.get('canonical_value', ''))
            t = str(ev.get('headline_value', ''))
            src_counter[s] += 1
            tgt_counter[t] += 1
            pair_dep[(s, t)] += 1

        top_s = [k for k, _ in src_counter.most_common(15)]
        top_t = [k for k, _ in tgt_counter.most_common(15)]
        mat = pd.DataFrame(0, index=top_s, columns=top_t)
        for (s, t), cnt in pair_dep.items():
            if s in mat.index and t in mat.columns:
                mat.loc[s, t] = cnt

        if not mat.empty:
            fig, ax = plt.subplots(figsize=(14, 11))
            sns.heatmap(mat, annot=True, fmt='d', cmap='YlOrRd', ax=ax,
                        linewidths=0.5, cbar_kws={'label': 'Count'})
            ax.set_title('DEP-REL-CHG: Canonical vs Reduced Relation Matrix (Top 15 x 15)')
            ax.set_xlabel('Reduced Register Relation')
            ax.set_ylabel('Canonical Register Relation')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            fig.savefig(out / 'deprel_transformation_heatmap.png')
            plt.close(fig)
            print('  deprel_transformation_heatmap.png')

        # --- 6. deprel_cross_newspaper (grouped bar) ---
        csv = self.task1_dir / 'tables' / 'deprel_cross_newspaper.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            # Pick top 10 transformations
            top10 = df.groupby('Transformation')['Count'].sum().nlargest(10).index.tolist()
            df_top = df[df['Transformation'].isin(top10)]
            pivot = df_top.pivot_table(index='Transformation', columns='Newspaper',
                                       values='Count', fill_value=0)
            # Sort by total
            pivot['_total'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('_total', ascending=False).drop(columns='_total')

            fig, ax = plt.subplots(figsize=(14, 7))
            pivot.plot(kind='bar', ax=ax, color=[NEWSPAPER_COLORS.get(c, '#999') for c in pivot.columns])
            ax.set_title('Top 10 DEP-REL-CHG Transformations by Newspaper')
            ax.set_xlabel('Transformation')
            ax.set_ylabel('Count')
            ax.legend(title='Newspaper')
            plt.xticks(rotation=45, ha='right')
            fig.savefig(out / 'deprel_cross_newspaper.png')
            plt.close(fig)
            print('  deprel_cross_newspaper.png')

    # ------------------------------------------------------------------
    # Task 2: Transformation Study (3 tables + 3 figures)
    # ------------------------------------------------------------------

    def generate_task2_tables(self):
        """Generate 3 CSV tables for Task 2."""
        out = self.task2_dir / 'tables'
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*80}")
        print('TASK 2: Generating tables')
        print(f"{'='*80}\n")

        # --- 1. morph_rule_coverage_by_feature ---
        feat_type_data = defaultdict(lambda: {'count': 0, 'patterns': Counter()})
        for ev in self.feat_events:
            ft = self._feat_type(ev.get('canonical_value', ''))
            cv = str(ev.get('canonical_value', ''))
            hv = str(ev.get('headline_value', ''))
            pattern = f'{cv} -> {hv}'
            feat_type_data[ft]['count'] += 1
            feat_type_data[ft]['patterns'][pattern] += 1

        rows = []
        for ft in sorted(feat_type_data, key=lambda x: -feat_type_data[x]['count']):
            d = feat_type_data[ft]
            top_pat = d['patterns'].most_common(1)[0] if d['patterns'] else ('', 0)
            unique = len(d['patterns'])
            # Systematicity = proportion of instances covered by top pattern
            systematicity = round(top_pat[1] / max(d['count'], 1), 4)
            rows.append({
                'Feature_Type': ft,
                'Total_Instances': d['count'],
                'Unique_Patterns': unique,
                'Top_Pattern': top_pat[0],
                'Top_Pattern_Count': top_pat[1],
                'Systematicity': systematicity,
            })
        pd.DataFrame(rows).to_csv(out / 'morph_rule_coverage_by_feature.csv', index=False)
        print(f'  morph_rule_coverage_by_feature.csv ({len(rows)} rows)')

        # --- 2. deprel_rule_systematicity ---
        src_data = defaultdict(lambda: {'count': 0, 'targets': Counter()})
        for ev in self.deprel_events:
            src = str(ev.get('canonical_value', ''))
            tgt = str(ev.get('headline_value', ''))
            src_data[src]['count'] += 1
            src_data[src]['targets'][tgt] += 1

        rows = []
        for src in sorted(src_data, key=lambda s: -src_data[s]['count']):
            d = src_data[src]
            top_tgt = d['targets'].most_common(1)[0] if d['targets'] else ('', 0)
            unique = len(d['targets'])
            systematicity = round(top_tgt[1] / max(d['count'], 1), 4)
            rows.append({
                'Source_Relation': src,
                'Total_Instances': d['count'],
                'Unique_Targets': unique,
                'Top_Transformation': f'{src} -> {top_tgt[0]}',
                'Top_Count': top_tgt[1],
                'Systematicity': systematicity,
            })
        pd.DataFrame(rows).to_csv(out / 'deprel_rule_systematicity.csv', index=False)
        print(f'  deprel_rule_systematicity.csv ({len(rows)} rows)')

        # --- 3. morph_deprel_directionality ---
        # Events record canonical_value -> headline_value, i.e. what changed
        # when reducing a full sentence to its headline form.
        #   canonical=X, headline=ABSENT  -> feature/relation lost in reduction
        #   canonical=ABSENT, headline=X  -> feature/relation emerged in reduction
        #   both present, different       -> substituted during reduction
        def classify_direction(cv, hv):
            cv_s = str(cv).strip()
            hv_s = str(hv).strip()
            # FEAT-CHG values use "Feature=ABSENT" when a morphological feature
            # is missing in one register; DEP-REL-CHG values are raw relations.
            cv_absent = cv_s in ('ABSENT', '', 'nan', 'None') or cv_s.endswith('=ABSENT')
            hv_absent = hv_s in ('ABSENT', '', 'nan', 'None') or hv_s.endswith('=ABSENT')
            if not cv_absent and hv_absent:
                return 'Lost in Reduction'
            elif cv_absent and not hv_absent:
                return 'Emerged in Reduction'
            else:
                return 'Substituted in Reduction'

        feat_dir = Counter()
        deprel_dir = Counter()
        for ev in self.feat_events:
            d = classify_direction(ev.get('canonical_value', ''), ev.get('headline_value', ''))
            feat_dir[d] += 1
        for ev in self.deprel_events:
            d = classify_direction(ev.get('canonical_value', ''), ev.get('headline_value', ''))
            deprel_dir[d] += 1

        directions = ['Lost in Reduction', 'Emerged in Reduction', 'Substituted in Reduction']
        rows = []
        for d in directions:
            rows.append({
                'Direction': d,
                'FEAT_CHG_Count': feat_dir.get(d, 0),
                'FEAT_CHG_Pct': round(feat_dir.get(d, 0) / max(sum(feat_dir.values()), 1) * 100, 2),
                'DEP_REL_CHG_Count': deprel_dir.get(d, 0),
                'DEP_REL_CHG_Pct': round(deprel_dir.get(d, 0) / max(sum(deprel_dir.values()), 1) * 100, 2),
            })
        pd.DataFrame(rows).to_csv(out / 'morph_deprel_directionality.csv', index=False)
        print(f'  morph_deprel_directionality.csv ({len(rows)} rows)')

    def generate_task2_figures(self):
        """Generate 3 PNG figures for Task 2."""
        out = self.task2_dir / 'figures'
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*80}")
        print('TASK 2: Generating figures')
        print(f"{'='*80}\n")

        # --- 1. morph_rule_coverage_by_feature (horizontal bar + systematicity) ---
        csv = self.task2_dir / 'tables' / 'morph_rule_coverage_by_feature.csv'
        if csv.exists():
            df = pd.read_csv(csv).sort_values('Total_Instances', ascending=True)
            fig, ax1 = plt.subplots(figsize=(12, 7))
            y_pos = np.arange(len(df))
            bars = ax1.barh(y_pos, df['Total_Instances'], color='steelblue', label='Instance Count')
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(df['Feature_Type'])
            ax1.set_xlabel('Instance Count', color='steelblue')
            ax1.set_title('FEAT-CHG: Rule Coverage by Feature Type')

            ax2 = ax1.twiny()
            ax2.plot(df['Systematicity'].values, y_pos, 'ro-', label='Systematicity', markersize=6)
            ax2.set_xlabel('Systematicity Score', color='red')
            ax2.set_xlim(0, 1)

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right')
            fig.savefig(out / 'morph_rule_coverage_by_feature.png')
            plt.close(fig)
            print('  morph_rule_coverage_by_feature.png')

        # --- 2. deprel_transformation_patterns (scatter/bubble) ---
        csv = self.task2_dir / 'tables' / 'deprel_rule_systematicity.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            # Top 30 by count for readability
            df_top = df.head(30)
            fig, ax = plt.subplots(figsize=(12, 8))
            sizes = df_top['Unique_Targets'].values * 15
            scatter = ax.scatter(df_top['Total_Instances'], df_top['Systematicity'],
                                 s=sizes, alpha=0.6, c='steelblue', edgecolors='navy')
            # Label top 10
            for _, row in df_top.head(10).iterrows():
                ax.annotate(row['Source_Relation'],
                            (row['Total_Instances'], row['Systematicity']),
                            fontsize=7, ha='center', va='bottom')
            ax.set_xlabel('Total Instances')
            ax.set_ylabel('Systematicity Score')
            ax.set_title('DEP-REL-CHG: Source Relations - Instances vs Systematicity\n(bubble size = unique targets)')
            fig.savefig(out / 'deprel_transformation_patterns.png')
            plt.close(fig)
            print('  deprel_transformation_patterns.png')

        # --- 3. morph_deprel_directionality (grouped bar) ---
        csv = self.task2_dir / 'tables' / 'morph_deprel_directionality.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))

            # FEAT-CHG
            ax = axes[0]
            bars = ax.bar(range(len(df)), df['FEAT_CHG_Count'],
                          color=['#e74c3c', '#3498db', '#2ecc71'])
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(df['Direction'], rotation=20, ha='right', fontsize=8)
            ax.set_ylabel('Count')
            ax.set_title('FEAT-CHG Directionality')
            for bar, pct in zip(bars, df['FEAT_CHG_Pct']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{pct:.1f}%', ha='center', fontsize=9)

            # DEP-REL-CHG
            ax = axes[1]
            bars = ax.bar(range(len(df)), df['DEP_REL_CHG_Count'],
                          color=['#e74c3c', '#3498db', '#2ecc71'])
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(df['Direction'], rotation=20, ha='right', fontsize=8)
            ax.set_ylabel('Count')
            ax.set_title('DEP-REL-CHG Directionality')
            for bar, pct in zip(bars, df['DEP_REL_CHG_Pct']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                        f'{pct:.1f}%', ha='center', fontsize=9)

            fig.suptitle('Canonical-to-Reduced Changes: FEAT-CHG vs DEP-REL-CHG', fontsize=13, y=1.02)
            plt.tight_layout()
            fig.savefig(out / 'morph_deprel_directionality.png')
            plt.close(fig)
            print('  morph_deprel_directionality.png')

    # ------------------------------------------------------------------
    # Task 3: Complexity & Similarity (4 tables + 4 figures)
    # ------------------------------------------------------------------

    @staticmethod
    def _shannon_entropy(counter: Counter) -> float:
        """Compute Shannon entropy (bits) from a Counter."""
        total = sum(counter.values())
        if total == 0:
            return 0.0
        probs = np.array([c / total for c in counter.values()])
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))

    @staticmethod
    def _kl_divergence(p_counter: Counter, q_counter: Counter) -> float:
        """KL(P||Q) with Laplace smoothing."""
        all_keys = set(p_counter.keys()) | set(q_counter.keys())
        if not all_keys:
            return 0.0
        # Laplace smoothing
        alpha = 1e-10
        p_total = sum(p_counter.values()) + alpha * len(all_keys)
        q_total = sum(q_counter.values()) + alpha * len(all_keys)
        kl = 0.0
        for k in all_keys:
            p_val = (p_counter.get(k, 0) + alpha) / p_total
            q_val = (q_counter.get(k, 0) + alpha) / q_total
            if p_val > 0:
                kl += p_val * np.log2(p_val / q_val)
        return float(kl)

    @staticmethod
    def _js_divergence(p_counter: Counter, q_counter: Counter) -> float:
        """Jensen-Shannon divergence."""
        all_keys = set(p_counter.keys()) | set(q_counter.keys())
        if not all_keys:
            return 0.0
        alpha = 1e-10
        p_total = sum(p_counter.values()) + alpha * len(all_keys)
        q_total = sum(q_counter.values()) + alpha * len(all_keys)
        m_probs = {}
        p_probs = {}
        q_probs = {}
        for k in all_keys:
            p_probs[k] = (p_counter.get(k, 0) + alpha) / p_total
            q_probs[k] = (q_counter.get(k, 0) + alpha) / q_total
            m_probs[k] = (p_probs[k] + q_probs[k]) / 2

        kl_pm = sum(p_probs[k] * np.log2(p_probs[k] / m_probs[k]) for k in all_keys if p_probs[k] > 0)
        kl_qm = sum(q_probs[k] * np.log2(q_probs[k] / m_probs[k]) for k in all_keys if q_probs[k] > 0)
        return float((kl_pm + kl_qm) / 2)

    def _get_per_feature_counters(self, newspaper: str, register: str) -> Dict[str, Counter]:
        """Split morph distribution into per-feature-type counters.
        E.g., 'Tense=Past' -> feature_type 'Tense', value 'Past'."""
        result = defaultdict(Counter)
        dist = self.morph_distributions.get(newspaper, {}).get(register, Counter())
        for feat_val, cnt in dist.items():
            if '=' in feat_val:
                feat_type = feat_val.split('=')[0]
                result[feat_type][feat_val] += cnt
        return dict(result)

    def generate_task3_tables(self):
        """Generate 4 CSV tables for Task 3."""
        out = self.task3_dir / 'tables'
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*80}")
        print('TASK 3: Generating tables')
        print(f"{'='*80}\n")

        if not self.morph_distributions:
            print('  WARNING: CoNLL-U distributions not loaded. Skipping Task 3 tables.')
            return

        # --- 1. morph_feature_entropy ---
        rows = []
        for newspaper in self.newspapers:
            can_feats = self._get_per_feature_counters(newspaper, 'canonical')
            hed_feats = self._get_per_feature_counters(newspaper, 'headline')
            all_feat_types = sorted(set(can_feats.keys()) | set(hed_feats.keys()))
            for ft in all_feat_types:
                can_entropy = self._shannon_entropy(can_feats.get(ft, Counter()))
                hed_entropy = self._shannon_entropy(hed_feats.get(ft, Counter()))
                rows.append({
                    'Feature_Type': ft,
                    'Newspaper': newspaper,
                    'Canonical_Entropy': round(can_entropy, 4),
                    'Headline_Entropy': round(hed_entropy, 4),
                    'Entropy_Diff': round(can_entropy - hed_entropy, 4),
                })
        pd.DataFrame(rows).to_csv(out / 'morph_feature_entropy.csv', index=False)
        print(f'  morph_feature_entropy.csv ({len(rows)} rows)')

        # --- 2. deprel_entropy ---
        rows = []
        for newspaper in self.newspapers:
            can_dep = self.deprel_distributions.get(newspaper, {}).get('canonical', Counter())
            hed_dep = self.deprel_distributions.get(newspaper, {}).get('headline', Counter())
            can_ent = self._shannon_entropy(can_dep)
            hed_ent = self._shannon_entropy(hed_dep)
            rows.append({
                'Newspaper': newspaper,
                'Canonical_Entropy': round(can_ent, 4),
                'Headline_Entropy': round(hed_ent, 4),
                'Entropy_Diff': round(can_ent - hed_ent, 4),
                'Canonical_Unique_Deprels': len(can_dep),
                'Headline_Unique_Deprels': len(hed_dep),
            })
        pd.DataFrame(rows).to_csv(out / 'deprel_entropy.csv', index=False)
        print(f'  deprel_entropy.csv ({len(rows)} rows)')

        # --- 3. morph_feature_divergence ---
        # Aggregate across newspapers for each feature type
        agg_can = defaultdict(Counter)
        agg_hed = defaultdict(Counter)
        for newspaper in self.newspapers:
            can_feats = self._get_per_feature_counters(newspaper, 'canonical')
            hed_feats = self._get_per_feature_counters(newspaper, 'headline')
            for ft in set(can_feats.keys()) | set(hed_feats.keys()):
                agg_can[ft] += can_feats.get(ft, Counter())
                agg_hed[ft] += hed_feats.get(ft, Counter())

        rows = []
        for ft in sorted(agg_can.keys()):
            kl_c2h = self._kl_divergence(agg_can[ft], agg_hed.get(ft, Counter()))
            kl_h2c = self._kl_divergence(agg_hed.get(ft, Counter()), agg_can[ft])
            js = self._js_divergence(agg_can[ft], agg_hed.get(ft, Counter()))
            rows.append({
                'Feature_Type': ft,
                'KL_C_to_H': round(kl_c2h, 6),
                'KL_H_to_C': round(kl_h2c, 6),
                'JS_Divergence': round(js, 6),
            })
        pd.DataFrame(rows).to_csv(out / 'morph_feature_divergence.csv', index=False)
        print(f'  morph_feature_divergence.csv ({len(rows)} rows)')

        # --- 4. deprel_divergence ---
        rows = []
        for newspaper in self.newspapers:
            can_dep = self.deprel_distributions.get(newspaper, {}).get('canonical', Counter())
            hed_dep = self.deprel_distributions.get(newspaper, {}).get('headline', Counter())
            kl_c2h = self._kl_divergence(can_dep, hed_dep)
            kl_h2c = self._kl_divergence(hed_dep, can_dep)
            js = self._js_divergence(can_dep, hed_dep)
            rows.append({
                'Newspaper': newspaper,
                'KL_C_to_H': round(kl_c2h, 6),
                'KL_H_to_C': round(kl_h2c, 6),
                'JS_Divergence': round(js, 6),
            })
        pd.DataFrame(rows).to_csv(out / 'deprel_divergence.csv', index=False)
        print(f'  deprel_divergence.csv ({len(rows)} rows)')

    def generate_task3_figures(self):
        """Generate 4 PNG figures for Task 3."""
        out = self.task3_dir / 'figures'
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*80}")
        print('TASK 3: Generating figures')
        print(f"{'='*80}\n")

        # --- 1. morph_feature_entropy_comparison (grouped bar) ---
        csv = self.task3_dir / 'tables' / 'morph_feature_entropy.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            # Aggregate across newspapers by averaging
            agg = df.groupby('Feature_Type')[['Canonical_Entropy', 'Headline_Entropy']].mean()
            agg = agg.sort_values('Canonical_Entropy', ascending=False)

            fig, ax = plt.subplots(figsize=(12, 6))
            x = np.arange(len(agg))
            w = 0.35
            ax.bar(x - w/2, agg['Canonical_Entropy'], w, label='Canonical', color='steelblue')
            ax.bar(x + w/2, agg['Headline_Entropy'], w, label='Headline', color='coral')
            ax.set_xticks(x)
            ax.set_xticklabels(agg.index, rotation=45, ha='right')
            ax.set_ylabel('Shannon Entropy (bits)')
            ax.set_title('Morphological Feature Entropy: Canonical vs Headline')
            ax.legend()
            fig.savefig(out / 'morph_feature_entropy_comparison.png')
            plt.close(fig)
            print('  morph_feature_entropy_comparison.png')

        # --- 2. deprel_entropy_comparison (grouped bar) ---
        csv = self.task3_dir / 'tables' / 'deprel_entropy.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(df))
            w = 0.35
            ax.bar(x - w/2, df['Canonical_Entropy'], w, label='Canonical', color='steelblue')
            ax.bar(x + w/2, df['Headline_Entropy'], w, label='Headline', color='coral')
            ax.set_xticks(x)
            ax.set_xticklabels(df['Newspaper'], rotation=0)
            ax.set_ylabel('Shannon Entropy (bits)')
            ax.set_title('Dependency Relation Entropy: Canonical vs Headline')
            ax.legend()
            fig.savefig(out / 'deprel_entropy_comparison.png')
            plt.close(fig)
            print('  deprel_entropy_comparison.png')

        # --- 3. morph_feature_divergence (bar + line) ---
        csv = self.task3_dir / 'tables' / 'morph_feature_divergence.csv'
        if csv.exists():
            df = pd.read_csv(csv).sort_values('JS_Divergence', ascending=False)
            fig, ax1 = plt.subplots(figsize=(12, 6))
            x = np.arange(len(df))
            w = 0.3
            ax1.bar(x - w/2, df['KL_C_to_H'], w, label='KL(Canonical||Reduced)', color='steelblue')
            ax1.bar(x + w/2, df['KL_H_to_C'], w, label='KL(Reduced||Canonical)', color='coral')
            ax1.set_xticks(x)
            ax1.set_xticklabels(df['Feature_Type'], rotation=45, ha='right')
            ax1.set_ylabel('KL Divergence (bits)')
            ax1.legend(loc='upper left')

            ax2 = ax1.twinx()
            ax2.plot(x, df['JS_Divergence'].values, 'g^-', label='JS Divergence', markersize=8)
            ax2.set_ylabel('JS Divergence (bits)', color='green')
            ax2.legend(loc='upper right')

            ax1.set_title('Morphological Feature Divergence: Canonical vs Headline')
            fig.savefig(out / 'morph_feature_divergence.png')
            plt.close(fig)
            print('  morph_feature_divergence.png')

        # --- 4. deprel_complexity_ratio (horizontal bar) ---
        csv = self.task3_dir / 'tables' / 'deprel_entropy.csv'
        if csv.exists():
            df = pd.read_csv(csv)
            df['Entropy_Ratio'] = df['Canonical_Entropy'] / df['Headline_Entropy'].replace(0, np.nan)
            df = df.dropna(subset=['Entropy_Ratio'])
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = [NEWSPAPER_COLORS.get(n, '#999') for n in df['Newspaper']]
            bars = ax.barh(df['Newspaper'], df['Entropy_Ratio'], color=colors)
            ax.axvline(x=1.0, color='red', linestyle='--', linewidth=1, label='Ratio = 1.0')
            ax.set_xlabel('Canonical / Headline Entropy Ratio')
            ax.set_title('Dependency Relation Complexity Ratio by Newspaper')
            ax.legend()
            # Add labels
            for bar, ratio in zip(bars, df['Entropy_Ratio']):
                ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                        f'{ratio:.4f}', va='center', fontsize=9)
            fig.savefig(out / 'deprel_complexity_ratio.png')
            plt.close(fig)
            print('  deprel_complexity_ratio.png')

    # ------------------------------------------------------------------
    # LaTeX conversion & distribution
    # ------------------------------------------------------------------

    def convert_csvs_to_tex(self):
        """Convert all generated CSVs to .tex files alongside them."""
        print(f"\n{'='*80}")
        print('CONVERTING CSVs TO LaTeX')
        print(f"{'='*80}\n")

        for task_label, task_dir in [('task1', self.task1_dir),
                                      ('task2', self.task2_dir),
                                      ('task3', self.task3_dir)]:
            tables_dir = task_dir / 'tables'
            if not tables_dir.exists():
                continue
            for csv_path in sorted(tables_dir.glob('*.csv')):
                tex_path = save_tex(csv_path, task_label, tables_dir)
                if tex_path:
                    print(f'  {tex_path.name}')

    def distribute_to_latex(self):
        """Copy tables and figures to the appropriate LaTeX directories."""
        print(f"\n{'='*80}")
        print('DISTRIBUTING TO LaTeX DIRECTORIES')
        print(f"{'='*80}\n")

        def _copy_files(src_dir: Path, pattern: str, dest_dir: Path, label: str):
            dest_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for f in sorted(src_dir.glob(pattern)):
                shutil.copy2(f, dest_dir / f.name)
                count += 1
            if count:
                print(f'  {label}: {count} files -> {dest_dir}')

        # ==== Task 1 ====
        # Tables -> LaTeX/...Part-1.../tables/
        _copy_files(self.task1_dir / 'tables', '*.tex',
                    LATEX_TASK1_DIR / 'tables', 'Task1 tables')
        # Figures -> LaTeX/...Part-1.../latex/figures/global/
        _copy_files(self.task1_dir / 'figures', '*.png',
                    LATEX_TASK1_DIR / 'latex' / 'figures' / 'global', 'Task1 figures')

        # ==== Task 2 ====
        t2_comp_tables = LATEX_TASK2_BASE / 'latex-comprehensive' / 'tables'
        t2_comp_figs = LATEX_TASK2_BASE / 'latex-comprehensive' / 'figures' / 'global'
        t2_sel_tables_min = LATEX_TASK2_BASE / 'latex-selected' / 'tables' / 'minimal-set'
        t2_sel_tables_long = LATEX_TASK2_BASE / 'latex-selected' / 'tables' / 'longer-set'
        t2_sel_figs_min = LATEX_TASK2_BASE / 'latex-selected' / 'figures' / 'minimal-set'
        t2_sel_figs_long = LATEX_TASK2_BASE / 'latex-selected' / 'figures' / 'longer-set'

        # Comprehensive: all 3 tables + 3 figures
        _copy_files(self.task2_dir / 'tables', '*.tex', t2_comp_tables, 'Task2 comprehensive tables')
        _copy_files(self.task2_dir / 'figures', '*.png', t2_comp_figs, 'Task2 comprehensive figures')

        # Selected minimal: morph_deprel_directionality
        for src_dir, pattern, dest, label in [
            (self.task2_dir / 'tables', 'morph_deprel_directionality.tex', t2_sel_tables_min, 'Task2 sel-min tables'),
            (self.task2_dir / 'figures', 'morph_deprel_directionality.png', t2_sel_figs_min, 'Task2 sel-min figures'),
        ]:
            dest.mkdir(parents=True, exist_ok=True)
            src = src_dir / pattern
            if src.exists():
                shutil.copy2(src, dest / src.name)
                print(f'  {label}: {src.name} -> {dest}')

        # Selected longer: + morph_rule_coverage_by_feature
        for src_dir, patterns, dest, label in [
            (self.task2_dir / 'tables',
             ['morph_deprel_directionality.tex', 'morph_rule_coverage_by_feature.tex'],
             t2_sel_tables_long, 'Task2 sel-long tables'),
            (self.task2_dir / 'figures',
             ['morph_deprel_directionality.png', 'morph_rule_coverage_by_feature.png'],
             t2_sel_figs_long, 'Task2 sel-long figures'),
        ]:
            dest.mkdir(parents=True, exist_ok=True)
            for p in patterns:
                src = src_dir / p
                if src.exists():
                    shutil.copy2(src, dest / src.name)
                    print(f'  {label}: {src.name} -> {dest}')

        # ==== Task 3 ====
        t3_comp_tables = LATEX_TASK3_BASE / 'latex-comprehensive' / 'tables'
        t3_comp_figs = LATEX_TASK3_BASE / 'latex-comprehensive' / 'figures' / 'global'
        t3_sel_tables_min = LATEX_TASK3_BASE / 'latex-selected' / 'tables' / 'minimal-set'
        t3_sel_tables_long = LATEX_TASK3_BASE / 'latex-selected' / 'tables' / 'longer-set'
        t3_sel_figs_min = LATEX_TASK3_BASE / 'latex-selected' / 'figures' / 'minimal-set'
        t3_sel_figs_long = LATEX_TASK3_BASE / 'latex-selected' / 'figures' / 'longer-set'

        # Comprehensive: all 4 tables + 4 figures
        _copy_files(self.task3_dir / 'tables', '*.tex', t3_comp_tables, 'Task3 comprehensive tables')
        _copy_files(self.task3_dir / 'figures', '*.png', t3_comp_figs, 'Task3 comprehensive figures')

        # Selected minimal: morph_feature_entropy
        for src_dir, pattern, dest, label in [
            (self.task3_dir / 'tables', 'morph_feature_entropy.tex', t3_sel_tables_min, 'Task3 sel-min tables'),
            (self.task3_dir / 'figures', 'morph_feature_entropy_comparison.png', t3_sel_figs_min, 'Task3 sel-min figures'),
        ]:
            dest.mkdir(parents=True, exist_ok=True)
            src = src_dir / pattern
            if src.exists():
                shutil.copy2(src, dest / src.name)
                print(f'  {label}: {src.name} -> {dest}')

        # Selected longer: + deprel_entropy
        for src_dir, patterns, dest, label in [
            (self.task3_dir / 'tables',
             ['morph_feature_entropy.tex', 'deprel_entropy.tex'],
             t3_sel_tables_long, 'Task3 sel-long tables'),
            (self.task3_dir / 'figures',
             ['morph_feature_entropy_comparison.png', 'deprel_entropy_comparison.png'],
             t3_sel_figs_long, 'Task3 sel-long figures'),
        ]:
            dest.mkdir(parents=True, exist_ok=True)
            for p in patterns:
                src = src_dir / p
                if src.exists():
                    shutil.copy2(src, dest / src.name)
                    print(f'  {label}: {src.name} -> {dest}')

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(self):
        """Count and report all generated outputs."""
        print(f"\n{'='*80}")
        print('VERIFICATION')
        print(f"{'='*80}\n")

        total_csv = 0
        total_tex = 0
        total_png = 0

        for label, task_dir in [('Task 1', self.task1_dir),
                                 ('Task 2', self.task2_dir),
                                 ('Task 3', self.task3_dir)]:
            csvs = list((task_dir / 'tables').glob('*.csv')) if (task_dir / 'tables').exists() else []
            texs = list((task_dir / 'tables').glob('*.tex')) if (task_dir / 'tables').exists() else []
            pngs = list((task_dir / 'figures').glob('*.png')) if (task_dir / 'figures').exists() else []
            print(f'  {label}: {len(csvs)} CSVs, {len(texs)} .tex, {len(pngs)} PNGs')
            total_csv += len(csvs)
            total_tex += len(texs)
            total_png += len(pngs)

        print(f'\n  TOTAL: {total_csv} CSVs, {total_tex} .tex, {total_png} PNGs')

        expected_csv = 13
        expected_png = 13
        if total_csv < expected_csv:
            print(f'  WARNING: Expected {expected_csv} CSVs, got {total_csv}')
        if total_png < expected_png:
            print(f'  WARNING: Expected {expected_png} PNGs, got {total_png}')

        # Check event counts
        print(f'\n  Event counts: FEAT-CHG={len(self.feat_events):,}, DEP-REL-CHG={len(self.deprel_events):,}')

    # ------------------------------------------------------------------
    # Main runner
    # ------------------------------------------------------------------

    def run(self, tasks: List[str] = None):
        """Run the full pipeline or selected tasks."""
        if tasks is None:
            tasks = ['task1', 'task2', 'task3']

        self.load_all_events()

        if 'task3' in tasks:
            self.load_conllu_distributions()

        if 'task1' in tasks:
            self.generate_task1_tables()
            self.generate_task1_figures()

        if 'task2' in tasks:
            self.generate_task2_tables()
            self.generate_task2_figures()

        if 'task3' in tasks:
            self.generate_task3_tables()
            self.generate_task3_figures()

        self.convert_csvs_to_tex()
        self.distribute_to_latex()
        self.verify()

        print(f"\n{'='*80}")
        print('DONE')
        print(f"{'='*80}\n")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate FEAT-CHG and DEP-REL-CHG tables & figures for all tasks')
    parser.add_argument('--task', choices=['task1', 'task2', 'task3', 'all'],
                        default='all', help='Which task(s) to generate (default: all)')
    args = parser.parse_args()

    tasks = ['task1', 'task2', 'task3'] if args.task == 'all' else [args.task]

    analyzer = MorphDepRelAnalyzer()
    analyzer.run(tasks)


if __name__ == '__main__':
    main()
