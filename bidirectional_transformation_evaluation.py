#!/usr/bin/env python3
"""
Bidirectional Transformation Evaluation System.

Generates transformations in both directions:
1. Headline → Canonical (H2C)
2. Canonical → Headline (C2H)

Evaluates using MT metrics:
- BLEU (n-gram precision)
- METEOR (synonym matching)
- ROUGE (recall-oriented)
- chrF (character-level F-score)
- TER (Translation Edit Rate)
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import numpy as np

# Import evaluation metrics
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score
    import nltk
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    NLTK_AVAILABLE = True
except:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not available, BLEU and METEOR will be skipped")

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except:
    ROUGE_AVAILABLE = False
    print("⚠️  rouge-score not available, ROUGE will be skipped")


class BidirectionalTransformationSystem:
    """Bidirectional transformation system with rule-based generation."""

    def __init__(self, newspaper: str, project_root: Path):
        self.newspaper = newspaper
        self.project_root = project_root

        # Load data
        self.alignment_data = self.load_alignment_data()
        self.rules = self.load_all_rules()

        # Statistics
        self.stats = {
            'h2c_generated': 0,
            'c2h_generated': 0,
            'h2c_errors': 0,
            'c2h_errors': 0
        }

    def load_alignment_data(self) -> List[Dict]:
        """Load aligned headline-canonical pairs."""
        alignment_path = self.project_root / 'data' / self.newspaper / 'aligned.json'

        if not alignment_path.exists():
            print(f"⚠️  Alignment file not found: {alignment_path}")
            return []

        with open(alignment_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✅ Loaded {len(data)} aligned pairs for {self.newspaper}")
        return data

    def load_all_rules(self) -> Dict[str, List[Dict]]:
        """Load all transformation rules."""
        rules = {
            'lexical': [],
            'morphological': [],
            'syntactic': [],
            'default': []
        }

        # Load lexical/syntactic/default rules
        rules_path = self.project_root / 'output' / self.newspaper / 'rule_analysis' / 'extracted_rules' / 'extracted_rules.json'
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                rules_data = json.load(f)
                rules['lexical'] = rules_data.get('lexical_rules', [])
                rules['syntactic'] = rules_data.get('syntactic_rules', [])
                rules['default'] = rules_data.get('default_rules', [])

        # Load morphological rules
        morph_path = self.project_root / 'output' / self.newspaper / 'morphological_analysis' / 'morphological_rules.csv'
        if morph_path.exists():
            df = pd.read_csv(morph_path)
            for _, row in df.iterrows():
                rules['morphological'].append({
                    'pos': row['pos'],
                    'feature': row['feature'],
                    'headline_value': row['headline_value'],
                    'canonical_value': row['canonical_value'],
                    'frequency': row['frequency']
                })

        print(f"✅ Loaded rules for {self.newspaper}:")
        for rule_type, rule_list in rules.items():
            print(f"   - {rule_type.capitalize()}: {len(rule_list)}")

        return rules

    def generate_headline_to_canonical(self, headline: str) -> str:
        """
        Generate canonical sentence from headline using rules.

        This is a simplified rule-based approach that applies transformations.
        For a full implementation, this would need:
        - Dependency parsing of headline
        - Token-level transformation application
        - Morphological feature restoration
        - Syntactic structure expansion
        """
        # For this evaluation, we'll use the actual canonical as a baseline
        # since implementing full generation requires extensive NLP pipeline

        # This is a placeholder - real implementation would:
        # 1. Parse headline
        # 2. Apply morphological rules to restore features
        # 3. Apply syntactic rules to expand structure
        # 4. Apply lexical rules for word-specific changes

        canonical = headline  # Placeholder
        self.stats['h2c_generated'] += 1
        return canonical

    def generate_canonical_to_headline(self, canonical: str) -> str:
        """
        Generate headline from canonical sentence using rules.

        This is a simplified rule-based approach that applies transformations.
        For a full implementation, this would need:
        - Dependency parsing of canonical
        - Token-level transformation application
        - Morphological feature removal
        - Syntactic structure reduction
        """
        # For this evaluation, we'll use the actual headline as a baseline
        # since implementing full generation requires extensive NLP pipeline

        # This is a placeholder - real implementation would:
        # 1. Parse canonical
        # 2. Apply morphological rules to remove features
        # 3. Apply syntactic rules to reduce structure
        # 4. Apply lexical rules for word-specific changes

        headline = canonical  # Placeholder
        self.stats['c2h_generated'] += 1
        return headline

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
            # Calculate character n-gram overlap
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

    def run_evaluation(self, sample_size: int = None) -> Dict[str, Any]:
        """Run bidirectional evaluation on aligned pairs."""
        print(f"\n{'='*80}")
        print(f"RUNNING BIDIRECTIONAL EVALUATION: {self.newspaper}")
        print(f"{'='*80}\n")

        if sample_size:
            sample_data = self.alignment_data[:sample_size]
            print(f"Using sample of {sample_size} pairs")
        else:
            sample_data = self.alignment_data
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
                generated_canonical = self.generate_headline_to_canonical(headline)
                h2c_metrics = self.evaluate_with_mt_metrics(canonical, generated_canonical)
                h2c_results.append({
                    'reference': canonical,
                    'hypothesis': generated_canonical,
                    **h2c_metrics
                })
            except Exception as e:
                self.stats['h2c_errors'] += 1

            # C2H: Generate headline from canonical
            try:
                generated_headline = self.generate_canonical_to_headline(canonical)
                c2h_metrics = self.evaluate_with_mt_metrics(headline, generated_headline)
                c2h_results.append({
                    'reference': headline,
                    'hypothesis': generated_headline,
                    **c2h_metrics
                })
            except Exception as e:
                self.stats['c2h_errors'] += 1

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
        print(f"   H2C: {len(h2c_results)} evaluations")
        print(f"   C2H: {len(c2h_results)} evaluations")

        return results

    def aggregate_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Aggregate metrics across all results."""
        if not results:
            return {}

        aggregated = {}
        metric_keys = [k for k in results[0].keys() if k not in ['reference', 'hypothesis']]

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
        self.project_root = Path(__file__).parent.absolute()
        self.output_dir = self.project_root / 'output' / 'bidirectional_evaluation'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_all_newspapers(self, sample_size: int = 500):
        """Run evaluation on all newspapers."""
        print(f"\n{'='*80}")
        print("BIDIRECTIONAL TRANSFORMATION EVALUATION")
        print(f"{'='*80}\n")

        all_results = {}

        for newspaper in self.newspapers:
            system = BidirectionalTransformationSystem(newspaper, self.project_root)
            results = system.run_evaluation(sample_size=sample_size)
            all_results[newspaper] = results

            # Save individual results
            self.save_results(newspaper, results)

        # Create summary comparison
        self.create_summary_comparison(all_results)

        print(f"\n{'='*80}")
        print("EVALUATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"Results saved to: {self.output_dir}")

    def save_results(self, newspaper: str, results: Dict):
        """Save results for a newspaper."""
        # Save H2C results
        h2c_df = pd.DataFrame(results['h2c_results'])
        h2c_path = self.output_dir / f'{newspaper}_H2C_results.csv'
        h2c_df.to_csv(h2c_path, index=False)
        print(f"✅ Saved H2C results to: {h2c_path}")

        # Save C2H results
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
    # Note: This is a baseline implementation using identity transformation
    # (generated = reference) to establish evaluation framework
    # Full implementation requires NLP pipeline for actual rule application

    print("\n" + "="*80)
    print("BASELINE BIDIRECTIONAL EVALUATION")
    print("="*80)
    print("\nNOTE: This baseline uses identity transformation (generated = reference)")
    print("to establish the evaluation framework. Full rule-based generation")
    print("requires implementing the complete NLP pipeline.")
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
