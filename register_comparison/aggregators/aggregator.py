
# Version 1

from collections import defaultdict
from typing import List, Dict, Any
from register_comparison.comparators.comparator import DifferenceEvent

class Aggregator:
    """
    Aggregates DifferenceEvent records into summary counts and matrices
    for later statistical analysis and reporting.
    """

    def __init__(self):
        # Stores aggregated data
        self.by_newspaper: Dict[str, List[DifferenceEvent]] = defaultdict(list)
        self.by_parse_type: Dict[str, List[DifferenceEvent]] = defaultdict(list)
        self.global_events: List[DifferenceEvent] = []

    def add_events(self, events: List[DifferenceEvent]):
        """
        Add a list of DifferenceEvent objects to the aggregators.
        """
        for ev in events:
            self.by_newspaper[ev.newspaper].append(ev)
            self.by_parse_type[ev.parse_type].append(ev)
            self.global_events.append(ev)

    def feature_counts(self, events: List[DifferenceEvent]) -> Dict[str, int]:
        """
        Count how many times each feature appears in a given list of events.
        """
        counts = defaultdict(int)
        for ev in events:
            counts[ev.feature_id] += 1
        return dict(counts)

    def per_newspaper_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Get feature frequency counts for each newspaper.
        """
        result = {}
        for newspaper, evs in self.by_newspaper.items():
            result[newspaper] = self.feature_counts(evs)
        return result

    def per_parse_type_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Get feature frequency counts for each parse type (dep/const).
        """
        result = {}
        for ptype, evs in self.by_parse_type.items():
            result[ptype] = self.feature_counts(evs)
        return result

    def global_counts(self) -> Dict[str, int]:
        """
        Get feature frequency counts across all events.
        """
        return self.feature_counts(self.global_events)

    def to_matrix(self, events: List[DifferenceEvent]) -> List[Dict[str, Any]]:
        """
        Convert events into a list of dicts for CSV/DF creation.
        """
        return [ev.to_dict() for ev in events]

# from register_comparison.meta_data.schema import FeatureSchema
# from register_comparison.comparators.comparator import Comparator
# from aggregator import Aggregator
# from register_comparison.extractors.extractor import FeatureExtractor
# from register_comparison.aligners.aligner import Aligner

# Usage:

# 1. Load schema
# schema = FeatureSchema("data/diff-ontology-ver-3.0.json")
# schema.load_schema()
#
# # 2. Prepare aligner and get pairs (example, one newspaper setup)
# aligner = Aligner(
#     texts_canonical=schema.canon_text_list,
#     texts_headlines=head_text_list,
#     deps_canonical=canon_dep_list,
#     deps_headlines=head_dep_list,
#     consts_canonical=canon_const_list,
#     consts_headlines=head_const_list,
#     newspaper_name="Times-of-India"
# )
#
# pairs = aligner.align()
#
# # 3. Extract features
# extractor = FeatureExtractor(schema)
# comparator = Comparator(schema)
# aggregators = Aggregator()
#
# for pair in pairs:
#     features = extractor.extract_features(pair)
#     events = comparator.compare_pair(pair, features)
#     aggregators.add_events(events)
#
# # 4. Check counts
# print("Global counts:", aggregators.global_counts())
# print("Counts per newspaper:", aggregators.per_newspaper_counts())
#
# # 5. Convert to matrix for DataFrame/CSV
# matrix = aggregators.to_matrix(aggregators.global_events)

# Version 2

# from collections import defaultdict
# from typing import List, Dict, Any
from register_comparison.comparators.comparator import DifferenceEvent

class Aggregator:
    """
    Aggregates DifferenceEvent records into summary counts and matrices
    for later statistical analysis and reporting.
    """

    def __init__(self):
        # Stores aggregated data
        self.by_newspaper: Dict[str, List[DifferenceEvent]] = defaultdict(list)
        self.by_parse_type: Dict[str, List[DifferenceEvent]] = defaultdict(list)
        self.global_events: List[DifferenceEvent] = []

    def add_events(self, events: List[DifferenceEvent]):
        """
        Add a list of DifferenceEvent objects to the aggregator.
        """
        for ev in events:
            self.by_newspaper[ev.newspaper].append(ev)
            self.by_parse_type[ev.parse_type].append(ev)
            self.global_events.append(ev)

    def feature_counts(self, events: List[DifferenceEvent]) -> Dict[str, int]:
        """
        Count how many times each feature appears in a given list of events.
        """
        counts = defaultdict(int)
        for ev in events:
            counts[ev.feature_id] += 1
        return dict(counts)

    def per_newspaper_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Get feature frequency counts for each newspaper.
        """
        result = {}
        for newspaper, evs in self.by_newspaper.items():
            result[newspaper] = self.feature_counts(evs)
        return result

    def per_parse_type_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Get feature frequency counts for each parse type (dep/const).
        """
        result = {}
        for ptype, evs in self.by_parse_type.items():
            result[ptype] = self.feature_counts(evs)
        return result

    def global_counts(self) -> Dict[str, int]:
        """
        Get feature frequency counts across all events.
        """
        return self.feature_counts(self.global_events)

    def to_matrix(self, events: List[DifferenceEvent]) -> List[Dict[str, Any]]:
        """
        Convert events into a list of dicts for CSV/DF creation.
        """
        return [ev.to_dict() for ev in events]

    def to_stats_runner_format(self) -> List[Dict[str, Any]]:
        """
        Convert feature counts to format expected by StatsRunner for statistical testing.
        Creates proper contingency table data comparing canonical vs headline register usage.
        Returns data in format: feature_id, count_a, total_a, count_b, total_b
        """
        # Count total contexts (unique sentence pairs)
        contexts = set()
        for event in self.global_events:
            contexts.add(f"{event.newspaper}_{event.sent_id}")

        total_contexts = len(contexts)

        # Count feature occurrences per context for each register
        canonical_feature_contexts = {}  # feature_id -> set of contexts where it appears in canonical
        headline_feature_contexts = {}   # feature_id -> set of contexts where it appears in headline

        for event in self.global_events:
            context_id = f"{event.newspaper}_{event.sent_id}"
            feature_id = event.feature_id

            # Initialize if needed
            if feature_id not in canonical_feature_contexts:
                canonical_feature_contexts[feature_id] = set()
            if feature_id not in headline_feature_contexts:
                headline_feature_contexts[feature_id] = set()

            # Determine which register(s) this feature applies to based on values
            if event.canonical_value and event.canonical_value != "ABSENT":
                canonical_feature_contexts[feature_id].add(context_id)
            if event.headline_value and event.headline_value != "ABSENT":
                headline_feature_contexts[feature_id].add(context_id)

        # Convert to StatsRunner format
        stats_data = []
        all_features = set(canonical_feature_contexts.keys()) | set(headline_feature_contexts.keys())

        for feature_id in all_features:
            canonical_count = len(canonical_feature_contexts.get(feature_id, set()))
            headline_count = len(headline_feature_contexts.get(feature_id, set()))

            stats_data.append({
                "feature_id": feature_id,
                "count_a": canonical_count,      # contexts where feature appears in canonical
                "total_a": total_contexts,       # total canonical contexts
                "count_b": headline_count,       # contexts where feature appears in headline
                "total_b": total_contexts        # total headline contexts
            })

        return stats_data

    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive multi-dimensional analysis of all events.
        """
        analysis = {
            'global': {
                'total_events': len(self.global_events),
                'feature_counts': self.global_counts(),
                'parse_type_breakdown': self.per_parse_type_counts(),
            },
            'by_newspaper': {},
            'by_parse_type': {},
            'cross_analysis': {}
        }

        # Per-newspaper analysis
        for newspaper, events in self.by_newspaper.items():
            analysis['by_newspaper'][newspaper] = {
                'total_events': len(events),
                'feature_counts': self.feature_counts(events),
                'parse_type_breakdown': self._get_parse_type_breakdown_for_events(events),
                'feature_value_pairs': self._get_feature_value_pairs(events)
            }

        # Per-parse-type analysis
        for parse_type, events in self.by_parse_type.items():
            analysis['by_parse_type'][parse_type] = {
                'total_events': len(events),
                'feature_counts': self.feature_counts(events),
                'newspaper_breakdown': self._get_newspaper_breakdown_for_events(events),
                'feature_value_pairs': self._get_feature_value_pairs(events)
            }

        # Cross-analysis: newspaper × parse_type combinations
        for newspaper in self.by_newspaper.keys():
            for parse_type in self.by_parse_type.keys():
                key = f"{newspaper}_{parse_type}"
                filtered_events = [ev for ev in self.global_events
                                 if ev.newspaper == newspaper and ev.parse_type == parse_type]

                analysis['cross_analysis'][key] = {
                    'total_events': len(filtered_events),
                    'feature_counts': self.feature_counts(filtered_events),
                    'feature_value_pairs': self._get_feature_value_pairs(filtered_events)
                }

        return analysis

    def _get_parse_type_breakdown_for_events(self, events: List[DifferenceEvent]) -> Dict[str, Dict[str, int]]:
        """Get parse type breakdown for a given set of events."""
        breakdown = defaultdict(lambda: defaultdict(int))
        for event in events:
            breakdown[event.parse_type][event.feature_id] += 1
        return dict(breakdown)

    def _get_newspaper_breakdown_for_events(self, events: List[DifferenceEvent]) -> Dict[str, Dict[str, int]]:
        """Get newspaper breakdown for a given set of events."""
        breakdown = defaultdict(lambda: defaultdict(int))
        for event in events:
            breakdown[event.newspaper][event.feature_id] += 1
        return dict(breakdown)

    def _get_feature_value_pairs(self, events: List[DifferenceEvent]) -> Dict[str, Dict[str, int]]:
        """Get canonical→headline value pair frequencies for features."""
        pairs = defaultdict(lambda: defaultdict(int))
        for event in events:
            pair_key = f"{event.canonical_value}→{event.headline_value}"
            pairs[event.feature_id][pair_key] += 1
        return dict(pairs)

    def get_feature_value_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive feature-value level analysis for ALL features.
        This provides fine-grained analysis of what specific values are changing.
        """
        analysis = {
            'global_feature_values': {},
            'by_newspaper_feature_values': {},
            'by_parse_type_feature_values': {},
            'cross_feature_values': {},
            'transformation_patterns': {},
            'value_statistics': {}
        }

        # Global feature-value analysis
        global_pairs = self._get_feature_value_pairs(self.global_events)
        analysis['global_feature_values'] = global_pairs

        # By newspaper feature-value analysis
        for newspaper in self.by_newspaper.keys():
            newspaper_pairs = self._get_feature_value_pairs(self.by_newspaper[newspaper])
            analysis['by_newspaper_feature_values'][newspaper] = newspaper_pairs

        # By parse type feature-value analysis
        for parse_type in self.by_parse_type.keys():
            parse_type_pairs = self._get_feature_value_pairs(self.by_parse_type[parse_type])
            analysis['by_parse_type_feature_values'][parse_type] = parse_type_pairs

        # Cross-dimensional feature-value analysis (consistent with comprehensive analysis)
        for newspaper in self.by_newspaper.keys():
            for parse_type in self.by_parse_type.keys():
                key = f"{newspaper}_{parse_type}"
                filtered_events = [ev for ev in self.global_events
                                 if ev.newspaper == newspaper and ev.parse_type == parse_type]
                combo_pairs = self._get_feature_value_pairs(filtered_events)
                analysis['cross_feature_values'][key] = combo_pairs

        # Transformation pattern analysis
        analysis['transformation_patterns'] = self._analyze_transformation_patterns(global_pairs)

        # Value-level statistics
        analysis['value_statistics'] = self._get_value_level_statistics(global_pairs)

        return analysis

    def _analyze_transformation_patterns(self, feature_value_pairs: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Analyze common transformation patterns across features."""
        patterns = {
            'most_common_transformations': {},
            'transformation_types': {
                'deletions': {},  # canonical→ABSENT
                'additions': {},  # ABSENT→headline
                'changes': {},    # canonical→headline (both present)
                'null_changes': {} # same→same
            },
            'bidirectional_changes': {}
        }

        for feature_id, pairs in feature_value_pairs.items():
            # Sort by frequency
            sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
            patterns['most_common_transformations'][feature_id] = sorted_pairs[:10]

            # Categorize transformation types
            for pair_key, count in pairs.items():
                canonical_val, headline_val = pair_key.split('→', 1)

                if headline_val == 'ABSENT':
                    patterns['transformation_types']['deletions'][pair_key] = count
                elif canonical_val == 'ABSENT':
                    patterns['transformation_types']['additions'][pair_key] = count
                elif canonical_val == headline_val:
                    patterns['transformation_types']['null_changes'][pair_key] = count
                else:
                    patterns['transformation_types']['changes'][pair_key] = count

        return patterns

    def _get_value_level_statistics(self, feature_value_pairs: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Get statistical summaries at the value level."""
        stats = {}

        for feature_id, pairs in feature_value_pairs.items():
            total_transformations = sum(pairs.values())
            unique_transformations = len(pairs)

            # Value diversity metrics
            canonical_values = set()
            headline_values = set()
            for pair_key in pairs.keys():
                canonical_val, headline_val = pair_key.split('→', 1)
                canonical_values.add(canonical_val)
                headline_values.add(headline_val)

            # Transformation concentration (top 3 pairs)
            sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
            top3_concentration = sum(count for _, count in sorted_pairs[:3]) / total_transformations if total_transformations > 0 else 0

            stats[feature_id] = {
                'total_transformations': total_transformations,
                'unique_transformation_types': unique_transformations,
                'canonical_value_diversity': len(canonical_values),
                'headline_value_diversity': len(headline_values),
                'top3_concentration_ratio': top3_concentration,
                'most_frequent_transformation': sorted_pairs[0] if sorted_pairs else None,
                'transformation_entropy': self._calculate_entropy(list(pairs.values())) if pairs else 0
            }

        return stats

    def _calculate_entropy(self, counts: List[int]) -> float:
        """Calculate Shannon entropy for transformation distribution."""
        import math
        total = sum(counts)
        if total == 0:
            return 0

        entropy = 0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return entropy

    def get_feature_value_pair_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive analysis treating feature-value pairs as single units.
        This analyzes feature-value combinations as atomic entities for deeper insights.
        """
        analysis = {
            'global_feature_value_pairs': {},
            'by_newspaper_feature_value_pairs': {},
            'by_parse_type_feature_value_pairs': {},
            'cross_feature_value_pairs': {},
            'pair_statistics': {},
            'pair_diversity_metrics': {},
            'transformation_pair_patterns': {}
        }

        # Global feature-value pair analysis
        global_pair_units = self._get_feature_value_pair_units(self.global_events)
        analysis['global_feature_value_pairs'] = global_pair_units

        # By newspaper feature-value pair analysis
        for newspaper in self.by_newspaper.keys():
            newspaper_pairs = self._get_feature_value_pair_units(self.by_newspaper[newspaper])
            analysis['by_newspaper_feature_value_pairs'][newspaper] = newspaper_pairs

        # By parse type feature-value pair analysis
        for parse_type in self.by_parse_type.keys():
            parse_type_pairs = self._get_feature_value_pair_units(self.by_parse_type[parse_type])
            analysis['by_parse_type_feature_value_pairs'][parse_type] = parse_type_pairs

        # Cross-dimensional analysis
        for newspaper in self.by_newspaper.keys():
            for parse_type in self.by_parse_type.keys():
                cross_key = f"{newspaper}_{parse_type}"
                cross_events = [e for e in self.global_events
                               if e.newspaper == newspaper and e.parse_type == parse_type]
                if cross_events:
                    cross_pairs = self._get_feature_value_pair_units(cross_events)
                    analysis['cross_feature_value_pairs'][cross_key] = cross_pairs

        # Calculate pair statistics
        analysis['pair_statistics'] = self._calculate_pair_statistics(analysis)

        # Calculate diversity metrics for pairs
        analysis['pair_diversity_metrics'] = self._calculate_pair_diversity_metrics(analysis)

        # Analyze transformation patterns at pair level
        analysis['transformation_pair_patterns'] = self._analyze_transformation_pair_patterns(analysis)

        return analysis

    def _get_feature_value_pair_units(self, events: List[DifferenceEvent]) -> Dict[str, int]:
        """
        Get feature-value pairs treated as single atomic units.
        Returns: {feature_canonical_value→headline_value: count}
        """
        pair_units = {}

        for event in events:
            # Create atomic feature-value pair identifier
            pair_key = f"{event.feature_id}:{event.canonical_value}→{event.headline_value}"
            pair_units[pair_key] = pair_units.get(pair_key, 0) + 1

        return pair_units

    def _calculate_pair_statistics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for feature-value pairs."""
        stats = {
            'total_unique_pairs': 0,
            'most_frequent_pairs': [],
            'pair_frequency_distribution': {},
            'average_pair_frequency': 0,
            'pair_concentration_metrics': {}
        }

        # Analyze global pairs
        global_pairs = analysis['global_feature_value_pairs']
        if global_pairs:
            stats['total_unique_pairs'] = len(global_pairs)

            # Most frequent pairs
            sorted_pairs = sorted(global_pairs.items(), key=lambda x: x[1], reverse=True)
            stats['most_frequent_pairs'] = sorted_pairs[:10]

            # Frequency distribution
            frequencies = list(global_pairs.values())
            stats['average_pair_frequency'] = sum(frequencies) / len(frequencies) if frequencies else 0

            # Concentration metrics (how concentrated are the pairs)
            total_occurrences = sum(frequencies)
            if total_occurrences > 0:
                # Calculate concentration metrics
                sorted_freqs = sorted(frequencies)
                stats['pair_concentration_metrics'] = {
                    'total_pair_occurrences': total_occurrences,
                    'entropy': self._calculate_entropy(frequencies),
                    'concentration_ratio': sum(sorted_freqs[-5:]) / total_occurrences if total_occurrences > 0 else 0
                }

        return stats

    def _calculate_pair_diversity_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate diversity metrics for feature-value pairs across dimensions."""
        diversity = {
            'newspaper_pair_diversity': {},
            'parse_type_pair_diversity': {},
            'cross_dimension_diversity': {}
        }

        # Newspaper diversity
        for newspaper, pairs in analysis['by_newspaper_feature_value_pairs'].items():
            diversity['newspaper_pair_diversity'][newspaper] = {
                'unique_pairs': len(pairs),
                'total_occurrences': sum(pairs.values()) if pairs else 0,
                'diversity_index': self._calculate_diversity_index(list(pairs.values())) if pairs else 0
            }

        # Parse type diversity
        for parse_type, pairs in analysis['by_parse_type_feature_value_pairs'].items():
            diversity['parse_type_pair_diversity'][parse_type] = {
                'unique_pairs': len(pairs),
                'total_occurrences': sum(pairs.values()) if pairs else 0,
                'diversity_index': self._calculate_diversity_index(list(pairs.values())) if pairs else 0
            }

        return diversity

    def _analyze_transformation_pair_patterns(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in transformation pairs."""
        patterns = {
            'feature_transformation_counts': {},
            'bidirectional_transformations': [],
            'transformation_complexity': {}
        }

        global_pairs = analysis['global_feature_value_pairs']

        # Analyze by feature
        transformation_types = {}
        for pair_key, count in global_pairs.items():
            if ':' in pair_key and '→' in pair_key:
                feature_part, transformation = pair_key.split(':', 1)
                canonical_val, headline_val = transformation.split('→', 1)

                # Count transformations per feature
                if feature_part not in patterns['feature_transformation_counts']:
                    patterns['feature_transformation_counts'][feature_part] = 0
                patterns['feature_transformation_counts'][feature_part] += count

                # Track transformation types
                if feature_part not in transformation_types:
                    transformation_types[feature_part] = set()
                transformation_types[feature_part].add(transformation)

        # Convert sets to counts for JSON serialization
        for feature in transformation_types:
            patterns['transformation_complexity'][feature] = len(transformation_types[feature])

        return patterns

    def _calculate_diversity_index(self, frequencies: List[int]) -> float:
        """Calculate Shannon diversity index for frequency distribution."""
        if not frequencies or sum(frequencies) == 0:
            return 0.0

        total = sum(frequencies)
        proportions = [f / total for f in frequencies if f > 0]

        import math
        diversity = -sum(p * math.log(p) for p in proportions)
        return diversity

    def get_bidirectional_cross_entropy_analysis(self) -> Dict[str, Any]:
        """
        Calculate bidirectional cross-entropy between canonical and headline registers.
        Provides information-theoretic measures of register differences.
        """
        analysis = {
            'global_cross_entropy': {},
            'by_newspaper_cross_entropy': {},
            'by_parse_type_cross_entropy': {},
            'cross_dimensional_cross_entropy': {},
            'cross_entropy_statistics': {},
            'feature_level_cross_entropy': {}
        }

        # Global bidirectional cross-entropy
        global_ce = self._calculate_bidirectional_cross_entropy(self.global_events)
        analysis['global_cross_entropy'] = global_ce

        # By newspaper cross-entropy
        for newspaper in self.by_newspaper.keys():
            newspaper_events = self.by_newspaper[newspaper]
            newspaper_ce = self._calculate_bidirectional_cross_entropy(newspaper_events)
            analysis['by_newspaper_cross_entropy'][newspaper] = newspaper_ce

        # By parse type cross-entropy
        for parse_type in self.by_parse_type.keys():
            parse_type_events = self.by_parse_type[parse_type]
            parse_type_ce = self._calculate_bidirectional_cross_entropy(parse_type_events)
            analysis['by_parse_type_cross_entropy'][parse_type] = parse_type_ce

        # Cross-dimensional analysis
        for newspaper in self.by_newspaper.keys():
            for parse_type in self.by_parse_type.keys():
                cross_key = f"{newspaper}_{parse_type}"
                cross_events = [e for e in self.global_events
                               if e.newspaper == newspaper and e.parse_type == parse_type]
                if cross_events:
                    cross_ce = self._calculate_bidirectional_cross_entropy(cross_events)
                    analysis['cross_dimensional_cross_entropy'][cross_key] = cross_ce

        # Feature-level cross-entropy analysis
        analysis['feature_level_cross_entropy'] = self._calculate_feature_level_cross_entropy()

        # Cross-entropy statistics and summaries
        analysis['cross_entropy_statistics'] = self._calculate_cross_entropy_statistics(analysis)

        return analysis

    def _calculate_bidirectional_cross_entropy(self, events: List[DifferenceEvent]) -> Dict[str, Any]:
        """
        Calculate bidirectional cross-entropy for a set of events.
        Returns cross-entropy in both directions and combined measures.
        """
        import math
        from collections import defaultdict

        # Separate events by feature for more granular analysis
        feature_events = defaultdict(list)
        for event in events:
            feature_events[event.feature_id].append(event)

        # Calculate distributions for canonical and headline registers
        canonical_dist = defaultdict(int)
        headline_dist = defaultdict(int)
        total_canonical = 0
        total_headline = 0

        # Count value occurrences in each register
        for event in events:
            canonical_dist[event.canonical_value] += 1
            headline_dist[event.headline_value] += 1
            total_canonical += 1
            total_headline += 1

        # Convert to probabilities
        canonical_probs = {val: count/total_canonical for val, count in canonical_dist.items()}
        headline_probs = {val: count/total_headline for val, count in headline_dist.items()}

        # Get all unique values
        all_values = set(canonical_dist.keys()) | set(headline_dist.keys())

        # Calculate cross-entropies
        # H(canonical, headline) = -sum(p_canonical(x) * log(p_headline(x)))
        canonical_to_headline_ce = 0
        headline_to_canonical_ce = 0

        for value in all_values:
            p_canonical = canonical_probs.get(value, 1e-10)  # Small epsilon for unseen values
            p_headline = headline_probs.get(value, 1e-10)

            # Cross-entropy: canonical → headline
            if p_canonical > 0 and p_headline > 0:
                canonical_to_headline_ce += -p_canonical * math.log2(p_headline)

            # Cross-entropy: headline → canonical
            if p_headline > 0 and p_canonical > 0:
                headline_to_canonical_ce += -p_headline * math.log2(p_canonical)

        # Calculate entropy of each register
        canonical_entropy = -sum(p * math.log2(p) for p in canonical_probs.values() if p > 0)
        headline_entropy = -sum(p * math.log2(p) for p in headline_probs.values() if p > 0)

        # Calculate KL divergences
        kl_canonical_to_headline = canonical_to_headline_ce - canonical_entropy
        kl_headline_to_canonical = headline_to_canonical_ce - headline_entropy

        # Combined measures
        bidirectional_sum = canonical_to_headline_ce + headline_to_canonical_ce
        kl_divergence_sum = kl_canonical_to_headline + kl_headline_to_canonical
        jensen_shannon_divergence = 0.5 * kl_canonical_to_headline + 0.5 * kl_headline_to_canonical

        return {
            'canonical_to_headline_cross_entropy': canonical_to_headline_ce,
            'headline_to_canonical_cross_entropy': headline_to_canonical_ce,
            'bidirectional_cross_entropy_sum': bidirectional_sum,
            'canonical_entropy': canonical_entropy,
            'headline_entropy': headline_entropy,
            'kl_canonical_to_headline': kl_canonical_to_headline,
            'kl_headline_to_canonical': kl_headline_to_canonical,
            'kl_divergence_sum': kl_divergence_sum,
            'jensen_shannon_divergence': jensen_shannon_divergence,
            'total_events': len(events),
            'unique_canonical_values': len(canonical_dist),
            'unique_headline_values': len(headline_dist),
            'unique_combined_values': len(all_values),
            'register_overlap_ratio': len(set(canonical_dist.keys()) & set(headline_dist.keys())) / len(all_values) if all_values else 0
        }

    def _calculate_feature_level_cross_entropy(self) -> Dict[str, Dict[str, Any]]:
        """Calculate cross-entropy analysis for each feature separately."""
        feature_analysis = {}

        # Group events by feature
        from collections import defaultdict
        feature_events = defaultdict(list)
        for event in self.global_events:
            feature_events[event.feature_id].append(event)

        # Calculate cross-entropy for each feature
        for feature_id, events in feature_events.items():
            if len(events) >= 2:  # Need minimum events for meaningful analysis
                feature_ce = self._calculate_bidirectional_cross_entropy(events)
                feature_analysis[feature_id] = feature_ce

        return feature_analysis

    def _calculate_cross_entropy_statistics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for cross-entropy analysis."""
        stats = {
            'newspaper_comparison': {},
            'parse_type_comparison': {},
            'feature_ranking': {},
            'overall_metrics': {}
        }

        # Newspaper comparison statistics
        newspaper_ces = analysis['by_newspaper_cross_entropy']
        if newspaper_ces:
            newspaper_stats = []
            for newspaper, ce_data in newspaper_ces.items():
                newspaper_stats.append({
                    'newspaper': newspaper,
                    'bidirectional_sum': ce_data['bidirectional_cross_entropy_sum'],
                    'canonical_to_headline': ce_data['canonical_to_headline_cross_entropy'],
                    'headline_to_canonical': ce_data['headline_to_canonical_cross_entropy'],
                    'jensen_shannon': ce_data['jensen_shannon_divergence'],
                    'register_overlap': ce_data['register_overlap_ratio']
                })

            # Sort by bidirectional sum (highest information loss first)
            newspaper_stats.sort(key=lambda x: x['bidirectional_sum'], reverse=True)
            stats['newspaper_comparison'] = {
                'ranked_newspapers': newspaper_stats,
                'most_divergent': newspaper_stats[0]['newspaper'] if newspaper_stats else None,
                'least_divergent': newspaper_stats[-1]['newspaper'] if newspaper_stats else None,
                'average_bidirectional_ce': sum(ns['bidirectional_sum'] for ns in newspaper_stats) / len(newspaper_stats) if newspaper_stats else 0
            }

        # Parse type comparison
        parse_type_ces = analysis['by_parse_type_cross_entropy']
        if parse_type_ces:
            parse_stats = []
            for parse_type, ce_data in parse_type_ces.items():
                parse_stats.append({
                    'parse_type': parse_type,
                    'bidirectional_sum': ce_data['bidirectional_cross_entropy_sum'],
                    'jensen_shannon': ce_data['jensen_shannon_divergence'],
                    'register_overlap': ce_data['register_overlap_ratio']
                })

            parse_stats.sort(key=lambda x: x['bidirectional_sum'], reverse=True)
            stats['parse_type_comparison'] = {
                'ranked_parse_types': parse_stats,
                'most_divergent_parse_type': parse_stats[0]['parse_type'] if parse_stats else None
            }

        # Feature-level ranking
        feature_ces = analysis['feature_level_cross_entropy']
        if feature_ces:
            feature_stats = []
            for feature_id, ce_data in feature_ces.items():
                feature_stats.append({
                    'feature_id': feature_id,
                    'bidirectional_sum': ce_data['bidirectional_cross_entropy_sum'],
                    'jensen_shannon': ce_data['jensen_shannon_divergence'],
                    'total_events': ce_data['total_events'],
                    'register_overlap': ce_data['register_overlap_ratio']
                })

            feature_stats.sort(key=lambda x: x['bidirectional_sum'], reverse=True)
            stats['feature_ranking'] = {
                'ranked_features': feature_stats[:10],  # Top 10 most divergent features
                'most_divergent_feature': feature_stats[0]['feature_id'] if feature_stats else None,
                'least_divergent_feature': feature_stats[-1]['feature_id'] if feature_stats else None
            }

        # Overall metrics
        global_ce = analysis['global_cross_entropy']
        if global_ce:
            stats['overall_metrics'] = {
                'global_bidirectional_sum': global_ce['bidirectional_cross_entropy_sum'],
                'global_jensen_shannon': global_ce['jensen_shannon_divergence'],
                'global_register_overlap': global_ce['register_overlap_ratio'],
                'information_asymmetry': abs(global_ce['canonical_to_headline_cross_entropy'] - global_ce['headline_to_canonical_cross_entropy']),
                'total_unique_values': global_ce['unique_combined_values']
            }

        return stats

    def get_statistical_summary(self) -> Dict[str, Any]:
        """Generate statistical summary for all dimensions."""
        analysis = self.get_comprehensive_analysis()

        summary = {
            'overview': {
                'total_events': analysis['global']['total_events'],
                'unique_features': len(analysis['global']['feature_counts']),
                'newspapers': list(analysis['by_newspaper'].keys()),
                'parse_types': list(analysis['by_parse_type'].keys())
            },
            'feature_statistics': {},
            'newspaper_statistics': {},
            'parse_type_statistics': {}
        }

        # Feature-level statistics
        for feature_id, count in analysis['global']['feature_counts'].items():
            summary['feature_statistics'][feature_id] = {
                'total_occurrences': count,
                'percentage_of_total': (count / analysis['global']['total_events']) * 100,
                'newspapers_found_in': len([n for n, data in analysis['by_newspaper'].items()
                                          if feature_id in data['feature_counts']]),
                'parse_types_found_in': len([p for p, data in analysis['by_parse_type'].items()
                                           if feature_id in data['feature_counts']])
            }

        # Newspaper-level statistics
        for newspaper, data in analysis['by_newspaper'].items():
            summary['newspaper_statistics'][newspaper] = {
                'total_events': data['total_events'],
                'percentage_of_global': (data['total_events'] / analysis['global']['total_events']) * 100,
                'unique_features': len(data['feature_counts']),
                'most_frequent_feature': max(data['feature_counts'].items(), key=lambda x: x[1]) if data['feature_counts'] else None
            }

        # Parse type statistics
        for parse_type, data in analysis['by_parse_type'].items():
            summary['parse_type_statistics'][parse_type] = {
                'total_events': data['total_events'],
                'percentage_of_global': (data['total_events'] / analysis['global']['total_events']) * 100,
                'unique_features': len(data['feature_counts']),
                'most_frequent_feature': max(data['feature_counts'].items(), key=lambda x: x[1]) if data['feature_counts'] else None
            }

        return summary


# # Usage:
#
# # from register_comparison.meta_data.schema import FeatureSchema
# # from register_comparison.comparators.comparator import Comparator
# # from aggregator import Aggregator
# # from register_comparison.extractors.extractor import FeatureExtractor
# # from register_comparison.aligners.aligner import Aligner
#
# from register_comparison.meta_data.schema import FeatureSchema
# from register_comparison.comparators.comparator import Comparator
# from aggregator import Aggregator
# from register_comparison.extractors.extractor import FeatureExtractor
# from register_comparison.aligners.aligner import Aligner
# from register_comparison.aligners.aligner import AlignedSentencePair
#
#
# # aligner = Aligner(
# #     texts_canonical=schema.canon_text_list,
# #     texts_headlines=head_text_list,
# #     deps_canonical=canon_dep_list,
# #     deps_headlines=head_dep_list,
# #     consts_canonical=canon_const_list,
# #     consts_headlines=head_const_list,
# #     newspaper_name="Times-of-India"
# # )
# #
# # pairs = aligner.align()
#
#
#
# # 1. Load schema
# schema = FeatureSchema("data/diff-ontology-ver-3.0.json")
# schema.load_schema()
#
# # 2. Prepare aligner and get pairs (example, one newspaper setup)
# aligner = Aligner(
#     texts_canonical=schema.canon_text_list,
#     texts_headlines=schema.head_text_list,
#     deps_canonical=schema.canon_dep_list,
#     deps_headlines=schema.head_dep_list,
#     consts_canonical=schema.canon_const_list,
#     consts_headlines=schema.head_const_list,
#     newspaper_name="Times-of-India"
# )
# pairs = aligner.align()
#
# # 3. Extract features
# extractor = FeatureExtractor(schema)
# comparator = Comparator(schema)
# aggregator = Aggregator()
#
# for pair in pairs:
#     features = extractor.extract_features(pair)
#     events = comparator.compare_pair(pair, features)
#     aggregator.add_events(events)
#
# # 4. Check counts
# print("Global counts:", aggregator.global_counts())
# print("Counts per newspaper:", aggregator.per_newspaper_counts())
#
# # 5. Convert to matrix for DataFrame/CSV
# matrix = aggregator.to_matrix(aggregator.global_events)
