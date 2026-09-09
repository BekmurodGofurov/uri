# aspect-svc — Evaluation Report

## 1. Taxonomy and Gold-Set

6 aspects: `delivery`, `quality`, `price`, `seller`, `packaging`, `other` (detailed definitions and examples: `TAXONOMY.md`).

300 manually annotated reviews — randomly sampled from the `risqaliyevds/uzbek-sentiment-analysis` dataset (`random_state=42`, reproducible). The 300 samples are split into 3 subsets: **200 train / 40 dev / 60 test (LOCKED — reserved for final unbiased evaluation)**.

---

## 2. Self-Agreement (Cohen's Kappa)

50 gold reviews were re-annotated blind on a subsequent day (without showing original annotations) and compared against the first annotation pass (at the presence level, evaluated per aspect).

| Aspect | Kappa (presence) | N |
|---|---|---|
| delivery | 0.898 | 50 |
| quality | 0.674 | 50 |
| price | 0.778 | 50 |
| seller | **0.479** | 50 |
| packaging | 0.778 | 50 |
| other | **0.440** | 50 |

**Summary:** Self-agreement is high (>0.75) for `delivery`, `price`, and `packaging` — indicating clear definitions that were consistently applied. For `seller` and `other`, Kappa dropped below 0.6, as boundaries between these two categories remained less distinct in the taxonomy (e.g., distinguishing general seller interaction from overall impression/other). Refining these two definitions in `TAXONOMY.md` is recommended for future iterations.

---

## 3. Baselines

| Aspect | Majority baseline | Keyword baseline |
|---|---|---|
| delivery | 0.000 | 0.000 |
| quality | 0.710 | 0.286 |
| price | 0.000 | 0.833 |
| seller | 0.000 | 0.333 |
| packaging | 0.000 | 0.444 |
| other | 0.000 | 0.258 |

As expected, the keyword baseline performed strongly on aspects with explicit lexical signals (`price`, `packaging`), serving as a benchmark target for the model in subsequent steps.

---

## 4. LLM Bootstrap — Experiment and Rejection

Using Groq (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`), 1,173 silver labels were generated from the remaining part of the `risqaliyevds/uzbek-sentiment-analysis` dataset (excluding the 300 gold samples and exact text duplicates).

**Spot-Check Results** (Re-annotating 100 gold reviews with LLM vs. original gold labels; "Trivial" column represents accuracy when predicting "aspect absent" for all cases):

| Aspect | LLM Agreement | Trivial Baseline | Conclusion |
|---|---|---|---|
| delivery | 44.4% | 88.9% | ❌ LLM worse than trivial |
| quality | 57.6% | 30.3% | ✅ LLM better |
| price | 50.5% | 85.9% | ❌ LLM worse than trivial |
| seller | 46.5% | 90.9% | ❌ LLM worse than trivial |
| packaging | 63.6% | 90.9% | ❌ LLM worse than trivial |
| other | 55.6% | 92.9% | ❌ LLM worse than trivial |

**Decision: Silver-set was excluded from final training.**
Reason: In 5/6 aspects, the LLM performed below the trivial baseline due to a high rate of false positives, introducing more noise than signal. Downweighting (e.g., `weight=0.3`) would still introduce detrimental noise at this error rate. Prioritizing quality over quantity, the final model was trained **strictly on the gold train-set (200 samples)**.

---

## 5. Final Test Evaluation (Locked Test Set)

Base Model: `tahrirchi/tahrirchi-bert-small`  
Device: `cpu` / `cuda`  
Results saved in: `locked_test_results.json`

### Aspect-Level Performance Metrics

| Aspect | Majority F1 | Keyword F1 | Model Precision | Model Recall | Model F1 |
|---|---|---|---|---|---|
| delivery | 0.000 | 0.250 | 0.091 | 0.167 | **0.118** |
| quality | 0.763 | 0.426 | 0.659 | 0.730 | **0.692** |
| price | 0.000 | 0.909 | 0.200 | 0.167 | **0.182** |
| seller | 0.000 | 0.000 | 0.000 | 0.000 | **0.000** |
| packaging | 0.000 | 0.375 | 0.667 | 0.364 | **0.471** |
| other | 0.000 | 0.213 | 0.000 | 0.000 | **0.000** |

### Macro-F1 Summary

* **Majority Baseline:** 0.127
* **Keyword Baseline:** 0.362
* **Model Macro-F1:** **0.244**

---

## 6. Known Limitations and Next Steps

- **Keyword baseline outperforms model on explicit lexical keywords (`price`):** Keywords like "narx", "qimmat", and "arzon" carry high lexical signal. Rule-based regex captures these cleanly, whereas the model required more than ~17 positive training samples to fully learn these patterns.
- **Limited dataset size:** Due to small sample sizes in certain classes (`seller`, `other`), statistical variance remains high on rare aspects. Collecting more high-quality manual annotations is recommended over synthetic LLM bootstrapping.
- **Future Improvements:** Future work may explore refined few-shot prompt strategies for LLM silver generation or fine-tuning with larger domain-specific transformer backbones.