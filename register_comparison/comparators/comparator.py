
# Version 1

from typing import List, Dict, Any
from register_comparison.aligners.aligner import AlignedSentencePair
from register_comparison.meta_data.schema import FeatureSchema

class DifferenceEvent:
    """
    Represents a single difference in feature-values between
    canonical and headline register for a sentence pair.
    """
    def __init__(self,
                 newspaper: str,
                 sent_id: int,
                 parse_type: str,          # "dep" or "const"
                 feature_id: str,
                 canonical_value: str,
                 headline_value: str,
                 feature_name: str,
                 feature_mnemonic: str,
                 canonical_context: str,
                 headline_context: str):
        self.newspaper = newspaper
        self.sent_id = sent_id
        self.parse_type = parse_type
        self.feature_id = feature_id
        self.canonical_value = canonical_value
        self.headline_value = headline_value
        self.feature_name = feature_name
        self.feature_mnemonic = feature_mnemonic
        self.canonical_context = canonical_context
        self.headline_context = headline_context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newspaper": self.newspaper,
            "sentence_id": self.sent_id,
            "parse_type": self.parse_type,
            "feature_id": self.feature_id,
            "feature_name": self.feature_name,
            "mnemonic": self.feature_mnemonic,
            "canonical_value": self.canonical_value,
            "headline_value": self.headline_value,
            "canonical_context": self.canonical_context,
            "headline_context": self.headline_context,
        }


class Comparator:
    """
    Compares extracted features for canonical vs. headline register
    and generates DifferenceEvent records.
    """
    def __init__(self, schema: FeatureSchema):
        self.schema = schema

    def compare_pair(self, aligned_pair: AlignedSentencePair,
                     extracted_features: Dict[str, Dict[str, str]]) -> List[DifferenceEvent]:
        events: List[DifferenceEvent] = []

        for parse_type in ["dep", "const"]:
            can_key = f"canonical_{parse_type}"
            head_key = f"headline_{parse_type}"

            canonical_feats = extracted_features.get(can_key, {})
            headline_feats = extracted_features.get(head_key, {})

            # Compare each feature present in canonical or headline
            all_feature_ids = set(canonical_feats) | set(headline_feats)

            for feat_id in all_feature_ids:
                can_val = canonical_feats.get(feat_id)
                head_val = headline_feats.get(feat_id)

                # Only record if values differ
                if can_val != head_val:
                    feat_obj = self.schema.get_feature_by_id(feat_id)
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type=parse_type,
                            feature_id=feat_id,
                            canonical_value=can_val,
                            headline_value=head_val,
                            feature_name=feat_obj.name if feat_obj else None,
                            feature_mnemonic=feat_obj.mnemonic if feat_obj else None,
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )
        return events

# Version 2

# from typing import List, Dict, Any
# from aligner import AlignedSentencePair
# from schema import FeatureSchema

class DifferenceEvent:
    """
    Represents a single difference in feature-values between
    canonical and headline register for a sentence pair.
    """
    def __init__(self,
                 newspaper: str,
                 sent_id: int,
                 parse_type: str,          # "dep" or "const"
                 feature_id: str,
                 canonical_value: str,
                 headline_value: str,
                 feature_name: str,
                 feature_mnemonic: str,
                 canonical_context: str,
                 headline_context: str):
        self.newspaper = newspaper
        self.sent_id = sent_id
        self.parse_type = parse_type
        self.feature_id = feature_id
        self.canonical_value = canonical_value
        self.headline_value = headline_value
        self.feature_name = feature_name
        self.feature_mnemonic = feature_mnemonic
        self.canonical_context = canonical_context
        self.headline_context = headline_context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newspaper": self.newspaper,
            "sentence_id": self.sent_id,
            "parse_type": self.parse_type,
            "feature_id": self.feature_id,
            "feature_name": self.feature_name,
            "mnemonic": self.feature_mnemonic,
            "canonical_value": self.canonical_value,
            "headline_value": self.headline_value,
            "canonical_context": self.canonical_context,
            "headline_context": self.headline_context,
        }


class Comparator:
    """
    Compares extracted features for canonical vs. headline register
    and generates DifferenceEvent records.
    """
    def __init__(self, schema: FeatureSchema):
        self.schema = schema

    def compare_pair(self, aligned_pair: AlignedSentencePair,
                     extracted_features: Dict[str, Dict[str, str]]) -> List[DifferenceEvent]:
        events: List[DifferenceEvent] = []

        for parse_type in ["dep", "const"]:
            can_key = f"canonical_{parse_type}"
            head_key = f"headline_{parse_type}"

            canonical_feats = extracted_features.get(can_key, {})
            headline_feats = extracted_features.get(head_key, {})

            # Compare each feature present in canonical or headline
            all_feature_ids = set(canonical_feats) | set(headline_feats)

            for feat_id in all_feature_ids:
                can_val = canonical_feats.get(feat_id)
                head_val = headline_feats.get(feat_id)

                # Only record if values differ
                if can_val != head_val:
                    feat_obj = self.schema.get_feature_by_id(feat_id)
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type=parse_type,
                            feature_id=feat_id,
                            canonical_value=can_val,
                            headline_value=head_val,
                            feature_name=feat_obj.name if feat_obj else None,
                            feature_mnemonic=feat_obj.mnemonic if feat_obj else None,
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )
        return events


