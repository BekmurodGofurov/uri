# Machine Learning Components and Model Governance

This document describes the machine learning architecture, datasets, deterministic data splitting, evaluation methodology, and model version governance for Uzum Review Intelligence (URI).

---

## 1. Machine Learning Overview

The system operates two primary machine learning tasks:
1. Sentiment Classification (`sentiment-svc`): Multi-class classification predicting whether a review has `positive`, `neutral`, or `negative` sentiment.
2. Aspect Extraction (`aspect-svc`): Multi-label tagging detecting mentioned operational dimensions (`delivery`, `quality`, `price`, `seller`, `packaging`, `other`) and their specific polarities.

---

## 2. Dataset and Deterministic Splitting

### 2.1 Primary Dataset
The sentiment model is trained on the public dataset `risqaliyevds/uzbek-sentiment-analysis` containing 352,151 Uzbek-language customer reviews from Uzum Market.

### 2.2 Hash-Based Deterministic Split
To guarantee exact reproducibility and prevent data leakage across experiments, data partitions are computed using a deterministic SHA-256 hash modulo 100:
- Train Set: 70 percent (251,141 rows)
- Validation Set: 15 percent (50,224 rows)
- Locked Test Set: 15 percent (50,786 rows)

The partition assignments are committed in `data/split_manifest.json`.

---

## 3. Evaluation Methodology and Baseline Floors

### 3.1 Class Imbalance and Metric Selection
The sentiment test dataset exhibits severe class imbalance:
- Positive: 76.9 percent (40,631 reviews)
- Negative: 18.6 percent (9,822 reviews)
- Neutral: 4.5 percent (2,370 reviews)

Because of this distribution, raw accuracy is a deceptive metric. A trivial model predicting `positive` for every example achieves 76.9 percent accuracy, but yields a Macro-F1 score of only 0.2905 and zero recall on the minority `neutral` class.

Therefore, **Macro-F1** is enforced as the primary evaluation metric.

### 3.2 Model Performance Comparison

| Model Architecture | Validation Macro-F1 | Test Macro-F1 | Overall Accuracy | Neutral Class F1 | Decision |
|---|:---:|:---:|:---:|:---:|---|
| Majority-Class Baseline | 0.2910 | 0.2905 | 76.9% | 0.00 | Rejected (Floor) |
| TahrirchiBERT-small | 0.6210 | Not Evaluated | 90.1% | 0.10 | Rejected (Low minority F1) |
| TF-IDF + Balanced Logistic Regression | 0.6291 | 0.6241 | 82.2% | 0.22 | Accepted & Deployed |

The balanced TF-IDF model outperforms the fine-tuned BERT transformer on Macro-F1 while requiring less than 50MB of memory and executing inference in under 5 milliseconds.

---

## 4. Reproducible Training Pipeline

### 4.1 Training Sentiment Service
The model is retrained deterministically using a fixed random seed:
```bash
cd sentiment-svc
python training/train.py
```
This produces `models/tfidf_v1.joblib` and writes metadata to `models/model_info.json`.

### 4.2 Locked Test Set Evaluation
The test partition is evaluated exclusively through the locked evaluation script:
```bash
cd sentiment-svc
python training/evaluate_locked_test.py
```

---

## 5. Model Registry and Instant Rollback

### 5.1 Architecture
Model metadata, version tags, evaluation metrics, and active deployment pointers are tracked in the PostgreSQL `model_versions` table and managed by `gateway/registry/`.

### 5.2 One-Command Rollback
If a newly deployed model exhibits anomalies in production, the Gateway can instantly roll back active model routing without requiring code edits or server restarts:
```bash
python -m gateway.registry.cli rollback --service sentiment --to sentiment-v1
```
The registry updates the active version pointer and subsequent inference requests route to the designated fallback model.
