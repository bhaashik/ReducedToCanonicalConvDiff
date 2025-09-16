
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
