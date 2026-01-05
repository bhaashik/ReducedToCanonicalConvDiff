#!/usr/bin/env python3
"""
Enhanced Bidirectional Transformation System with Detailed Trace Output

Outputs:
A. Structured data of transformation rules applied (CSV/JSON)
B. Transformed sentences + specific difference events/rules triggered
C. Comprehensive mapping: [Original] → [Rules Applied] → [Transformed]

This implements a rule-based MT-like scenario for studying cross-register
complexity and similarity using morphosyntactic transformations only.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass, asdict
from collections import Counter
import spacy
from config import BASE_DIR
from paths_config import TEXT_FILES

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    import subprocess
    subprocess.run(["python3", "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load('en_core_web_sm')


@dataclass
class TransformationRule:
    """Represents a single transformation rule."""
    rule_id: str
    rule_type: str  # 'FW-DEL', 'FW-ADD', 'C-DEL', 'C-ADD', 'DEP-REL-CHG', etc.
    pattern: str
    action: str
    confidence: float = 1.0


@dataclass
class RuleApplication:
    """Records a single rule application."""
    rule_id: str
    rule_type: str
    source_token: str
    target_token: str
    position: int
    confidence: float


@dataclass
class TransformationTrace:
    """Complete trace of a transformation."""
    sentence_id: int
    source_sentence: str
    target_sentence: str
    direction: str  # 'C2H' or 'H2C'
    rules_applied: List[RuleApplication]
    intermediate_states: List[str]
    events_triggered: List[str]
    success: bool
    error_message: Optional[str] = None


class EnhancedTransformationEngine:
    """Enhanced transformation engine with detailed tracing."""

    def __init__(self, newspaper: str, project_root: Path):
        self.newspaper = newspaper
        self.project_root = project_root
        self.transformation_traces = []

        # Define transformation rules
        self.articles = {'a', 'an', 'the'}
        self.auxiliaries = {'is', 'are', 'was', 'were', 'be', 'been', 'being',
                           'has', 'have', 'had', 'do', 'does', 'did',
                           'will', 'would', 'shall', 'should', 'may', 'might',
                           'can', 'could', 'must'}

        # Initialize rule database
        self.rules = self.initialize_rules()

    def initialize_rules(self) -> Dict[str, TransformationRule]:
        """Initialize transformation rules."""
        rules = {}

        # Article deletion rules (C→H)
        for article in self.articles:
            rule_id = f"FW-DEL-ARTICLE-{article.upper()}"
            rules[rule_id] = TransformationRule(
                rule_id=rule_id,
                rule_type='FW-DEL',
                pattern=f"delete article '{article}'",
                action='DELETE',
                confidence=0.95
            )

        # Auxiliary deletion rules (C→H)
        for aux in self.auxiliaries:
            rule_id = f"FW-DEL-AUX-{aux.upper()}"
            rules[rule_id] = TransformationRule(
                rule_id=rule_id,
                rule_type='FW-DEL',
                pattern=f"delete auxiliary '{aux}'",
                action='DELETE',
                confidence=0.90
            )

        # Article addition rules (H→C)
        rules['FW-ADD-ARTICLE-A'] = TransformationRule(
            rule_id='FW-ADD-ARTICLE-A',
            rule_type='FW-ADD',
            pattern='add article "a" before consonant-initial noun',
            action='ADD',
            confidence=0.85
        )

        rules['FW-ADD-ARTICLE-AN'] = TransformationRule(
            rule_id='FW-ADD-ARTICLE-AN',
            rule_type='FW-ADD',
            pattern='add article "an" before vowel-initial noun',
            action='ADD',
            confidence=0.85
        )

        # Verb simplification rules (C→H)
        rules['FORM-CHG-VERB-LEMMA'] = TransformationRule(
            rule_id='FORM-CHG-VERB-LEMMA',
            rule_type='FORM-CHG',
            pattern='simplify verb to lemma form',
            action='MODIFY',
            confidence=0.80
        )

        # Punctuation addition (H→C)
        rules['C-ADD-PERIOD'] = TransformationRule(
            rule_id='C-ADD-PERIOD',
            rule_type='C-ADD',
            pattern='add sentence-final period',
            action='ADD',
            confidence=0.95
        )

        return rules

    def canonical_to_headline(self, canonical: str, sentence_id: int) -> TransformationTrace:
        """Transform canonical to headline with detailed tracing."""

        trace = TransformationTrace(
            sentence_id=sentence_id,
            source_sentence=canonical,
            target_sentence="",
            direction='C2H',
            rules_applied=[],
            intermediate_states=[canonical],
            events_triggered=[],
            success=True
        )

        try:
            doc = nlp(canonical)
            kept_tokens = []
            position = 0

            for token in doc:
                token_kept = True

                # Check for article deletion
                if token.lower_ in self.articles:
                    rule_id = f"FW-DEL-ARTICLE-{token.lower_.upper()}"
                    trace.rules_applied.append(RuleApplication(
                        rule_id=rule_id,
                        rule_type='FW-DEL',
                        source_token=token.text,
                        target_token='<DELETED>',
                        position=position,
                        confidence=self.rules[rule_id].confidence
                    ))
                    trace.events_triggered.append(f'FW-DEL:{token.lower_}→ABSENT')
                    token_kept = False

                # Check for auxiliary deletion
                elif token.lower_ in self.auxiliaries and token.dep_ == 'aux':
                    rule_id = f"FW-DEL-AUX-{token.lower_.upper()}"
                    trace.rules_applied.append(RuleApplication(
                        rule_id=rule_id,
                        rule_type='FW-DEL',
                        source_token=token.text,
                        target_token='<DELETED>',
                        position=position,
                        confidence=self.rules[rule_id].confidence
                    ))
                    trace.events_triggered.append(f'FW-DEL:{token.lower_}→ABSENT')
                    token_kept = False

                # Verb simplification
                elif token.pos_ == 'VERB' and token.tag_ in ['VBZ', 'VBD', 'VBP']:
                    trace.rules_applied.append(RuleApplication(
                        rule_id='FORM-CHG-VERB-LEMMA',
                        rule_type='FORM-CHG',
                        source_token=token.text,
                        target_token=token.lemma_,
                        position=position,
                        confidence=self.rules['FORM-CHG-VERB-LEMMA'].confidence
                    ))
                    trace.events_triggered.append(f'FORM-CHG:{token.text}→{token.lemma_}')
                    kept_tokens.append(token.lemma_)

                else:
                    if token_kept:
                        kept_tokens.append(token.text)

                position += 1

            # Create headline
            headline = ' '.join(kept_tokens)

            # Remove trailing punctuation
            if headline and headline[-1] in '.!?':
                trace.rules_applied.append(RuleApplication(
                    rule_id='C-DEL-PERIOD',
                    rule_type='C-DEL',
                    source_token=headline[-1],
                    target_token='<DELETED>',
                    position=len(kept_tokens),
                    confidence=0.95
                ))
                trace.events_triggered.append(f'C-DEL:PERIOD→ABSENT')
                headline = headline[:-1]

            trace.target_sentence = headline
            trace.intermediate_states.append(headline)

        except Exception as e:
            trace.success = False
            trace.error_message = str(e)
            trace.target_sentence = canonical  # Fallback

        return trace

    def headline_to_canonical(self, headline: str, sentence_id: int) -> TransformationTrace:
        """Transform headline to canonical with detailed tracing."""

        trace = TransformationTrace(
            sentence_id=sentence_id,
            source_sentence=headline,
            target_sentence="",
            direction='H2C',
            rules_applied=[],
            intermediate_states=[headline],
            events_triggered=[],
            success=True
        )

        try:
            doc = nlp(headline)
            result_tokens = []
            position = 0

            for i, token in enumerate(doc):
                # Add article before initial noun
                if token.pos_ in ['NOUN', 'PROPN'] and i == 0:
                    if token.pos_ == 'NOUN' and token.tag_ == 'NN':
                        first_char = token.text[0].lower()
                        if first_char in 'aeiou':
                            article = 'An'
                            rule_id = 'FW-ADD-ARTICLE-AN'
                        else:
                            article = 'A'
                            rule_id = 'FW-ADD-ARTICLE-A'

                        trace.rules_applied.append(RuleApplication(
                            rule_id=rule_id,
                            rule_type='FW-ADD',
                            source_token='<ABSENT>',
                            target_token=article,
                            position=position,
                            confidence=self.rules[rule_id].confidence
                        ))
                        trace.events_triggered.append(f'FW-ADD:ABSENT→{article.lower()}')
                        result_tokens.append(article)

                result_tokens.append(token.text)
                position += 1

            # Create canonical
            canonical = ' '.join(result_tokens)

            # Add sentence-final period
            if canonical and canonical[-1] not in '.!?':
                trace.rules_applied.append(RuleApplication(
                    rule_id='C-ADD-PERIOD',
                    rule_type='C-ADD',
                    source_token='<ABSENT>',
                    target_token='.',
                    position=position,
                    confidence=self.rules['C-ADD-PERIOD'].confidence
                ))
                trace.events_triggered.append('C-ADD:ABSENT→PERIOD')
                canonical += '.'

            trace.target_sentence = canonical
            trace.intermediate_states.append(canonical)

        except Exception as e:
            trace.success = False
            trace.error_message = str(e)
            trace.target_sentence = headline  # Fallback

        return trace

    def transform_all(self, aligned_data: List[Dict]) -> Dict:
        """Transform all sentence pairs in both directions with tracing."""

        c2h_traces = []
        h2c_traces = []

        for idx, pair in enumerate(aligned_data):
            # C→H transformation
            c2h_trace = self.canonical_to_headline(pair['canonical'], idx)
            c2h_traces.append(c2h_trace)

            # H→C transformation
            h2c_trace = self.headline_to_canonical(pair['headline'], idx)
            h2c_traces.append(h2c_trace)

        return {
            'c2h_traces': c2h_traces,
            'h2c_traces': h2c_traces
        }


class TransformationTraceWriter:
    """Writes transformation traces to various output formats."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_all_formats(self, newspaper: str, traces: Dict):
        """Write traces in all required formats (A, B, C)."""

        c2h_traces = traces['c2h_traces']
        h2c_traces = traces['h2c_traces']

        # Option A: Structured rule applications (CSV/JSON)
        self.write_rule_applications_csv(newspaper, c2h_traces, h2c_traces)
        self.write_rule_applications_json(newspaper, c2h_traces, h2c_traces)

        # Option B: Transformed sentences + events (CSV)
        self.write_transformation_results(newspaper, c2h_traces, h2c_traces)

        # Option C: Comprehensive mapping (detailed CSV + JSON)
        self.write_comprehensive_mapping(newspaper, c2h_traces, h2c_traces)

        print(f"✓ Written all transformation traces for {newspaper}")

    def write_rule_applications_csv(self, newspaper: str, c2h_traces: List, h2c_traces: List):
        """Option A: CSV of all rule applications."""

        rows = []
        for trace in c2h_traces + h2c_traces:
            for app in trace.rules_applied:
                rows.append({
                    'sentence_id': trace.sentence_id,
                    'direction': trace.direction,
                    'rule_id': app.rule_id,
                    'rule_type': app.rule_type,
                    'source_token': app.source_token,
                    'target_token': app.target_token,
                    'position': app.position,
                    'confidence': app.confidence
                })

        df = pd.DataFrame(rows)
        output_path = self.output_dir / f'{newspaper}_rule_applications.csv'
        df.to_csv(output_path, index=False)
        print(f"  → {output_path.name}")

    def write_rule_applications_json(self, newspaper: str, c2h_traces: List, h2c_traces: List):
        """Option A: JSON of all rule applications."""

        data = {
            'newspaper': newspaper,
            'c2h': [self._trace_to_dict(t) for t in c2h_traces],
            'h2c': [self._trace_to_dict(t) for t in h2c_traces]
        }

        output_path = self.output_dir / f'{newspaper}_rule_applications.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  → {output_path.name}")

    def write_transformation_results(self, newspaper: str, c2h_traces: List, h2c_traces: List):
        """Option B: Transformed sentences + events triggered."""

        # C2H results
        c2h_rows = []
        for trace in c2h_traces:
            c2h_rows.append({
                'sentence_id': trace.sentence_id,
                'source_canonical': trace.source_sentence,
                'generated_headline': trace.target_sentence,
                'rules_applied_count': len(trace.rules_applied),
                'events_triggered': '|'.join(trace.events_triggered),
                'success': trace.success,
                'error': trace.error_message or ''
            })

        df_c2h = pd.DataFrame(c2h_rows)
        output_path = self.output_dir / f'{newspaper}_C2H_transformations.csv'
        df_c2h.to_csv(output_path, index=False)
        print(f"  → {output_path.name}")

        # H2C results
        h2c_rows = []
        for trace in h2c_traces:
            h2c_rows.append({
                'sentence_id': trace.sentence_id,
                'source_headline': trace.source_sentence,
                'generated_canonical': trace.target_sentence,
                'rules_applied_count': len(trace.rules_applied),
                'events_triggered': '|'.join(trace.events_triggered),
                'success': trace.success,
                'error': trace.error_message or ''
            })

        df_h2c = pd.DataFrame(h2c_rows)
        output_path = self.output_dir / f'{newspaper}_H2C_transformations.csv'
        df_h2c.to_csv(output_path, index=False)
        print(f"  → {output_path.name}")

    def write_comprehensive_mapping(self, newspaper: str, c2h_traces: List, h2c_traces: List):
        """Option C: Comprehensive [Original] → [Rules] → [Transformed] mapping."""

        # Detailed CSV with rule chains
        rows = []
        for trace in c2h_traces + h2c_traces:
            rule_chain = ' → '.join([app.rule_id for app in trace.rules_applied])
            token_changes = ' → '.join([
                f"{app.source_token}⇒{app.target_token}"
                for app in trace.rules_applied
            ])

            rows.append({
                'sentence_id': trace.sentence_id,
                'direction': trace.direction,
                'source': trace.source_sentence,
                'target': trace.target_sentence,
                'rule_chain': rule_chain,
                'token_changes': token_changes,
                'num_rules': len(trace.rules_applied),
                'events': '|'.join(trace.events_triggered),
                'success': trace.success
            })

        df = pd.DataFrame(rows)
        output_path = self.output_dir / f'{newspaper}_comprehensive_mapping.csv'
        df.to_csv(output_path, index=False)
        print(f"  → {output_path.name}")

        # Detailed JSON with all information
        detailed_data = {
            'newspaper': newspaper,
            'transformations': {
                'C2H': [self._trace_to_detailed_dict(t) for t in c2h_traces],
                'H2C': [self._trace_to_detailed_dict(t) for t in h2c_traces]
            }
        }

        output_path = self.output_dir / f'{newspaper}_comprehensive_mapping.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        print(f"  → {output_path.name}")

    def _trace_to_dict(self, trace: TransformationTrace) -> Dict:
        """Convert trace to dictionary (basic version)."""
        return {
            'sentence_id': trace.sentence_id,
            'source': trace.source_sentence,
            'target': trace.target_sentence,
            'direction': trace.direction,
            'rules_applied': [asdict(app) for app in trace.rules_applied],
            'events': trace.events_triggered,
            'success': trace.success
        }

    def _trace_to_detailed_dict(self, trace: TransformationTrace) -> Dict:
        """Convert trace to detailed dictionary (comprehensive version)."""
        return {
            'sentence_id': trace.sentence_id,
            'transformation': {
                'source': trace.source_sentence,
                'target': trace.target_sentence,
                'direction': trace.direction
            },
            'rules': [asdict(app) for app in trace.rules_applied],
            'intermediate_states': trace.intermediate_states,
            'events_triggered': trace.events_triggered,
            'statistics': {
                'num_rules_applied': len(trace.rules_applied),
                'num_events_triggered': len(trace.events_triggered),
                'success': trace.success
            },
            'error': trace.error_message
        }


def main():
    project_root = Path(BASE_DIR)
    newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']

    # Output directories
    output_dir = project_root / 'output' / 'complexity-similarity-study' / 'transformation-traces'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("ENHANCED BIDIRECTIONAL TRANSFORMATION WITH DETAILED TRACES")
    print("="*80)
    print()

    for newspaper in newspapers:
        print(f"\nProcessing: {newspaper}")
        print("-" * 60)

        # Load aligned data
        headline_path = TEXT_FILES[newspaper]['headlines']
        canonical_path = TEXT_FILES[newspaper]['canonical']

        with open(headline_path, 'r', encoding='utf-8') as f:
            headlines = [line.strip() for line in f if line.strip()]
        with open(canonical_path, 'r', encoding='utf-8') as f:
            canonicals = [line.strip() for line in f if line.strip()]

        aligned_data = [
            {'headline': h, 'canonical': c}
            for h, c in zip(headlines[:500], canonicals[:500])  # First 500 for now
        ]

        print(f"  Loaded {len(aligned_data)} sentence pairs")

        # Transform with tracing
        engine = EnhancedTransformationEngine(newspaper, project_root)
        traces = engine.transform_all(aligned_data)

        # Write outputs in all formats
        writer = TransformationTraceWriter(output_dir)
        writer.write_all_formats(newspaper, traces)

    print()
    print("="*80)
    print("✓ TRANSFORMATION TRACES COMPLETE")
    print("="*80)
    print(f"\nOutput directory: {output_dir}")
    print("\nFiles created per newspaper:")
    print("  - {newspaper}_rule_applications.csv (Option A)")
    print("  - {newspaper}_rule_applications.json (Option A)")
    print("  - {newspaper}_C2H_transformations.csv (Option B)")
    print("  - {newspaper}_H2C_transformations.csv (Option B)")
    print("  - {newspaper}_comprehensive_mapping.csv (Option C)")
    print("  - {newspaper}_comprehensive_mapping.json (Option C)")


if __name__ == '__main__':
    main()
