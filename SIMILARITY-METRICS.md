Yes — **conditional entropy** and **relative entropy (KL divergence)** are different objects, and for “two language strings” they answer different questions.

## 1) What they are (and why they’re different)

### Conditional entropy (depends on a *joint* model)

* **Definition:** (H(Y\mid X)) is the remaining uncertainty in (Y) once (X) is known.
* It requires a **joint distribution** (p(x,y)) (equivalently (p(y\mid x)) plus (p(x))).
* In language terms, (X) and (Y) might be:

  * aligned/parallel strings (translation pairs),
  * bilingual paired samples (e.g., same content in two languages),
  * or a latent-variable model that ties them together.

Classic reference definitions: Shannon’s original paper and standard textbooks. ([Harvard Math People][1])

### Relative entropy / KL divergence (compares *two* distributions)

* **Definition:** (D_{\mathrm{KL}}(P|Q)=\sum_x P(x)\log\frac{P(x)}{Q(x)}).
* It compares **two distributions over the same event space** (same vocabulary / same feature space), and does **not** require a joint model of paired samples.
* In language terms, you usually pick a representation (token unigrams, character n-grams, subword n-grams, topic distributions, etc.) and compare those distributions across languages/corpora.

Foundational reference: Kullback & Leibler (1951) and standard info-theory texts. ([SciSpace][2])

**Key relationship (often confused):**
“Cross-entropy” decomposes into entropy + KL:
[
H(P,Q)=H(P)+D_{\mathrm{KL}}(P|Q)
]
So when you evaluate a model trained on one language/corpus on another, you are often implicitly measuring **cross-entropy**, which includes a KL term. (This connection is explicitly used in standard perplexity definitions.) ([Wikipedia][3])

---

## 2) “Usual measures” for language strings (practical estimators)

Because you don’t directly have (p(\cdot)), you estimate via language models or empirical n-gram distributions.

### A. Entropy / cross-entropy / perplexity (most common in NLP)

Given a sequence (w_{1:N}) and a model (q),

* **Per-token cross-entropy estimate:**
  [
  \hat H = -\frac{1}{N}\sum_{i=1}^N \log q(w_i \mid w_{<i})
  ]
* **Perplexity:** (\mathrm{PPL} = b^{\hat H}) (often (b=2) or (e)).

This is the standard “LM perplexity = exponentiated average negative log-likelihood / cross-entropy” story. ([Wikipedia][3])

**Variations**

* word-level vs subword-level vs character-level perplexity (tokenization matters).
* sentence-level vs corpus-level (normalize by tokens/characters).
* smoothing choices for n-gram LMs (classic). ([People @ EECS][4])

### B. Conditional entropy for bilingual / paired strings

If you have paired data ((x,y)) (e.g., translation pairs):

* **Conditional cross-entropy / negative log-likelihood of (y) given (x):**
  [
  \hat H(Y\mid X) \approx -\frac{1}{N}\sum_{(x,y)} \log q(y\mid x)
  ]
  Used implicitly whenever you evaluate a translation model or conditional generator.

(Info-theory definition basis: Shannon / Cover–Thomas.) ([Harvard Math People][1])

### C. KL / divergence between *language distributions* (requires shared feature space)

Pick features that make sense across languages (common trick: **character n-grams**, IPA features, multilingual subwords, POS tag distributions, etc.). Let (\hat P) be the empirical distribution from language A and (\hat Q) from language B:

* **KL:** (D_{\mathrm{KL}}(\hat P|\hat Q)) (asymmetric, can blow up with zeros).
* **Symmetrized KL:** (D_{\mathrm{KL}}(P|Q)+D_{\mathrm{KL}}(Q|P)).
* **Jensen–Shannon divergence (JSD):** symmetric + bounded, widely used as a safer alternative. ([CompSci Engineering][5])

A useful NLP/ML thread that uses KL-family divergences for distributional similarity is summarized in classic distributional similarity work/notes. ([Cornell Computer Science][6])

### D. Cross-entropy difference (domain/data selection; also “distance-like”)

A very common *practical* “difference of cross-entropies” measure:
[
\Delta H(s) = H_{\text{in}}(s) - H_{\text{out}}(s)
]
used for selecting sentences close to a target domain; it’s not exactly KL but is closely related to comparing how two LMs score the same string. ([ACL Anthology][7])

### E. Compression-based “string distance” (alignment-free)

If you truly want to compare two raw strings without choosing probabilistic features, you’ll often see:

* **Normalized Compression Distance (NCD)** and related “information distance” ideas (compression approximates Kolmogorov complexity). ([Mathematics at UC Davis][8])

---

## 3) Normalized versions (analogous to “normalized perplexity”)

### A. Length normalization (most standard)

* **Entropy rate / per-token (or per-character) normalization:** divide total negative log-likelihood by (N). This is exactly why perplexity is typically reported “per token”. ([Wikipedia][3])
* Character-level cross-entropy (bits/char) is often preferred for cross-language comparisons (less tokenization bias).

### B. Vocabulary/maximum-entropy normalization

Common normalizations to map values into comparable ranges:

* **Normalize cross-entropy by (\log |V|)** (max entropy for uniform over a vocab of size (|V|)):
  (\hat H / \log |V|)  (careful: (|V|) depends on tokenization/feature choice).
* **Perplexity normalized by vocab size:** (\mathrm{PPL}/|V|) (much less common in serious LM papers; more common in quick comparisons).

### C. Bounded divergences (a “built-in normalization”)

* **JSD is bounded** (0 to (\log 2) with natural logs; 0 to 1 with base-2 logs), which makes it a popular “normalized divergence”. ([Wikipedia][9])
* Sometimes people report **JS distance** (=\sqrt{\mathrm{JSD}}) (a metric).

### D. KL normalization (not canonical, but used)

Because KL is unbounded, papers sometimes use:

* (D_{\mathrm{KL}}(P|Q)/\log |V|) (feature-space bound proxy),
* or **clip/smooth** probabilities and then compare.

### E. Normalized compression distance (already normalized)

* NCD is explicitly constructed as a normalized similarity/distance from compressed lengths. ([Mathematics at UC Davis][8])

---

## 4) Practical guidance for “two strings from two languages”

* If the strings are **translations / aligned content**, conditional entropy (H(Y\mid X)) is meaningful (model (q(y\mid x))).
* If they’re **unpaired** and you want “language distance”, you typically estimate **divergence between distributions** built from features (character n-grams → KL/JSD) or use **compression-based distances**.
* If you’re evaluating an LM trained on language A against text in language B, you are measuring **cross-entropy/perplexity of B under A’s model**, which relates to KL via (H(P,Q)=H(P)+D_{\mathrm{KL}}(P|Q)). ([Wikipedia][3])

---

## References (with publication links)

* Shannon, C. (1948) *A Mathematical Theory of Communication* (entropy, conditional entropy foundations). ([Harvard Math People][1])
* Cover, T. & Thomas, J. *Elements of Information Theory* (standard definitions + identities). ([CS-114][10])
* Kullback, S. & Leibler, R. (1951) *On Information and Sufficiency* (KL / relative entropy). ([SciSpace][2])
* Chen, S. & Goodman, J. (1996) *An Empirical Study of Smoothing Techniques for Language Modeling* (cross-entropy evaluation; n-gram LM practice). ([ACL Anthology][11])
* Jelinek, F. *Statistical Methods for Speech Recognition* (LM evaluation foundations; cross-entropy/perplexity in practice). ([MIT Press][12])
* Moore, R. & Lewis, W. (2010) *Intelligent Selection of Language Model Training Data* (cross-entropy difference). ([ACL Anthology][7])
* Lin, J. (1991) *Divergence measures based on the Shannon entropy* (Jensen–Shannon divergence). ([CompSci Engineering][5])
* Cilibrasi, R. & Vitányi, P. (2005) *Clustering by Compression* (NCD). ([Mathematics at UC Davis][8])
* Vitányi et al. (2008) *Normalized Information Distance* (theory + practical realizations). ([arXiv][13])

If you tell me what your “strings” are (raw text? tokenized? IPA? aligned parallel pairs?), I can recommend the *most defensible* pairing of (conditional entropy vs divergence) and a normalization that won’t get dominated by tokenization artifacts.

[1]: https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf?utm_source=chatgpt.com "A Mathematical Theory of Communication"
[2]: https://scispace.com/papers/on-information-and-sufficiency-3o6xv2h9bw?citations_page=151&utm_source=chatgpt.com "Solomon Kullback - On Information and Sufficiency"
[3]: https://en.wikipedia.org/wiki/Perplexity?utm_source=chatgpt.com "Perplexity"
[4]: https://people.eecs.berkeley.edu/~klein/cs294-5/chen_goodman.pdf?utm_source=chatgpt.com "An Empirical Study of Smoothing Techniques for"
[5]: https://www.cise.ufl.edu/~anand/sp06/jensen-shannon.pdf?utm_source=chatgpt.com "Divergence measures based on the Shannon entropy"
[6]: https://www.cs.cornell.edu/courses/cs6742/2017fa/handouts/lee-ch2.3.pdf?utm_source=chatgpt.com "2.3 Measures of Distributional Similarity"
[7]: https://aclanthology.org/P10-2041.pdf?utm_source=chatgpt.com "Intelligent Selection of Language Model Training Data"
[8]: https://www.math.ucdavis.edu/~saito/data/acha.read.w17/cilibrasi-vitanyi_clustering-by-compression.pdf?utm_source=chatgpt.com "Clustering by Compression"
[9]: https://en.wikipedia.org/wiki/Jensen%E2%80%93Shannon_divergence?utm_source=chatgpt.com "Jensen–Shannon divergence"
[10]: https://cs-114.org/wp-content/uploads/2015/01/Elements_of_Information_Theory_Elements.pdf?utm_source=chatgpt.com "Elements of Information Theory"
[11]: https://aclanthology.org/P96-1041.pdf?utm_source=chatgpt.com "An Empirical Study of Smoothing Techniques for Language ..."
[12]: https://mitpress.mit.edu/9780262100663/statistical-methods-for-speech-recognition/?utm_source=chatgpt.com "Statistical Methods for Speech Recognition"
[13]: https://arxiv.org/abs/0809.2553?utm_source=chatgpt.com "Normalized Information Distance"
