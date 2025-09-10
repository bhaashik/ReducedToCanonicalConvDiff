
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

from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.comparators.comparator import Comparator
from aggregator import Aggregator
from register_comparison.extractors.extractor import FeatureExtractor
from register_comparison.aligners.aligner import Aligner

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


# Usage:

# from register_comparison.meta_data.schema import FeatureSchema
# from register_comparison.comparators.comparator import Comparator
# from aggregator import Aggregator
# from register_comparison.extractors.extractor import FeatureExtractor
# from register_comparison.aligners.aligner import Aligner

from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.comparators.comparator import Comparator
from aggregator import Aggregator
from register_comparison.extractors.extractor import FeatureExtractor
from register_comparison.aligners.aligner import Aligner
from register_comparison.aligners.aligner import AlignedSentencePair


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



# 1. Load schema
schema = FeatureSchema("data/diff-ontology-ver-3.0.json")
schema.load_schema()

# 2. Prepare aligner and get pairs (example, one newspaper setup)
aligner = Aligner(
    texts_canonical=schema.canon_text_list,
    texts_headlines=schema.head_text_list,
    deps_canonical=schema.canon_dep_list,
    deps_headlines=schema.head_dep_list,
    consts_canonical=schema.canon_const_list,
    consts_headlines=schema.head_const_list,
    newspaper_name="Times-of-India"
)
pairs = aligner.align()

# 3. Extract features
extractor = FeatureExtractor(schema)
comparator = Comparator(schema)
aggregator = Aggregator()

for pair in pairs:
    features = extractor.extract_features(pair)
    events = comparator.compare_pair(pair, features)
    aggregator.add_events(events)

# 4. Check counts
print("Global counts:", aggregator.global_counts())
print("Counts per newspaper:", aggregator.per_newspaper_counts())

# 5. Convert to matrix for DataFrame/CSV
matrix = aggregator.to_matrix(aggregator.global_events)
