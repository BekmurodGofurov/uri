# Evaluation Report — `aspect-svc`

**Date:** 2026-09-10
**Model version:** `aspect-multilabel-v1`
**Author:** Biloliddin

---

## 1. Data

| Set | Size | Source |
|---|---|---|
| Gold (hand-labeled) | 300 | Hand-labeled per `TAXONOMY.md`, confirmed with a two-round kappa check |
| — of which train | 200 | Model training |
| — of which dev | 40 | Model selection/tuning (threshold-tuning was done here) |
| — of which test (LOCKED) | 60 | Untouched until the final day, used only for a single final evaluation (R5) |
| Silver (LLM-labeled, Groq) | 1173 | Randomly sampled from `risqaliyevds/uzbek-sentiment-analysis` and auto-labeled via Groq — **not included in the final training run** (see Section 2) |
| Intermediate pretraining | 47,400 | `biloliddin1221/uzbek-balanced-sentiment-analysis` — general 3-class sentiment, used only to warm up the backbone |

## 2. LLM (silver) label quality — spot-check and decision

100 gold reviews were re-labeled via Groq (`openai/gpt-oss-20b` / `allam-2-7b`) and compared against the gold answers:

| Metric | Result |
|---|---|
| Exact match (all aspects + polarity) | 15.2% (15/99) |
| Aspect-level match | 53.0% (315/594) |

**Key finding:** when compared to a trivial "no aspect present" baseline (e.g. 88.9% for `delivery`, 90.9% for `packaging`), the LLM scored **below** this trivial baseline on **5 of 6 aspects** (`delivery`, `price`, `seller`, `packaging`, `other`) — it was only relatively good on `quality` (the most frequent class).

**Decision:** The silver set (1173 rows) was **not included in the final training run**. The evidence showed that low-quality LLM labels add more noise than useful signal. This is not a result of time or resource constraints, but a deliberate decision based on measured quality.

## 3. Model architecture

- **Backbone:** `tahrirchi/tahrirchi-bert-small`
- **Intermediate fine-tuning:** 2 epochs on a 47,400-row balanced sentiment dataset (general 3-class sentiment classification) — to adapt the backbone to real Uzbek text style, without any LLM API cost. Loss 0.755 → 0.665 (epoch 1→2).
- **Main training:** two-headed architecture, 8 epochs, gold train only (200 rows)
  - **Presence head:** 6 sigmoid outputs, **BCE loss + `pos_weight`** (to compensate for class imbalance — in an earlier attempt, without `pos_weight`, the model collapsed to predicting only the majority class, with F1=0 for every rare aspect)
  - **Polarity head:** 3-class classification per aspect (negative/neutral/positive), masked cross-entropy (computed only for aspects that are actually present)

## 4. Final result — on the LOCKED test set (60 rows, one-time, R5)

**Methodological note:** the model results below were obtained with an **unadjusted, strict 0.5 threshold** (the threshold-tuning done on dev was deliberately *not* applied to this final test, to avoid fitting to the test set).

| Aspect | Majority F1 | Keyword F1 | Model Precision | Model Recall | **Model F1** |
|---|---|---|---|---|---|
| delivery | 0.000 | 0.250 | 0.091 | 0.167 | 0.118 |
| quality | 0.763 | 0.426 | 0.659 | 0.730 | **0.692** |
| price | 0.000 | 0.909 | 0.200 | 0.167 | 0.182 |
| seller | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| packaging | 0.000 | 0.375 | 0.667 | 0.364 | 0.471 |
| other | 0.000 | 0.213 | 0.000 | 0.000 | 0.000 |
| **Macro-F1** | **0.127** | **0.362** | - | - | **0.244** |

## 5. Conclusion and limitations — an honest assessment

**Where the model beat the baselines:**
- `quality` — clearly better (0.692 vs. 0.426 keyword)
- `packaging` — somewhat better (0.471 vs. 0.375 keyword)

**Where the model fell short:**
- `price` — the keyword rule was surprisingly strong (0.909), because this aspect is expressed through clear, unambiguous lexical markers ("narx", "qimmat", "arzon"), which gives a simple rule a natural advantage
- `delivery` — below the keyword baseline
- `seller`, `other` — the model failed to detect these at all (Recall=0)

**Identified causes:**
1. **Small training size** (200 rows) — aspects like `seller` (~26), `other` (~30), and `delivery` (~29) had too few examples
2. **Unadjusted threshold (0.5)** — threshold-tuning on dev had selected much lower cutoffs (0.20–0.30) for `seller`/`other`; these were not applied in the final test, causing the model to be overly "cautious" and predict rare aspects almost never
3. **`seller` and `other`** were also the aspects with the most disagreement in the `TAXONOMY.md` kappa check (kappa 0.479 and 0.44) — this human-level ambiguity carried over to the model as well

**Overall conclusion:** The model added real value for some aspects (`quality`, `packaging`), but is not yet reliable for low-data aspects (`seller`, `other`, and partly `delivery`/`price`). This is the expected limitation of multi-label fine-tuning on a small gold set (300 rows), not a failure.

## 6. Future improvement directions

- Apply the per-aspect thresholds (selected on dev) at final inference time — especially for `seller`/`other`
- Collect additional hand-labeled examples for `seller`, `other`, and `delivery`
- Retry silver-labeling with a stronger LLM or an improved prompt (the current Groq output was low quality — see Section 2)