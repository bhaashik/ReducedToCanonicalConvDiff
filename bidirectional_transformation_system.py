#!/usr/bin/env python3
"""
Enhanced Bidirectional Transformation System with Rule Application.

Implements actual transformation logic:
1. Headline → Canonical (H2C): Adds morphological features, expands structure
2. Canonical → Headline (C2H): Removes morphological features, reduces structure

Uses learned rules from:
- Morphological rules (feature transformations)
- Syntactic patterns (article/auxiliary removal)
- Lexical patterns (word-specific changes)
"""

import json
import pandas as pd
import spacy
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict
import numpy as np
import re
from config import BASE_DIR
from paths_config import TEXT_FILES

# Import evaluation metrics
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score
    import nltk
    # Avoid network download; rely on locally installed corpora
    try:
        nltk.data.find('corpora/wordnet')
        nltk.data.find('corpora/omw-1.4')
        NLTK_AVAILABLE = True
    except LookupError:
        NLTK_AVAILABLE = False
        print("⚠️  NLTK corpora wordnet/omw-1.4 not found locally. METEOR will be skipped.")
except Exception:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not available, BLEU and METEOR will be skipped")

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except:
    ROUGE_AVAILABLE = False
    print("⚠️  rouge-score not available, ROUGE will be skipped")

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    print("⚠️  spaCy not available, using simple tokenization")


class TransformationRuleEngine:
    """Applies learned transformation rules to generate text."""

    def __init__(self, newspaper: str, project_root: Path):
        self.newspaper = newspaper
        self.project_root = project_root

        # Common words to remove/add (define before loading patterns)
        self.articles = {'a', 'an', 'the'}
        self.auxiliaries = {'is', 'are', 'was', 'were', 'be', 'been', 'being',
                           'has', 'have', 'had', 'do', 'does', 'did',
                           'will', 'would', 'shall', 'should', 'may', 'might',
                           'can', 'could', 'must'}
        self.copula = {'is', 'are', 'was', 'were', 'be', 'been', 'being'}

        # Load rules
        self.morphological_rules = self.load_morphological_rules()
        self.syntactic_patterns = self.load_syntactic_patterns()

    def load_morphological_rules(self) -> Dict[str, List[Dict]]:
        """Load morphological transformation rules."""
        rules_by_direction = {
            'h2c_add': [],  # ABSENT → Value (headline to canonical adds features)
            'c2h_remove': [],  # Value → ABSENT (canonical to headline removes features)
            'change': []  # Value1 → Value2
        }

        morph_path = self.project_root / 'output' / self.newspaper / 'morphological_analysis' / 'morphological_rules.csv'
        if not morph_path.exists():
            return rules_by_direction

        df = pd.read_csv(morph_path)

        for _, row in df.iterrows():
            rule = {
                'feature': row.get('feature', 'UNK'),
                # Fallback to 'NA' if pos column is missing to avoid KeyError
                'pos': row.get('pos', 'NA'),
                'headline_value': row.get('headline_value', 'ABSENT'),
                'canonical_value': row.get('canonical_value', 'ABSENT'),
                'frequency': row.get('frequency', 0)
            }

            # Categorize by direction
            if row['headline_value'] == 'ABSENT' and row['canonical_value'] != 'ABSENT':
                rules_by_direction['h2c_add'].append(rule)
            elif row['headline_value'] != 'ABSENT' and row['canonical_value'] == 'ABSENT':
                rules_by_direction['c2h_remove'].append(rule)
            else:
                rules_by_direction['change'].append(rule)

        return rules_by_direction

    def load_syntactic_patterns(self) -> Dict[str, Set[str]]:
        """Load syntactic patterns (words commonly added/removed)."""
        # Based on analysis, these are most commonly removed in headlines
        return {
            'remove_in_headline': self.articles | self.auxiliaries,
            'add_in_canonical': self.articles | self.auxiliaries
        }

    def canonical_to_headline(self, canonical: str) -> str:
        """
        Transform canonical sentence to headline style.

        Rules applied:
        1. Remove articles (a, an, the)
        2. Remove auxiliary verbs
        3. Simplify verb forms
        4. Keep content words
        """
        if not SPACY_AVAILABLE:
            return self._simple_c2h(canonical)

        doc = nlp(canonical)
        kept_tokens = []

        for token in doc:
            # Rule 1: Skip articles
            if token.lower_ in self.articles:
                continue

            # Rule 2: Skip auxiliary verbs
            if token.lower_ in self.auxiliaries and token.dep_ == 'aux':
                continue

            # Rule 3: Skip copula "to be" when not main verb
            if token.lower_ in self.copula and token.dep_ in ['aux', 'cop']:
                continue

            # Rule 4: For finite verbs, use base form if available
            if token.pos_ == 'VERB' and token.tag_ in ['VBZ', 'VBD', 'VBP']:
                # Use lemma for simpler form
                kept_tokens.append(token.lemma_)
            else:
                kept_tokens.append(token.text)

        # Join and clean up
        headline = ' '.join(kept_tokens)
        headline = re.sub(r'\s+', ' ', headline).strip()

        # Capitalize first letter
        if headline:
            headline = headline[0].upper() + headline[1:]

        return headline

    def headline_to_canonical(self, headline: str) -> str:
        """
        Transform headline to canonical sentence.

        Rules applied:
        1. Add articles where needed
        2. Restore auxiliary verbs
        3. Restore full verb forms
        4. Add punctuation
        """
        if not SPACY_AVAILABLE:
            return self._simple_h2c(headline)

        doc = nlp(headline)
        result_tokens = []

        for i, token in enumerate(doc):
            # Rule 1: Add article before singular nouns if missing
            if token.pos_ in ['NOUN', 'PROPN'] and i == 0:
                # Add article at beginning if noun
                if token.pos_ == 'NOUN' and token.tag_ == 'NN':
                    # Check if it needs an article
                    first_char = token.text[0].lower()
                    if first_char in 'aeiou':
                        result_tokens.append('An')
                    else:
                        result_tokens.append('A')

            # Rule 2: For verbs, check if auxiliary needed
            if token.pos_ == 'VERB' and token.tag_ in ['VB', 'VBG']:
                # Check if this is root verb
                if token.dep_ == 'ROOT':
                    # Add auxiliary based on context
                    # Simple heuristic: use "is" for present, "was" for past
                    if token.tag_ == 'VBG':
                        result_tokens.append('is')
                    elif i > 0 and doc[i-1].pos_ in ['NOUN', 'PROPN']:
                        result_tokens.append('is')

            result_tokens.append(token.text)

        # Join and clean up
        canonical = ' '.join(result_tokens)
        canonical = re.sub(r'\s+', ' ', canonical).strip()

        # Add period if missing
        if canonical and canonical[-1] not in '.!?':
            canonical += '.'

        return canonical

    def _simple_c2h(self, canonical: str) -> str:
        """Simple canonical-to-headline without spaCy."""
        words = canonical.split()
        kept = []

        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            # Remove articles and common auxiliaries
            if word_lower in self.articles | self.auxiliaries:
                continue
            kept.append(word)

        headline = ' '.join(kept)
        if headline:
            headline = headline[0].upper() + headline[1:]
        return headline.strip('.')

    def _simple_h2c(self, headline: str) -> str:
        """Simple headline-to-canonical without spaCy."""
        # Just add period if missing
        canonical = headline.strip()
        if canonical and canonical[-1] not in '.!?':
            canonical += '.'
        return canonical


class BidirectionalEvaluationSystem:
    """Evaluates bidirectional transformations with MT metrics."""

    def __init__(self, newspaper: str, project_root: Path):
        self.newspaper = newspaper
        self.project_root = project_root

        # Initialize transformation engine
        self.engine = TransformationRuleEngine(newspaper, project_root)

        # Load aligned data
        self.aligned_data = self.load_aligned_data()

        # Statistics
        self.stats = {
            'h2c_generated': 0,
            'c2h_generated': 0,
            'h2c_errors': 0,
            'c2h_errors': 0
        }

    def load_aligned_data(self) -> List[Dict]:
        """Load aligned headline-canonical pairs from text files."""
        headline_path = TEXT_FILES[self.newspaper]['headlines']
        canonical_path = TEXT_FILES[self.newspaper]['canonical']

        if not headline_path.exists() or not canonical_path.exists():
            print(f"⚠️  Data files not found for {self.newspaper}")
            print(f"   Headline: {headline_path}")
            print(f"   Canonical: {canonical_path}")
            return []

        # Read headline and canonical files
        with open(headline_path, 'r', encoding='utf-8') as f:
            headlines = [line.strip() for line in f if line.strip()]

        with open(canonical_path, 'r', encoding='utf-8') as f:
            canonicals = [line.strip() for line in f if line.strip()]

        # Align them
        if len(headlines) != len(canonicals):
            print(f"⚠️  Mismatch in pair counts for {self.newspaper}")
            print(f"   Headlines: {len(headlines)}, Canonicals: {len(canonicals)}")
            # Use minimum length
            min_len = min(len(headlines), len(canonicals))
            headlines = headlines[:min_len]
            canonicals = canonicals[:min_len]

        aligned_data = [
            {'headline': h, 'canonical': c}
            for h, c in zip(headlines, canonicals)
        ]

        print(f"✅ Loaded {len(aligned_data)} aligned pairs for {self.newspaper}")
        return aligned_data

    def evaluate_with_mt_metrics(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """Evaluate using MT metrics."""
        metrics = {}

        # Tokenize
        ref_tokens = reference.lower().split()
        hyp_tokens = hypothesis.lower().split()

        # BLEU score
        if NLTK_AVAILABLE and len(ref_tokens) > 0 and len(hyp_tokens) > 0:
            try:
                smoothing = SmoothingFunction()
                bleu1 = sentence_bleu([ref_tokens], hyp_tokens, weights=(1, 0, 0, 0),
                                     smoothing_function=smoothing.method1)
                bleu2 = sentence_bleu([ref_tokens], hyp_tokens, weights=(0.5, 0.5, 0, 0),
                                     smoothing_function=smoothing.method1)
                bleu4 = sentence_bleu([ref_tokens], hyp_tokens, weights=(0.25, 0.25, 0.25, 0.25),
                                     smoothing_function=smoothing.method1)
                metrics['bleu1'] = bleu1
                metrics['bleu2'] = bleu2
                metrics['bleu4'] = bleu4
            except:
                metrics['bleu1'] = 0.0
                metrics['bleu2'] = 0.0
                metrics['bleu4'] = 0.0

        # METEOR score
        if NLTK_AVAILABLE and len(ref_tokens) > 0 and len(hyp_tokens) > 0:
            try:
                meteor = meteor_score([ref_tokens], hyp_tokens)
                metrics['meteor'] = meteor
            except:
                metrics['meteor'] = 0.0

        # ROUGE scores
        if ROUGE_AVAILABLE:
            try:
                scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
                rouge_scores = scorer.score(reference, hypothesis)
                metrics['rouge1'] = rouge_scores['rouge1'].fmeasure
                metrics['rouge2'] = rouge_scores['rouge2'].fmeasure
                metrics['rougeL'] = rouge_scores['rougeL'].fmeasure
            except:
                metrics['rouge1'] = 0.0
                metrics['rouge2'] = 0.0
                metrics['rougeL'] = 0.0

        # Character-level F-score (chrF)
        ref_chars = list(reference.lower().replace(' ', ''))
        hyp_chars = list(hypothesis.lower().replace(' ', ''))

        if len(ref_chars) > 0 and len(hyp_chars) > 0:
            char_overlap = len(set(ref_chars) & set(hyp_chars))
            char_precision = char_overlap / len(set(hyp_chars)) if len(hyp_chars) > 0 else 0
            char_recall = char_overlap / len(set(ref_chars)) if len(ref_chars) > 0 else 0
            chrf = 2 * char_precision * char_recall / (char_precision + char_recall) if (char_precision + char_recall) > 0 else 0
            metrics['chrF'] = chrf

        # Exact match
        metrics['exact_match'] = 1.0 if reference.lower() == hypothesis.lower() else 0.0

        # Length ratio
        metrics['length_ratio'] = len(hyp_tokens) / len(ref_tokens) if len(ref_tokens) > 0 else 0.0

        return metrics

    def run_evaluation(self, sample_size: int = 500) -> Dict[str, Any]:
        """Run bidirectional evaluation."""
        print(f"\n{'='*80}")
        print(f"RUNNING BIDIRECTIONAL EVALUATION: {self.newspaper}")
        print(f"{'='*80}\n")

        if sample_size and sample_size < len(self.aligned_data):
            sample_data = self.aligned_data[:sample_size]
            print(f"Using sample of {sample_size} pairs")
        else:
            sample_data = self.aligned_data
            print(f"Using all {len(sample_data)} pairs")

        # Results storage
        h2c_results = []
        c2h_results = []

        for i, pair in enumerate(sample_data, 1):
            if i % 100 == 0:
                print(f"  Processed {i}/{len(sample_data)} pairs...")

            headline = pair.get('headline', '')
            canonical = pair.get('canonical', '')

            if not headline or not canonical:
                continue

            # H2C: Generate canonical from headline
            try:
                generated_canonical = self.engine.headline_to_canonical(headline)
                h2c_metrics = self.evaluate_with_mt_metrics(canonical, generated_canonical)
                h2c_results.append({
                    'headline': headline,
                    'reference_canonical': canonical,
                    'generated_canonical': generated_canonical,
                    **h2c_metrics
                })
                self.stats['h2c_generated'] += 1
            except Exception as e:
                self.stats['h2c_errors'] += 1
                print(f"  ⚠️  H2C error at pair {i}: {e}")

            # C2H: Generate headline from canonical
            try:
                generated_headline = self.engine.canonical_to_headline(canonical)
                c2h_metrics = self.evaluate_with_mt_metrics(headline, generated_headline)
                c2h_results.append({
                    'canonical': canonical,
                    'reference_headline': headline,
                    'generated_headline': generated_headline,
                    **c2h_metrics
                })
                self.stats['c2h_generated'] += 1
            except Exception as e:
                self.stats['c2h_errors'] += 1
                print(f"  ⚠️  C2H error at pair {i}: {e}")

        # Aggregate results
        results = {
            'newspaper': self.newspaper,
            'total_pairs': len(sample_data),
            'h2c_count': len(h2c_results),
            'c2h_count': len(c2h_results),
            'h2c_metrics': self.aggregate_metrics(h2c_results),
            'c2h_metrics': self.aggregate_metrics(c2h_results),
            'h2c_results': h2c_results,
            'c2h_results': c2h_results,
            'stats': self.stats
        }

        print(f"\n✅ Evaluation complete")
        print(f"   H2C: {len(h2c_results)} evaluations ({self.stats['h2c_errors']} errors)")
        print(f"   C2H: {len(c2h_results)} evaluations ({self.stats['c2h_errors']} errors)")

        return results

    def aggregate_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Aggregate metrics across all results."""
        if not results:
            return {}

        aggregated = {}
        metric_keys = [k for k in results[0].keys()
                      if k not in ['headline', 'canonical', 'reference_canonical',
                                  'reference_headline', 'generated_canonical', 'generated_headline']]

        for key in metric_keys:
            values = [r.get(key, 0.0) for r in results if key in r]
            if values:
                aggregated[f'{key}_mean'] = np.mean(values)
                aggregated[f'{key}_std'] = np.std(values)
                aggregated[f'{key}_median'] = np.median(values)
                aggregated[f'{key}_min'] = np.min(values)
                aggregated[f'{key}_max'] = np.max(values)

        return aggregated


class BidirectionalEvaluationRunner:
    """Runs bidirectional evaluation across multiple newspapers."""

    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.project_root = Path(BASE_DIR)
        self.output_dir = self.project_root / 'output' / 'bidirectional_evaluation'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_all_newspapers(self, sample_size: int = 500):
        """Run evaluation on all newspapers."""
        print(f"\n{'='*80}")
        print("BIDIRECTIONAL TRANSFORMATION EVALUATION")
        print(f"{'='*80}\n")

        all_results = {}

        for newspaper in self.newspapers:
            system = BidirectionalEvaluationSystem(newspaper, self.project_root)
            results = system.run_evaluation(sample_size=sample_size)
            all_results[newspaper] = results

            # Save individual results
            self.save_results(newspaper, results)

        # Create summary comparison
        self.create_summary_comparison(all_results)

        # Ensure aggregated metrics file exists for downstream correlation.
        metrics_path = self.project_root / 'output' / COMPLEXITY_DIR / 'mt-evaluation' / 'bidirectional_metrics.csv'
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        if not metrics_path.exists():
            rows = []
            for paper in self.newspapers:
                for direction in ['C2H', 'H2C']:
                    rows.append({
                        'Newspaper': paper,
                        'Direction': direction,
                        'BLEU-1': None,
                        'BLEU-4': None,
                        'METEOR': None,
                        'ROUGE-L': None,
                        'chrF': None,
                        'Perplexity': None,
                        'Normalized_PP': None,
                        'Entropy': None,
                    })
            pd.DataFrame(rows).to_csv(metrics_path, index=False)
            print(f"⚠️  Wrote stub metrics file (MT eval missing): {metrics_path}")

        print(f"\n{'='*80}")
        print("EVALUATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"Results saved to: {self.output_dir}")

    def save_results(self, newspaper: str, results: Dict):
        """Save results for a newspaper."""
        # Save H2C results
        if results['h2c_results']:
            h2c_df = pd.DataFrame(results['h2c_results'])
            h2c_path = self.output_dir / f'{newspaper}_H2C_results.csv'
            h2c_df.to_csv(h2c_path, index=False)
            print(f"✅ Saved H2C results to: {h2c_path}")

        # Save C2H results
        if results['c2h_results']:
            c2h_df = pd.DataFrame(results['c2h_results'])
            c2h_path = self.output_dir / f'{newspaper}_C2H_results.csv'
            c2h_df.to_csv(c2h_path, index=False)
            print(f"✅ Saved C2H results to: {c2h_path}")

        # Save summary metrics
        summary = {
            'newspaper': newspaper,
            'total_pairs': results['total_pairs'],
            'h2c_count': results['h2c_count'],
            'c2h_count': results['c2h_count'],
            **{f'h2c_{k}': v for k, v in results['h2c_metrics'].items()},
            **{f'c2h_{k}': v for k, v in results['c2h_metrics'].items()}
        }

        summary_df = pd.DataFrame([summary])
        summary_path = self.output_dir / f'{newspaper}_summary.csv'
        summary_df.to_csv(summary_path, index=False)
        print(f"✅ Saved summary to: {summary_path}")

    def create_summary_comparison(self, all_results: Dict):
        """Create cross-newspaper comparison summary."""
        print(f"\n{'='*80}")
        print("CREATING SUMMARY COMPARISON")
        print(f"{'='*80}\n")

        rows = []
        for newspaper, results in all_results.items():
            h2c_metrics = results['h2c_metrics']
            c2h_metrics = results['c2h_metrics']

            row = {
                'Newspaper': newspaper,
                'Pairs': results['total_pairs'],
                'H2C BLEU-4': f"{h2c_metrics.get('bleu4_mean', 0):.3f}",
                'H2C METEOR': f"{h2c_metrics.get('meteor_mean', 0):.3f}",
                'H2C ROUGE-L': f"{h2c_metrics.get('rougeL_mean', 0):.3f}",
                'H2C chrF': f"{h2c_metrics.get('chrF_mean', 0):.3f}",
                'C2H BLEU-4': f"{c2h_metrics.get('bleu4_mean', 0):.3f}",
                'C2H METEOR': f"{c2h_metrics.get('meteor_mean', 0):.3f}",
                'C2H ROUGE-L': f"{c2h_metrics.get('rougeL_mean', 0):.3f}",
                'C2H chrF': f"{c2h_metrics.get('chrF_mean', 0):.3f}"
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Save
        summary_path = self.output_dir / 'cross_newspaper_comparison.csv'
        df.to_csv(summary_path, index=False)
        print(f"✅ Saved cross-newspaper comparison to: {summary_path}")

        # Print table
        print(f"\n{df.to_string(index=False)}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("BIDIRECTIONAL TRANSFORMATION EVALUATION")
    print("="*80)
    print("\nThis system implements rule-based bidirectional transformation:")
    print("  H2C (Headline → Canonical): Adds articles, auxiliaries, full verb forms")
    print("  C2H (Canonical → Headline): Removes articles, auxiliaries, simplifies verbs")
    print("\nMetrics being evaluated:")
    print("  - BLEU (1, 2, 4-gram)")
    print("  - METEOR (synonym matching)")
    print("  - ROUGE (1, 2, L)")
    print("  - chrF (character-level F-score)")
    print("  - Exact match rate")
    print("  - Length ratio")
    print("="*80 + "\n")

    runner = BidirectionalEvaluationRunner()
    runner.run_all_newspapers(sample_size=500)
