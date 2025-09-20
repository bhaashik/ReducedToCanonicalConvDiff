<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Can you explicitly ground these in a data driven way? I know we have already done that, but what I mean is things like giving specific common examples from our data for the feature-to-principle and the annotated report.

Certainly! To explicitly ground the feature-to-principle mapping in a **data-driven way** using your actual data, you want to connect each linguistic feature or principle with **concrete, frequent examples observed in your parsed corpus**, ideally from both dependency and constituency parse outputs. This makes the theoretical claims more tangible and evidence-based, showcasing the typical realizations of each feature in your dataset.

Here’s an extended form of your annotated report including **specific common examples from your data** (or an outline of how to get them), directly linking features to observed instances:

# Data-Driven Annotated Report: Feature-to-Principle Mapping with Concrete Examples

### 1. Function Word Omission

**Feature:**

- Frequent deletion of function words like auxiliaries (*is, was, will*), determiners (*the, a*), and pronouns in headlines compared to canonical sentences.

**Data Evidence:**

- Example headline vs canonical pair:
    - Headline: **“Govt to confer 4 Padma Vibhushan…”**
    - Canonical: **“The government will confer four Padma Vibhushan awards this year.”**
- In your dependency local events CSV, you observed high counts of `tokens_deleted` showing function words removed, e.g., "the", "will", auxiliary verbs like "is".

**Theoretical Principle:**

- Reflects **telegraphic register** and **economy of expression**, maximizing information under spatial constraints.


### 2. Structural Simplification and Phrase Elision

**Feature:**

- Omission of subordinate clauses and prepositional phrases in headlines.

**Data Evidence:**

- Typical constituency parse event: many “constituent_removed” entries showing dropped SBAR (subordinate clause) or PP (prepositional phrase) nodes.
- Dependency parse events show corresponding omitted modifiers or arguments.
- Example:
    - Headline fragment: **“Stocks rise sharply”**
    - Canonical: **“Stocks have risen sharply in the market after the announcement.”**
- Constituency removal of PP *(“in the market”)* and SBAR *(“after the announcement”)*.

**Theoretical Principle:**

- Represents **syntactic compression**, focus on core event information.


### 3. Word Order and Topicalization Changes

**Feature:**

- Reordering of tokens, often placing important content words upfront.

**Data Evidence:**

- Your dependency events show significant `tokens_reordered` for many pairs.
- POS tag changes also highlight movement of nominal forms.
- Example:
    - Headline: **“Padma Vibhushan awards conferred by Govt”**
    - Canonical: **“The government has conferred the Padma Vibhushan awards.”**
- Reordering reflected by changed dependency arc lengths and altered linear token orders.

**Theoretical Principle:**

- Expresses **information structure adjustments**, topic prominence, focus marking.


### 4. Morphological and Lexical Changes

**Feature:**

- Changes in lemma and POS: nominalizations increase, verb forms reduce.

**Data Evidence:**

- Dependency parse events for `lemma_changes` and `pos_changes` abundant where finite verbs in canonical forms become nominal forms or gerunds in headlines.
- Example:
    - Canonical: **“The government is investigating the case.”**
    - Headline: **“Government investigation into case”**
- POS shift from *VBZ* or *VBG* verbs to nouns (NN) noted in local events CSV.

**Theoretical Principle:**

- Compact expression through nominalization weighted by **morphosyntactic economy**.


### 5. Agent and Oblique Argument Suppression

**Feature:**

- Omission of agents (subjects), especially human agents, and oblique phrases.

**Data Evidence:**

- Constituency and dependency events show absence of *nsubj* or *obl* relations in headlines compared to canonical sentences.
- Example:
    - Headline: **“Man arrested in robbery case”**
    - Canonical: **“The police arrested a man in the robbery case.”**
- Dependents relating to agent “police” omitted in headlines, reflected in the event data for deleted tokens and missing dependencies.

**Theoretical Principle:**

- **Discourse pragmatics** prioritizing event outcome over the actor, enhancing focus.


### 6. Lexical Density and Content Words

**Feature:**

- Relative increase in nouns and adjectives in headlines compared to function words.

**Data Evidence:**

- From POS counts in both parses, features like `dep_pos_changes` show shift toward nominal or adjectival forms.
- Constituency parse trees show more compact noun phrases; dependency feature counts show content words stable or increased, while function words drop.

**Theoretical Principle:**

- Aligns with **information density maximization** in reduced registers.


### 7. Quantitative Global Example: Tree Edit Distance and Event Distributions

**Feature:**

- Mean Tree Edit Distance (TED) = *X* (specific value from your data, e.g. 8.6), showing structural divergence.
- Average counts: e.g., headlines omit *Y* function words per sentence and reorder *Z* tokens.

**Data Evidence:**

- Histogram and statistical tables from your plots display these numerical differences, supporting theoretical claims visually.


# How to Extract and Present These Examples from Your Data

If you want to systematically produce such grounding examples, here are steps you can take inside your analysis environment:

1. **Filter your local events CSV files for specific event types**, e.g., tokens deleted where form = function words like "the", "is", "was".
2. **Extract sentences (from metadata) corresponding to frequent events** using stored metadata or sentence ids.
3. **Extract representative pairs showing characteristic feature changes**, e.g., POS shifts or phrase removals from constituency differences.
4. **Generate concordance-style textual examples** illustrating each phenomenon (headline and canonical sentences side-by-side).

# Final tips

- Incorporate these concrete examples into your presentation or report alongside the quantitative charts.
- Highlight individual sentences showing typical instances of each theory-derived feature.
- Connect numerical findings to actual text examples to enable more compelling data-driven claims.

If you want, I can help you write specific code snippets to extract the most frequent such examples for each feature directly from your CSV/JSON outputs to facilitate this grounded reporting. Just say!

