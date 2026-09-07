# EVALUATION.md — Sentiment Service

## 1. Models Compared

| Model | Val Macro-F1 | Test Macro-F1 | Accuracy | Notes |
|---|---|---|---|---|
| **Majority-Class Baseline** | 0.2910 | 0.2905 | 76.9% | Predicts 'positive' for everything (floor) |
| **TF-IDF + LR (v1 - Shipped)** | 0.6291 | **0.6241** | 82.2% | Baseline with `class_weight='balanced'` |
| **TahrirchiBERT-small (v1)** | 0.6210 | — | **90.1%** | 67M params, fine-tuned 3 epochs on GPU |

---

## 2. Winner & Key Finding

### 🏆 Winner: **TF-IDF + Logistic Regression**
- **Macro-F1:** `0.6241` vs `0.6210`
- **Why TF-IDF Won:** E-commerce reviews have a 77% positive class imbalance. Standard cross-entropy loss caused TahrirchiBERT to heavily optimize for the majority positive class (achieving 90% accuracy but a near-zero 0.10 F1 on `neutral`). TF-IDF with `class_weight='balanced'` penalized errors on the rare `neutral` class, pulling ahead on Macro-F1 (0.22 vs 0.10).
- **Takeaway:** Model scale does not compensate for severe class imbalance.

---

## 3. Per-Class Test Results (TF-IDF + LR)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **negative** | 0.71 | 0.78 | 0.75 | 9,822 |
| **neutral** | 0.15 | 0.40 | 0.22 | 2,370 |
| **positive** | 0.97 | 0.85 | 0.91 | 40,631 |
| **Macro Avg** | **0.61** | **0.68** | **0.62** | 52,823 |

### Confusion Matrix (Test Set)

```text
               Predicted:
               Negative   Neutral   Positive
Actual Neg:    [  7706      1505       611  ]
Actual Neu:    [   904       947       519  ]
Actual Pos:    [  2194      3832     34605  ]