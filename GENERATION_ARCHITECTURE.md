# Rule-Based Headline-to-Canonical Transformation System

## Research Question
**Can we transform news headlines to canonical form using only deterministic, schema-based transformation rules (no ML/statistics)?**

## System Architecture

### Phase 1: Rule Extraction from Aligned Data

#### 1.1 Pattern Mining Module
Extract deterministic patterns from existing alignments:

```python
# register_comparison/generation/rule_extractor.py

class RuleExtractor:
    """Mines transformation rules from aligned canonical-headline pairs"""

    def extract_insertion_rules(self, aligned_pairs):
        """
        Extract rules for inserting deleted elements

        Example patterns:
        - NP-initial position → insert "The" if proper noun, "A/An" otherwise
        - VP-initial → insert appropriate auxiliary based on tense markers
        - Before noun → insert article based on definiteness cues
        """

    def extract_tense_restoration_rules(self, aligned_pairs):
        """
        Learn tense recovery from morphological cues

        Headlines often use simple present even for past events
        Cues: time expressions, narrative context, semantic verb class
        """

    def extract_structural_expansion_rules(self, aligned_pairs):
        """
        Map constituency/dependency transformations

        - Clause type changes (e.g., declarative → subordinate)
        - Phrase expansions (NP → full NP with modifiers)
        """
```

#### 1.2 Context Feature Encoding
```python
class ContextPattern:
    """Encodes linguistic context for rule application"""

    attributes = {
        'position': 'sentence_initial|medial|final',
        'pos_tag': str,
        'dependency_role': str,
        'parent_phrase_type': str,
        'lexical_semantics': str,  # proper noun, count/mass noun, etc.
        'discourse_marker': bool,  # time expressions, etc.
    }
```

### Phase 2: Rule Organization

#### 2.1 Rule Hierarchy
```
Level 1: Morphological Rules (most local)
├── Tense restoration (present → past/perfect)
├── Number agreement restoration
└── Person agreement restoration

Level 2: Lexical Rules
├── Article insertion (Ø → the/a/an)
├── Auxiliary insertion (Ø → have/has/had/will/etc.)
├── Preposition insertion
└── Pronoun restoration

Level 3: Syntactic Rules
├── Clause type transformation
├── Dependency relation adjustments
├── Constituent reordering
└── Phrase expansion

Level 4: Discourse Rules (most global)
├── Sentence boundary adjustments
└── Cohesion marker insertion
```

#### 2.2 Rule Application Order
```python
class RuleOrdering:
    """Defines precedence for transformation rules"""

    # Apply in this order to avoid conflicts:
    ordering = [
        'morphological_rules',
        'lexical_insertion_rules',
        'syntactic_restructuring_rules',
        'discourse_level_rules'
    ]

    # Within each level, apply most specific rules first
    specificity_metric = lambda rule: rule.context_constraints_count()
```

### Phase 3: Rule Application Engine

#### 3.1 Core Transformation Pipeline
```python
class HeadlineToCanonicalGenerator:
    """Applies transformation rules to generate canonical form"""

    def __init__(self, rule_base, schema):
        self.rule_base = rule_base
        self.schema = schema
        self.parser = DependencyParser()  # Use Stanza

    def transform(self, headline: str) -> str:
        """
        Main transformation pipeline

        Input: "Police arrest suspect"
        Output: "The police have arrested a suspect"
        """

        # 1. Parse headline
        parsed = self.parser.parse(headline)

        # 2. Apply rule levels in order
        intermediate = parsed
        for level in self.rule_base.get_ordered_levels():
            intermediate = self.apply_rule_level(intermediate, level)

        # 3. Generate surface form
        canonical = self.realize_surface_form(intermediate)

        return canonical

    def apply_rule_level(self, parse_tree, rule_level):
        """Apply all rules at a given level"""

        applicable_rules = rule_level.find_applicable_rules(parse_tree)

        # Sort by specificity (most specific first)
        applicable_rules.sort(key=lambda r: r.specificity_score(), reverse=True)

        for rule in applicable_rules:
            if rule.preconditions_met(parse_tree):
                parse_tree = rule.apply(parse_tree)

        return parse_tree
```

#### 3.2 Example Rule Implementation
```python
class ArticleInsertionRule(TransformationRule):
    """
    Insert articles before bare nouns

    Decision logic (deterministic):
    - Proper noun → "The" if unique/known, Ø if generic name
    - Count noun + singular → "a/an" if indefinite, "the" if definite
    - Count noun + plural → "the" if definite, Ø if indefinite
    - Mass noun → "the" if definite, Ø if indefinite

    Definiteness cues:
    - First mention in discourse → indefinite
    - Previously mentioned → definite
    - Uniquely identifiable (superlatives, of-PPs) → definite
    - Generic/habitual context → indefinite
    """

    def applies_to(self, node):
        """Check if this noun needs an article"""
        return (node.pos == 'NOUN' and
                not node.has_determiner() and
                not node.is_proper_noun())

    def apply(self, node):
        """Insert appropriate article"""
        article = self.determine_article(node)
        node.insert_dependent(article, relation='det', position='before')
        return node

    def determine_article(self, node):
        """Deterministic article selection"""

        # Check definiteness cues
        if self.is_definite(node):
            return "the"
        elif node.features.get('Number') == 'Sing':
            # Indefinite singular → a/an
            return "an" if self.starts_with_vowel_sound(node.lemma) else "a"
        else:
            # Indefinite plural/mass → Ø
            return None

    def is_definite(self, node):
        """Check definiteness indicators"""

        # Superlative adjective modifier
        if any(dep.pos == 'ADJ' and 'Sup' in dep.features
               for dep in node.dependents):
            return True

        # Has 'of' PP complement (often definite)
        if any(dep.relation == 'nmod' and dep.text.lower() == 'of'
               for dep in node.dependents):
            return True

        # Previously mentioned (requires discourse tracking)
        if self.discourse_tracker.previously_mentioned(node.lemma):
            return True

        # Context-specific (e.g., "police", "government" often definite)
        if node.lemma.lower() in INHERENTLY_DEFINITE_NOUNS:
            return True

        return False
```

### Phase 4: Validation & Evaluation

#### 4.1 Evaluation Metrics
```python
class TransformationEvaluator:
    """Evaluate generated canonical forms against gold standard"""

    def evaluate(self, headline, generated_canonical, gold_canonical):
        """
        Compare generated vs. actual canonical form

        Metrics:
        - Exact match rate
        - Token-level accuracy
        - POS sequence match
        - Dependency structure match (UAS/LAS)
        - Feature-by-feature correctness
        """

        return {
            'exact_match': generated_canonical == gold_canonical,
            'token_accuracy': self.token_level_accuracy(generated, gold),
            'pos_accuracy': self.pos_sequence_match(generated, gold),
            'dependency_uas': self.unlabeled_attachment_score(generated, gold),
            'dependency_las': self.labeled_attachment_score(generated, gold),
            'feature_correctness': self.feature_level_evaluation(generated, gold)
        }
```

#### 4.2 Error Analysis
```python
class ErrorAnalyzer:
    """Analyze where rule-based generation fails"""

    def categorize_errors(self, generated, gold):
        """
        Error categories:
        - Missing insertions (failed to add required element)
        - Wrong insertions (added wrong element)
        - Incorrect tense/agreement
        - Word order errors
        - Ambiguity resolution failures
        """
```

## Implementation Strategy

### Stage 1: Baseline Rule Set (Weeks 1-2)
- Implement high-confidence rules (>95% consistency in training data)
- Focus on most frequent transformations:
  - Article insertion before nouns
  - Auxiliary restoration for verbs
  - Basic tense mapping (present → past for news events)

### Stage 2: Context-Sensitive Rules (Weeks 3-4)
- Add context patterns from aligned data
- Implement disambiguation strategies
- Handle noun phrase expansion

### Stage 3: Complex Transformations (Weeks 5-6)
- Clause type changes
- Constituent reordering
- Dependency restructuring

### Stage 4: Evaluation & Refinement (Weeks 7-8)
- Test on held-out data
- Error analysis
- Rule refinement based on failures
- Measure theoretical ceiling (what % is deterministic?)

## Research Insights to Investigate

### 1. Systematicity Analysis
**Question**: What percentage of transformations are fully deterministic?

```python
def measure_systematicity(aligned_pairs):
    """
    For each transformation context, measure consistency:
    - Deterministic: Always same transformation (100%)
    - Highly systematic: >90% consistency
    - Somewhat systematic: 70-90%
    - Variable: <70%
    """
```

### 2. Information-Theoretic Limits
**Question**: How much information is truly lost in headlines?

Some deletions may be recoverable from:
- Linguistic context (syntax, semantics)
- World knowledge (news conventions)
- Discourse patterns

But some may be genuinely ambiguous without external knowledge.

### 3. Rule Interaction Effects
**Question**: Do rules compose cleanly or interfere?

Example interference:
```
Rule A: Insert article before noun
Rule B: Convert NP to PP
→ If B applies first, A may insert in wrong position
```

## Expected Outcomes

### Optimistic Scenario
- 70-80% exact match on test data
- 90-95% token-level accuracy
- Demonstrates high systematicity of register variation

### Realistic Scenario
- 50-60% exact match
- 80-85% token-level accuracy
- Identifies systematic vs. idiosyncratic transformations

### Pessimistic Scenario
- <40% exact match
- Suggests register variation is too context-dependent for pure rule-based approach
- But: Failure analysis still provides linguistic insights

## Advantages of Pure Rule-Based Approach

1. **Interpretability**: Every transformation is linguistically motivated and inspectable
2. **Theoretical Insight**: Reveals systematicity of register variation
3. **Efficiency**: No training required, fast inference
4. **Generalization**: Rules based on linguistic principles may transfer to new domains
5. **Completeness Testing**: Identifies gaps in theoretical understanding

## Integration with Existing Codebase

New modules to add:
```
register_comparison/
├── generation/
│   ├── __init__.py
│   ├── rule_extractor.py      # Mine rules from aligned data
│   ├── rule_base.py            # Store and organize rules
│   ├── transformation_engine.py # Apply rules to headlines
│   ├── context_analyzer.py     # Analyze linguistic context
│   └── evaluator.py            # Validate generated output
```

This builds on existing infrastructure:
- Uses same schema (`diff-ontology-ver-3.0.json`)
- Uses same aligned data
- Leverages existing alignment and feature extraction
- Reverses the comparison direction
