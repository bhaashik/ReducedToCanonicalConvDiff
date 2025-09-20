from typing import List, Dict, Any
from register_comparison.aligners.aligner import AlignedSentencePair
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.comparators.comparator import DifferenceEvent


class SchemaBasedComparator:
    """
    Compares aligned sentence pairs to detect schema-defined difference events.
    This replaces the old approach that used custom features.
    """

    def __init__(self, schema: FeatureSchema):
        self.schema = schema

    def compare_pair(self, aligned_pair: AlignedSentencePair,
                     extracted_features: Dict[str, Dict[str, str]] = None) -> List[DifferenceEvent]:
        """
        Compare aligned sentence pairs to detect ALL schema-defined difference events.
        """
        events = []

        # === LEXICAL FEATURES ===

        # Function Word Deletion/Addition (FW-DEL, FW-ADD)
        events.extend(self._detect_function_word_changes(aligned_pair))

        # Content Word Deletion/Addition (C-DEL, C-ADD)
        events.extend(self._detect_content_word_changes(aligned_pair))

        # POS Changes (POS-CHG)
        events.extend(self._detect_pos_changes(aligned_pair))

        # Lemma Changes (LEMMA-CHG)
        events.extend(self._detect_lemma_changes(aligned_pair))

        # Surface Form Changes (FORM-CHG)
        events.extend(self._detect_form_changes(aligned_pair))

        # === SYNTACTIC FEATURES ===

        # Dependency Relation Changes (DEP-REL-CHG)
        events.extend(self._detect_deprel_changes(aligned_pair))

        # Dependency Head Changes (HEAD-CHG)
        events.extend(self._detect_head_changes(aligned_pair))

        # === MORPHOLOGICAL FEATURES ===

        # Morphological Feature Changes (FEAT-CHG)
        events.extend(self._detect_morphological_changes(aligned_pair))

        # Verb Form Changes (VERB-FORM-CHG)
        events.extend(self._detect_verb_form_changes(aligned_pair))

        # === STRUCTURAL FEATURES ===

        # Sentence Length Change (LENGTH-CHG)
        events.extend(self._detect_length_changes(aligned_pair))

        # === CONSTITUENCY FEATURES ===

        # Constituent Removal/Addition (CONST-REM, CONST-ADD)
        events.extend(self._detect_constituent_changes(aligned_pair))

        # Constituent Movement (CONST-MOV)
        events.extend(self._detect_constituent_movement(aligned_pair))

        # === WORD-ORDER FEATURES ===

        # Token Reordering (TOKEN-REORDER)
        events.extend(self._detect_token_reordering(aligned_pair))

        # === CLAUSE-LEVEL FEATURES ===

        # Clause Type Changes (CLAUSE-TYPE-CHG)
        events.extend(self._detect_clause_type_changes(aligned_pair))

        # === STRUCTURAL FEATURES ===

        # Tree Edit Distance (TED)
        events.extend(self._detect_tree_edit_distance(aligned_pair))

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_function_word_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect function word deletion/addition between canonical and headline."""
        events = []

        # Get tokens from dependency parses
        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        # Function word POS tags
        function_pos = {'DET', 'AUX', 'ADP', 'CCONJ', 'SCONJ', 'PRON'}

        # Simple alignment: match by word form and position
        canonical_fw = [(i, token) for i, token in enumerate(canonical_tokens)
                       if token.get('upos') in function_pos]
        headline_fw = [(i, token) for i, token in enumerate(headline_tokens)
                      if token.get('upos') in function_pos]

        # Detect deletions (in canonical but not in headline)
        canonical_words = {token.get('form').lower() for _, token in canonical_fw}
        headline_words = {token.get('form').lower() for _, token in headline_fw}

        # Function word deletions
        deleted_words = canonical_words - headline_words
        for word in deleted_words:
            # Find the token details
            token_info = next((token for _, token in canonical_fw
                             if token.get('form').lower() == word), None)
            if token_info:
                pos = token_info.get('upos')
                value_mnemonic = self._get_fw_deletion_mnemonic(pos)
                if value_mnemonic:
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="dependency",
                            feature_id="FW-DEL",
                            canonical_value=value_mnemonic,
                            headline_value="ABSENT",
                            feature_name="Function Word Deletion",
                            feature_mnemonic="FW-DEL",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )

        # Function word additions
        added_words = headline_words - canonical_words
        for word in added_words:
            token_info = next((token for _, token in headline_fw
                             if token.get('form').lower() == word), None)
            if token_info:
                pos = token_info.get('upos')
                value_mnemonic = self._get_fw_addition_mnemonic(pos)
                if value_mnemonic:
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="dependency",
                            feature_id="FW-ADD",
                            canonical_value="ABSENT",
                            headline_value=value_mnemonic,
                            feature_name="Function Word Addition",
                            feature_mnemonic="FW-ADD",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_content_word_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect content word deletion/addition between canonical and headline."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        # Content word POS tags
        content_pos = {'NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN'}

        # Get content words
        canonical_cw = [(i, token) for i, token in enumerate(canonical_tokens)
                       if token.get('upos') in content_pos]
        headline_cw = [(i, token) for i, token in enumerate(headline_tokens)
                      if token.get('upos') in content_pos]

        # Simple word-based comparison
        canonical_words = {token.get('lemma', token.get('form')).lower()
                          for _, token in canonical_cw}
        headline_words = {token.get('lemma', token.get('form')).lower()
                         for _, token in headline_cw}

        # Content word deletions
        deleted_words = canonical_words - headline_words
        for word in deleted_words:
            token_info = next((token for _, token in canonical_cw
                             if token.get('lemma', token.get('form')).lower() == word), None)
            if token_info:
                pos = token_info.get('upos')
                value_mnemonic = self._get_content_deletion_mnemonic(pos)
                if value_mnemonic:
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="dependency",
                            feature_id="C-DEL",
                            canonical_value=value_mnemonic,
                            headline_value="ABSENT",
                            feature_name="Content Word Deletion",
                            feature_mnemonic="C-DEL",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )

        # Content word additions
        added_words = headline_words - canonical_words
        for word in added_words:
            token_info = next((token for _, token in headline_cw
                             if token.get('lemma', token.get('form')).lower() == word), None)
            if token_info:
                pos = token_info.get('upos')
                value_mnemonic = self._get_content_addition_mnemonic(pos)
                if value_mnemonic:
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="dependency",
                            feature_id="C-ADD",
                            canonical_value="ABSENT",
                            headline_value=value_mnemonic,
                            feature_name="Content Word Addition",
                            feature_mnemonic="C-ADD",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_pos_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect part-of-speech changes in aligned tokens."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        # Create lemma-based alignment for better matching
        canonical_lemmas = {}
        headline_lemmas = {}

        # Index tokens by lemma for better alignment
        for token in canonical_tokens:
            lemma = token.get('lemma', token.get('form', '')).lower()
            if lemma not in canonical_lemmas:
                canonical_lemmas[lemma] = []
            canonical_lemmas[lemma].append(token)

        for token in headline_tokens:
            lemma = token.get('lemma', token.get('form', '')).lower()
            if lemma not in headline_lemmas:
                headline_lemmas[lemma] = []
            headline_lemmas[lemma].append(token)

        # Find POS changes by comparing tokens with same lemmas
        for lemma, can_tokens in canonical_lemmas.items():
            if lemma in headline_lemmas:
                head_tokens = headline_lemmas[lemma]

                # Compare POS tags for tokens with same lemma
                for can_token in can_tokens:
                    for head_token in head_tokens:
                        can_pos = can_token.get('upos')
                        head_pos = head_token.get('upos')

                        if can_pos != head_pos and can_pos and head_pos:
                            value_mnemonic = self._get_pos_change_mnemonic(can_pos, head_pos)
                            if value_mnemonic:
                                events.append(
                                    DifferenceEvent(
                                        newspaper=aligned_pair.newspaper,
                                        sent_id=aligned_pair.sent_id,
                                        parse_type="dependency",
                                        feature_id="POS-CHG",
                                        canonical_value=can_pos,
                                        headline_value=head_pos,
                                        feature_name="Part of Speech Change",
                                        feature_mnemonic="POS-CHG",
                                        canonical_context=aligned_pair.canonical_text,
                                        headline_context=aligned_pair.headline_text
                                    )
                                )
                                break  # Avoid duplicate events for same lemma

        # Also check positional alignment for cases where lemma matching fails
        min_len = min(len(canonical_tokens), len(headline_tokens))
        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            can_pos = can_token.get('upos')
            head_pos = head_token.get('upos')
            can_form = can_token.get('form', '').lower()
            head_form = head_token.get('form', '').lower()
            can_lemma = can_token.get('lemma', '').lower()
            head_lemma = head_token.get('lemma', '').lower()

            # Detect POS changes for similar words (relaxed conditions)
            is_similar = (can_form == head_form or
                         can_lemma == head_lemma or
                         (len(can_form) > 3 and len(head_form) > 3 and
                          (can_form.startswith(head_form[:3]) or head_form.startswith(can_form[:3]))))

            if (can_pos != head_pos and can_pos and head_pos and is_similar):
                # Check if we haven't already recorded this change via lemma matching
                lemma_key = can_lemma or can_form
                if lemma_key not in canonical_lemmas or lemma_key not in headline_lemmas:
                    value_mnemonic = self._get_pos_change_mnemonic(can_pos, head_pos)
                    if value_mnemonic:
                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="dependency",
                                feature_id="POS-CHG",
                                canonical_value=can_pos,
                                headline_value=head_pos,
                                feature_name="Part of Speech Change",
                                feature_mnemonic="POS-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_lemma_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect lemma changes in aligned tokens."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        min_len = min(len(canonical_tokens), len(headline_tokens))

        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            can_lemma = can_token.get('lemma', can_token.get('form'))
            head_lemma = head_token.get('lemma', head_token.get('form'))

            if (can_lemma != head_lemma and
                can_token.get('form', '').lower() == head_token.get('form', '').lower()):

                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="dependency",
                        feature_id="LEMMA-CHG",
                        canonical_value=can_lemma,
                        headline_value=head_lemma,
                        feature_name="Lemma Change",
                        feature_mnemonic="LEMMA-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_form_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect surface form changes."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        min_len = min(len(canonical_tokens), len(headline_tokens))

        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            can_form = can_token.get('form', '')
            head_form = head_token.get('form', '')

            # Same lemma, different form
            if (can_form != head_form and
                can_token.get('lemma', can_form) == head_token.get('lemma', head_form)):

                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="dependency",
                        feature_id="FORM-CHG",
                        canonical_value=can_form,
                        headline_value=head_form,
                        feature_name="Surface Form Change",
                        feature_mnemonic="FORM-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_deprel_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect dependency relation changes."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        min_len = min(len(canonical_tokens), len(headline_tokens))

        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            can_deprel = can_token.get('deprel')
            head_deprel = head_token.get('deprel')

            if can_deprel != head_deprel:
                value_mnemonic = self._get_deprel_change_mnemonic(can_deprel, head_deprel)
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="dependency",
                        feature_id="DEP-REL-CHG",
                        canonical_value=can_deprel,
                        headline_value=head_deprel,
                        feature_name="Dependency Relation Change",
                        feature_mnemonic="DEP-REL-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_length_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect sentence length changes."""
        events = []

        canonical_len = len(list(aligned_pair.canonical_dep))
        headline_len = len(list(aligned_pair.headline_dep))

        if canonical_len != headline_len:
            events.append(
                DifferenceEvent(
                    newspaper=aligned_pair.newspaper,
                    sent_id=aligned_pair.sent_id,
                    parse_type="dependency",
                    feature_id="LENGTH-CHG",
                    canonical_value=str(canonical_len),
                    headline_value=str(headline_len),
                    feature_name="Sentence Length Change",
                    feature_mnemonic="LENGTH-CHG",
                    canonical_context=aligned_pair.canonical_text,
                    headline_context=aligned_pair.headline_text
                )
            )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    # Helper methods for mnemonic mapping

    def _get_fw_deletion_mnemonic(self, pos: str) -> str:
        """Map POS to function word deletion mnemonic."""
        mapping = {
            'DET': 'ART-DEL',
            'AUX': 'AUX-DEL',
            'ADP': 'ADP-DEL',
            'CCONJ': 'CCONJ-DEL',
            'SCONJ': 'SCONJ-DEL',
            'PRON': 'PRON-PERS-DEL'  # Default to personal pronoun
        }
        return mapping.get(pos)

    def _get_fw_addition_mnemonic(self, pos: str) -> str:
        """Map POS to function word addition mnemonic."""
        mapping = {
            'DET': 'ART-ADD',
            'AUX': 'AUX-ADD',
            'ADP': 'ADP-ADD',
            'CCONJ': 'CCONJ-ADD',
            'SCONJ': 'SCONJ-ADD',
            'PRON': 'PRON-PERS-ADD'
        }
        return mapping.get(pos)

    def _get_content_deletion_mnemonic(self, pos: str) -> str:
        """Map POS to content word deletion mnemonic."""
        mapping = {
            'NOUN': 'NOUN-DEL',
            'PROPN': 'NOUN-DEL',
            'VERB': 'VERB-DEL',
            'ADJ': 'ADJ-DEL',
            'ADV': 'ADV-DEL'
        }
        return mapping.get(pos)

    def _get_content_addition_mnemonic(self, pos: str) -> str:
        """Map POS to content word addition mnemonic."""
        mapping = {
            'NOUN': 'NOUN-ADD',
            'PROPN': 'NOUN-ADD',
            'VERB': 'VERB-ADD',
            'ADJ': 'ADJ-ADD',
            'ADV': 'ADV-ADD'
        }
        return mapping.get(pos)

    def _get_pos_change_mnemonic(self, from_pos: str, to_pos: str) -> str:
        """Map POS changes to mnemonics."""
        change_mapping = {
            ('NOUN', 'VERB'): 'N2V',
            ('VERB', 'NOUN'): 'V2N',
            ('ADJ', 'NOUN'): 'ADJ2N',
            ('NOUN', 'ADJ'): 'N2ADJ',
            ('VERB', 'ADJ'): 'V2ADJ',
            ('ADJ', 'VERB'): 'ADJ2V'
        }
        return change_mapping.get((from_pos, to_pos))

    def _get_deprel_change_mnemonic(self, from_rel: str, to_rel: str) -> str:
        """Map dependency relation changes to mnemonics."""
        change_mapping = {
            ('nsubj', 'obl'): 'NSUBJ2OBL',
            ('obl', 'advmod'): 'OBL2ADVMOD',
            ('advmod', 'obl'): 'ADVMOD2OBL',
            ('obj', 'nsubj'): 'OBJ2NSUBJ',
            ('nsubj', 'obj'): 'NSUBJ2OBJ'
        }
        return change_mapping.get((from_rel, to_rel), 'DEP-MISC')

    def _detect_head_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect dependency head changes (HEAD-CHG)."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        # Simple alignment by position and form similarity
        min_len = min(len(canonical_tokens), len(headline_tokens))

        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            # Check if same word but different head
            if (can_token.get('form', '').lower() == head_token.get('form', '').lower() and
                can_token.get('deprel') == head_token.get('deprel')):  # Same relation

                can_head = can_token.get('head', 0)
                head_head = head_token.get('head', 0)

                if can_head != head_head:
                    # Determine if lexical or syntactic head change
                    value_mnemonic = "HEAD-SYN-CHG"  # Default to syntactic
                    if can_head > 0 and head_head > 0:
                        # Try to get head words to determine if lexical change
                        can_head_word = self._get_head_word(can_head, canonical_tokens)
                        head_head_word = self._get_head_word(head_head, headline_tokens)
                        if can_head_word and head_head_word and can_head_word != head_head_word:
                            value_mnemonic = "HEAD-LEX-CHG"

                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="dependency",
                            feature_id="HEAD-CHG",
                            canonical_value=str(can_head),
                            headline_value=str(head_head),
                            feature_name="Dependency Head Change",
                            feature_mnemonic="HEAD-CHG",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_morphological_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect morphological feature changes (FEAT-CHG)."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        min_len = min(len(canonical_tokens), len(headline_tokens))

        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            # Same lemma but different morphological features
            if (can_token.get('lemma', '').lower() == head_token.get('lemma', '').lower()):
                can_feats = can_token.get('feats') or {}
                head_feats = head_token.get('feats') or {}

                # Check specific morphological features
                morph_features = ['Tense', 'Number', 'Person', 'Voice', 'Mood', 'Aspect', 'Case']

                for feat in morph_features:
                    can_val = can_feats.get(feat) if isinstance(can_feats, dict) else None
                    head_val = head_feats.get(feat) if isinstance(head_feats, dict) else None

                    if can_val != head_val and (can_val or head_val):
                        value_mnemonic = self._get_morphological_change_mnemonic(feat, can_val, head_val)
                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="dependency",
                                feature_id="FEAT-CHG",
                                canonical_value=f"{feat}={can_val}",
                                headline_value=f"{feat}={head_val}",
                                feature_name="Morphological Feature Change",
                                feature_mnemonic="FEAT-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_verb_form_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect verb form changes (VERB-FORM-CHG)."""
        events = []

        canonical_tokens = list(aligned_pair.canonical_dep)
        headline_tokens = list(aligned_pair.headline_dep)

        min_len = min(len(canonical_tokens), len(headline_tokens))

        for i in range(min_len):
            can_token = canonical_tokens[i]
            head_token = headline_tokens[i]

            # Both must be verbs with same lemma
            if (can_token.get('upos') in ['VERB', 'AUX'] and
                head_token.get('upos') in ['VERB', 'AUX'] and
                can_token.get('lemma', '').lower() == head_token.get('lemma', '').lower()):

                can_feats = can_token.get('feats') or {}
                head_feats = head_token.get('feats') or {}

                can_verbform = can_feats.get('VerbForm') if isinstance(can_feats, dict) else None
                head_verbform = head_feats.get('VerbForm') if isinstance(head_feats, dict) else None

                if can_verbform != head_verbform and (can_verbform or head_verbform):
                    value_mnemonic = self._get_verb_form_change_mnemonic(can_verbform, head_verbform)
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="dependency",
                            feature_id="VERB-FORM-CHG",
                            canonical_value=can_verbform or "None",
                            headline_value=head_verbform or "None",
                            feature_name="Verb Form Change",
                            feature_mnemonic="VERB-FORM-CHG",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_constituent_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect constituent removal/addition (CONST-REM, CONST-ADD)."""
        events = []

        # Get phrase labels from constituency trees
        canonical_phrases = self._extract_phrase_labels(aligned_pair.canonical_const)
        headline_phrases = self._extract_phrase_labels(aligned_pair.headline_const)

        # Constituent removals (in canonical but not headlines)
        removed_phrases = canonical_phrases - headline_phrases
        for phrase in removed_phrases:
            value_mnemonic = self._get_constituent_removal_mnemonic(phrase)
            if value_mnemonic:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CONST-REM",
                        canonical_value=value_mnemonic,
                        headline_value="ABSENT",
                        feature_name="Constituent Removal",
                        feature_mnemonic="CONST-REM",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        # Constituent additions (in headlines but not canonical)
        added_phrases = headline_phrases - canonical_phrases
        for phrase in added_phrases:
            value_mnemonic = self._get_constituent_addition_mnemonic(phrase)
            if value_mnemonic:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CONST-ADD",
                        canonical_value="ABSENT",
                        headline_value=value_mnemonic,
                        feature_name="Constituent Addition",
                        feature_mnemonic="CONST-ADD",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_constituent_movement(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect constituent movement (CONST-MOV) - Movement of entire constituents to new positions."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Get constituent spans for both trees
            canonical_spans = self._get_constituent_spans(aligned_pair.canonical_const)
            headlines_spans = self._get_constituent_spans(aligned_pair.headline_const)

            # Find matching constituents that have moved
            for canon_span in canonical_spans:
                for head_span in headlines_spans:
                    if (canon_span['label'] == head_span['label'] and
                        canon_span['words'] == head_span['words'] and
                        canon_span['span'] != head_span['span']):

                        # Determine movement type
                        canon_start = canon_span['span'][0]
                        head_start = head_span['span'][0]

                        if head_start < canon_start:
                            movement_type = "fronted constituent"
                            mnemonic = "CONST-FRONT"
                        else:
                            movement_type = "postposed constituent"
                            mnemonic = "CONST-POST"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CONST-MOV",
                                canonical_value=mnemonic,
                                headline_value=mnemonic,
                                feature_name="Constituent Movement",
                                feature_mnemonic="CONST-MOV",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

        except Exception as e:
            print(f"Error detecting constituent movement: {e}")

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

        try:
            # Get constituent spans for both trees
            canonical_spans = self._get_constituent_spans(aligned_pair.canonical_const)
            headlines_spans = self._get_constituent_spans(aligned_pair.headline_const)

            # Find matching constituents that have moved
            for canon_span in canonical_spans:
                for head_span in headlines_spans:
                    if (canon_span['label'] == head_span['label'] and
                        canon_span['words'] == head_span['words'] and
                        canon_span['span'] != head_span['span']):

                        # Determine movement type
                        canon_start = canon_span['span'][0]
                        head_start = head_span['span'][0]

                        if head_start < canon_start:
                            movement_type = "fronted constituent"
                            mnemonic = "CONST-FRONT"
                        else:
                            movement_type = "postposed constituent"
                            mnemonic = "CONST-POST"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CONST-MOV",
                                canonical_value=mnemonic,
                                headline_value=mnemonic,
                                feature_name="Constituent Movement",
                                feature_mnemonic="CONST-MOV",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

        except Exception as e:
            print(f"Error detecting constituent movement: {e}")

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

    def _detect_token_reordering(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect token reordering (TOKEN-REORDER) - Changes in linear order of individual tokens."""
        events = []

        # Simple heuristic: check if word orders are different by comparing token sequences
        try:
            canonical_tokens = list(aligned_pair.canonical_dep)
            headline_tokens = list(aligned_pair.headline_dep)

            canonical_forms = [token.get('form', token.get('text', '')) for token in canonical_tokens]
            headline_forms = [token.get('form', token.get('text', '')) for token in headline_tokens]

            # Simple check: if sequences are different lengths or different order
            if len(canonical_forms) != len(headline_forms):
                return events  # Handle through deletion/addition features

            # Check for reorderings (simplified heuristic)
            different_positions = 0
            for i, (c_form, h_form) in enumerate(zip(canonical_forms, headline_forms)):
                if c_form != h_form:
                    # Look for this canonical form in the headline sequence
                    if c_form in headline_forms:
                        h_pos = headline_forms.index(c_form)
                        if h_pos != i:  # Position changed
                            different_positions += 1

                            # Determine movement type based on position change
                            if h_pos < i:
                                movement_type = "fronting"
                                mnemonic = "FRONT"
                            else:
                                movement_type = "postposing"
                                mnemonic = "POST"

                            events.append(
                                DifferenceEvent(
                                    newspaper=aligned_pair.newspaper,
                                    sent_id=aligned_pair.sent_id,
                                    parse_type="dependency",
                                    feature_id="TOKEN-REORDER",
                                    canonical_value=mnemonic,
                                    headline_value=mnemonic,
                                    feature_name="Token Reordering",
                                    feature_mnemonic="TOKEN-REORDER",
                                    canonical_context=aligned_pair.canonical_text,
                                    headline_context=aligned_pair.headline_text
                                )
                            )
                            break  # Only count one reordering per sentence pair

        except Exception as e:
            print(f"Error detecting token reordering: {e}")

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events

        try:
            # Get position mappings for aligned tokens
            position_changes = []

            for alignment in aligned_pair.alignments:
                if alignment.canonical_token and alignment.headlines_token:
                    canon_pos = alignment.canonical_token.get('id', 0)
                    headlines_pos = alignment.headlines_token.get('id', 0)

                    # Convert to 0-based indexing if needed
                    if isinstance(canon_pos, str) and canon_pos.isdigit():
                        canon_pos = int(canon_pos) - 1
                    if isinstance(headlines_pos, str) and headlines_pos.isdigit():
                        headlines_pos = int(headlines_pos) - 1

                    if canon_pos != headlines_pos:
                        position_changes.append({
                            'token': alignment.canonical_token,
                            'old_pos': canon_pos,
                            'new_pos': headlines_pos
                        })

            # Classify movement types
            for change in position_changes:
                token = change['token']
                old_pos = change['old_pos']
                new_pos = change['new_pos']

                # Determine movement type
                distance = abs(new_pos - old_pos)
                if new_pos < old_pos:
                    if distance > 3:
                        movement_type = "long-distance move"
                        mnemonic = "LD-MOVE"
                    elif old_pos == 0 or new_pos == 0:
                        movement_type = "fronting"
                        mnemonic = "FRONT"
                    else:
                        movement_type = "local swap"
                        mnemonic = "LSWAP"
                else:
                    if distance > 3:
                        movement_type = "long-distance move"
                        mnemonic = "LD-MOVE"
                    else:
                        movement_type = "postposing"
                        mnemonic = "POST"

                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="dependency",
                        feature_id="TOKEN-REORDER",
                        canonical_value=mnemonic,
                        headline_value=mnemonic,
                        feature_name="Token Reordering",
                        feature_mnemonic="TOKEN-REORDER",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting token reordering: {e}")

        return events

    def _detect_clause_type_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect clause type changes (CLAUSE-TYPE-CHG) - Changes in clause type or finiteness."""
        events = []

        if not aligned_pair.canonical_dep or not aligned_pair.headline_dep:
            return events

        try:
            # Check for finiteness changes in main verbs
            canonical_verbs = [token for token in aligned_pair.canonical_dep
                              if token.get('upos') in ['VERB', 'AUX']]
            headline_verbs = [token for token in aligned_pair.headline_dep
                             if token.get('upos') in ['VERB', 'AUX']]

            # Check for finite to nonfinite verb changes
            for c_verb in canonical_verbs:
                c_feats = c_verb.get('feats', {}) or {}
                c_verbform = c_feats.get('VerbForm', '')

                for h_verb in headline_verbs:
                    h_feats = h_verb.get('feats', {}) or {}
                    h_verbform = h_feats.get('VerbForm', '')

                    # Check for finite to nonfinite change
                    if (c_verbform == 'Fin' and h_verbform in ['Inf', 'Part', 'Ger']) or \
                       (c_verbform in ['Inf', 'Part', 'Ger'] and h_verbform == 'Fin'):

                        clause_type = "finite to nonfinite" if c_verbform == 'Fin' else "nonfinite to finite"
                        mnemonic = "FIN2NFIN" if c_verbform == 'Fin' else "NFIN2FIN"

                        events.append(
                            DifferenceEvent(
                                newspaper=aligned_pair.newspaper,
                                sent_id=aligned_pair.sent_id,
                                parse_type="constituency",
                                feature_id="CLAUSE-TYPE-CHG",
                                canonical_value=c_verbform,
                                headline_value=h_verbform,
                                feature_name="Clause Type Change",
                                feature_mnemonic="CLAUSE-TYPE-CHG",
                                canonical_context=aligned_pair.canonical_text,
                                headline_context=aligned_pair.headline_text
                            )
                        )

            # Check for verbless clauses (headline has no main verb)
            if canonical_verbs and not headline_verbs:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="CLAUSE-TYPE-CHG",
                        canonical_value="verbal",
                        headline_value="verbless",
                        feature_name="Clause Type Change",
                        feature_mnemonic="CLAUSE-TYPE-CHG",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error detecting clause type changes: {e}")

        return events

    def _detect_tree_edit_distance(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree edit distance (TED) - Calculate structural difference between constituency trees."""
        events = []

        if (aligned_pair.canonical_const is None or
            aligned_pair.headline_const is None):
            return events

        try:
            # Simple tree edit distance calculation
            ted_score = self._calculate_tree_edit_distance(
                aligned_pair.canonical_const,
                aligned_pair.headline_const
            )

            if ted_score > 0:
                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="constituency",
                        feature_id="TED",
                        canonical_value=str(ted_score),
                        headline_value=str(ted_score),
                        feature_name="Tree Edit Distance",
                        feature_mnemonic="TED",
                        canonical_context=aligned_pair.canonical_text,
                        headline_context=aligned_pair.headline_text
                    )
                )

        except Exception as e:
            print(f"Error calculating tree edit distance: {e}")

        return events    # Helper methods for the new feature implementations
    def _get_constituent_spans(self, tree):
        """Get spans for all constituents in a tree."""
        spans = []

        def extract_spans(node, start_pos=0):
            if isinstance(node, str):
                return start_pos + 1, [node]

            node_start = start_pos
            node_words = []

            for child in node:
                end_pos, child_words = extract_spans(child, start_pos)
                node_words.extend(child_words)
                start_pos = end_pos

            spans.append({
                'label': node.label() if hasattr(node, 'label') else str(node),
                'span': (node_start, start_pos),
                'words': node_words
            })

            return start_pos, node_words

        if tree:
            extract_spans(tree)
        return spans

    def _calculate_tree_edit_distance(self, tree1, tree2):
        """Calculate simple tree edit distance between two constituency trees."""
        if tree1 is None or tree2 is None:
            return 1 if tree1 != tree2 else 0

        # Simple implementation - count structural differences
        tree1_str = str(tree1) if tree1 else ""
        tree2_str = str(tree2) if tree2 else ""

        # Calculate Levenshtein distance on string representations
        # This is a simplified approach
        if len(tree1_str) == 0:
            return len(tree2_str)
        if len(tree2_str) == 0:
            return len(tree1_str)

        # Simple character-based distance (can be improved)
        differences = sum(c1 != c2 for c1, c2 in zip(tree1_str, tree2_str))
        differences += abs(len(tree1_str) - len(tree2_str))

        return min(differences // 10, 10)  # Normalize to reasonable range

    def _extract_phrase_labels(self, const_tree):
        """Extract phrase labels from constituency tree."""
        if const_tree is None:
            return set()

        labels = set()

        def collect_labels(node):
            # Avoid infinite recursion on strings
            if isinstance(node, str):
                return

            if hasattr(node, 'label'):
                labels.add(node.label())

            # Only recurse on non-string children
            if hasattr(node, '__iter__'):
                for child in node:
                    if not isinstance(child, str):
                        collect_labels(child)

        collect_labels(const_tree)
        return labels

    def _get_constituent_removal_mnemonic(self, phrase_label):
        """Get mnemonic for constituent removal based on phrase label."""
        removal_map = {
            'NP': 'NP-REM',
            'PP': 'PP-REM',
            'SBAR': 'SBAR-REM',
            'ADJP': 'ADJP-REM',
            'VP': 'VP-REM',
            'CP': 'CP-REM',
            'QP': 'QP-REM',
            'AdvP': 'ADVP-REM',
            'ADVP': 'ADVP-REM'
        }
        return removal_map.get(phrase_label)

    def _get_constituent_addition_mnemonic(self, phrase_label):
        """Get mnemonic for constituent addition based on phrase label."""
        addition_map = {
            'NP': 'NP-ADD',
            'PP': 'PP-ADD',
            'SBAR': 'SBAR-ADD',
            'ADJP': 'ADJP-ADD',
            'VP': 'VP-ADD',
            'CP': 'CP-ADD',
            'QP': 'QP-ADD',
            'AdvP': 'ADVP-ADD',
            'ADVP': 'ADVP-ADD'
        }
        return addition_map.get(phrase_label)

    def _get_head_word(self, head_id, tokens):
        """Get the word form of the head token by ID."""
        for token in tokens:
            if str(token.get('id', '')) == str(head_id):
                return token.get('form', token.get('text', ''))
        return f"ID:{head_id}"

    def _get_morphological_change_mnemonic(self, feature_name, source_val, target_val):
        """Get mnemonic for morphological feature changes."""
        feature_mnemonics = {
            'Tense': 'TENSE-CHG',
            'Number': 'NUM-CHG',
            'Aspect': 'ASP-CHG',
            'Voice': 'VOICE-CHG',
            'Mood': 'MOOD-CHG',
            'Case': 'CASE-CHG',
            'Degree': 'DEG-CHG'
        }
        return feature_mnemonics.get(feature_name, 'FEAT-CHG')

    def _get_verb_form_change_mnemonic(self, source_form, target_form):
        """Get mnemonic for verb form changes."""
        if source_form == 'Fin' and target_form in ['Part', 'Ger']:
            return 'VFIN2PART'
        elif source_form == 'Fin' and target_form == 'Inf':
            return 'VFIN2INF'
        elif source_form in ['Part', 'Ger'] and target_form == 'Fin':
            return 'PART2VFIN'
        else:
            return 'VERB-FORM-CHG'

