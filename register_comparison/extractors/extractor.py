
# Version 1

from typing import List, Dict, Any
from register_comparison.meta_data.schema import FeatureSchema, Feature, FeatureValue
from register_comparison.aligners.aligner import AlignedSentencePair

class FeatureExtractor:
    def __init__(self, schema: FeatureSchema):
        self.schema = schema

    def extract_from_dep(self, token_list) -> Dict[str, str]:
        """
        Extract feature values from a dependency parse (conllu.TokenList).
        Returns a dict mapping feature_id to observed value code.
        """
        feature_values = {}

        # Convert to list for easier processing
        tokens = list(token_list)

        # === LEXICAL FEATURES ===

        # Function Word Detection (FW-DEL/FW-ADD will be detected in comparison)
        function_words = {"DET": "ART", "AUX": "AUX", "ADP": "ADP",
                         "CCONJ": "CCONJ", "SCONJ": "SCONJ", "PRON": "PRON"}

        # Content Word Detection (C-DEL/C-ADD will be detected in comparison)
        content_words = {"NOUN": "NOUN", "VERB": "VERB", "ADJ": "ADJ", "ADV": "ADV"}

        # Count different POS types for analysis
        pos_counts = {}
        for token in tokens:
            upos = token["upos"]
            pos_counts[upos] = pos_counts.get(upos, 0) + 1

        # === MORPHOLOGICAL FEATURES ===

        # Morphological Feature Analysis
        tense_features = []
        number_features = []
        for token in tokens:
            feats = token.get("feats")
            if feats:
                if "Tense" in feats:
                    tense_features.append(feats["Tense"])
                if "Number" in feats:
                    number_features.append(feats["Number"])

        # === SYNTACTIC FEATURES ===

        # Dependency Relations
        dep_relations = [token["deprel"] for token in tokens]

        # Detect specific dependency patterns
        has_passive = any("pass" in deprel for deprel in dep_relations)
        if has_passive:
            feature_values["DEP-PASSIVE"] = "1"

        # Subject types
        nsubj_count = sum(1 for rel in dep_relations if rel == "nsubj")
        csubj_count = sum(1 for rel in dep_relations if rel == "csubj")

        # Object patterns
        obj_count = sum(1 for rel in dep_relations if rel == "obj")
        iobj_count = sum(1 for rel in dep_relations if rel == "iobj")

        # === STRUCTURAL FEATURES ===

        # Sentence length (LENGTH-CHG will be detected in comparison)
        sentence_length = len(tokens)
        feature_values["SENT-LEN"] = str(sentence_length)

        # Dependency depth (measure of syntactic complexity)
        max_depth = 0
        for token in tokens:
            depth = self._calculate_dep_depth(token, tokens)
            max_depth = max(max_depth, depth)
        feature_values["DEP-DEPTH"] = str(max_depth)

        # Root verb analysis
        root_tokens = [token for token in tokens if token["deprel"] == "root"]
        if root_tokens:
            root_token = root_tokens[0]
            feature_values["ROOT-POS"] = root_token["upos"]
            if root_token["upos"] == "VERB":
                feats = root_token.get("feats", {})
                if feats and "VerbForm" in feats:
                    feature_values["ROOT-VERBFORM"] = feats["VerbForm"]

        return feature_values

    def _calculate_dep_depth(self, token, all_tokens) -> int:
        """Calculate the depth of a token in the dependency tree."""
        if token["head"] == 0:  # Root
            return 0

        # Find parent token
        head_id = token["head"]
        parent_token = None
        for t in all_tokens:
            if t["id"] == head_id:
                parent_token = t
                break

        if parent_token is None:
            return 0

        return 1 + self._calculate_dep_depth(parent_token, all_tokens)

    def extract_from_const(self, tree) -> Dict[str, str]:
        """
        Extract feature values from a constituency parse (nltk.Tree).
        Returns a dict mapping feature_id to observed value code.
        """
        feature_values = {}

        # === CONSTITUENCY STRUCTURE ANALYSIS ===

        # Count different phrase types
        phrase_counts = {}
        all_labels = []

        def traverse_tree(subtree):
            """Recursively traverse the tree and collect phrase labels."""
            if hasattr(subtree, 'label'):
                label = subtree.label()
                all_labels.append(label)
                phrase_counts[label] = phrase_counts.get(label, 0) + 1

                # Recurse into children
                for child in subtree:
                    if hasattr(child, 'label'):  # It's a subtree
                        traverse_tree(child)

        traverse_tree(tree)

        # === PHRASE-LEVEL FEATURES ===

        # Noun phrases
        np_count = phrase_counts.get('NP', 0)
        feature_values["NP-COUNT"] = str(np_count)

        # Verb phrases
        vp_count = phrase_counts.get('VP', 0)
        feature_values["VP-COUNT"] = str(vp_count)

        # Prepositional phrases
        pp_count = phrase_counts.get('PP', 0)
        feature_values["PP-COUNT"] = str(pp_count)

        # Subordinate clauses
        sbar_count = phrase_counts.get('SBAR', 0)
        feature_values["SBAR-COUNT"] = str(sbar_count)

        # Adjective phrases
        adjp_count = phrase_counts.get('ADJP', 0)
        feature_values["ADJP-COUNT"] = str(adjp_count)

        # Adverb phrases
        advp_count = phrase_counts.get('ADVP', 0)
        feature_values["ADVP-COUNT"] = str(advp_count)

        # === STRUCTURAL COMPLEXITY ===

        # Tree depth (syntactic complexity)
        def get_tree_depth(subtree):
            if not hasattr(subtree, 'label'):
                return 0
            if not subtree:
                return 1
            max_child_depth = 0
            for child in subtree:
                if hasattr(child, 'label'):
                    child_depth = get_tree_depth(child)
                    max_child_depth = max(max_child_depth, child_depth)
            return 1 + max_child_depth

        tree_depth = get_tree_depth(tree)
        feature_values["TREE-DEPTH"] = str(tree_depth)

        # Number of constituents (structural complexity)
        total_constituents = len(all_labels)
        feature_values["CONST-COUNT"] = str(total_constituents)

        # === CLAUSE ANALYSIS ===

        # Clause types
        s_count = phrase_counts.get('S', 0)
        sq_count = phrase_counts.get('SQ', 0)  # Question
        sinv_count = phrase_counts.get('SINV', 0)  # Inverted declarative

        feature_values["S-COUNT"] = str(s_count)

        # Detect coordination
        cc_present = any(label in all_labels for label in ['CC'])
        if cc_present:
            feature_values["COORDINATION"] = "1"

        # === SPECIFIC CONSTRUCTIONS ===

        # Passive construction detection (VP -> VBN pattern)
        def has_passive_construction(subtree):
            if not hasattr(subtree, 'label'):
                return False

            if subtree.label() == 'VP':
                # Look for VBN (past participle) patterns
                children_labels = [child.label() if hasattr(child, 'label') else str(child)
                                 for child in subtree]
                if any('VBN' in label for label in children_labels):
                    return True

            # Recurse into children
            for child in subtree:
                if hasattr(child, 'label') and has_passive_construction(child):
                    return True
            return False

        if has_passive_construction(tree):
            feature_values["PASSIVE-CONST"] = "1"

        # Fronting detection (unusual word order)
        def detect_fronting(subtree):
            """Detect if non-subject elements appear before the main clause."""
            if not hasattr(subtree, 'label'):
                return False

            if subtree.label() == 'S':
                # Check if first child is not NP (subject)
                if subtree and hasattr(subtree[0], 'label'):
                    first_child_label = subtree[0].label()
                    if first_child_label in ['PP', 'ADVP', 'SBAR']:  # Non-subject fronting
                        return True

            # Recurse into children
            for child in subtree:
                if hasattr(child, 'label') and detect_fronting(child):
                    return True
            return False

        if detect_fronting(tree):
            feature_values["FRONTING"] = "1"

        return feature_values

    def extract_features(self, aligned_pair: AlignedSentencePair) -> Dict[str, Dict[str, str]]:
        """
        Extract feature sets for both registers in an aligned sentence pair.
        Returns dict:
            {
              "canonical_dep": {...feature_id: value_code...},
              "headline_dep": {...},
              "canonical_const": {...},
              "headline_const": {...}
            }
        """
        features = {
            "canonical_dep": self.extract_from_dep(aligned_pair.canonical_dep),
            "headline_dep": self.extract_from_dep(aligned_pair.headline_dep),
            "canonical_const": self.extract_from_const(aligned_pair.canonical_const),
            "headline_const": self.extract_from_const(aligned_pair.headline_const),
        }
        return features
