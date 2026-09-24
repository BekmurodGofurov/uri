---
name: evaluate-ml-models
description: Evaluate machine learning models against locked test sets and verify that candidate models exceed Macro-F1 baselines before deployment.
---

# Evaluate ML Models Skill

Use this skill whenever training, evaluating, or auditing sentiment and aspect models.

---

## When to Use
- After retraining a candidate model in `sentiment-svc` or `aspect-svc`.
- When verifying that a new model beats the majority-class baseline floor.
- Before updating serialized model artifacts (`.joblib` or checkpoint weights).

---

## Metric Baselines and Floors

### Sentiment Service Baselines
- Majority-Class Floor: Macro-F1 = 0.2905 (Test set). Any model at or below this floor must be rejected immediately.
- Production Target: Macro-F1 >= 0.6240.
- Neutral Class Recall: The minority neutral class (4.5 percent) must achieve F1 >= 0.20 to avoid degenerate majority-class collapse.

---

## Execution Steps

### Step 1: Verify Split Integrity
Confirm that `sentiment-svc/data/split_manifest.json` is untampered:
- Train partition: 70 percent (251,141 samples)
- Validation partition: 15 percent (50,224 samples)
- Test partition: 15 percent (50,786 samples)

### Step 2: Evaluate Sentiment Model on Test Set
Run the locked test evaluation script:
```bash
cd sentiment-svc
python training/evaluate_locked_test.py
```

### Step 3: Verify Aspect Service Performance
Run locked evaluations against `aspect-svc/gold_set.jsonl`:
```bash
cd aspect-svc
python training/evaluate_locked_test.py
```

### Step 4: Compare with Deployed Model Info
Inspect `models/model_info.json` to ensure the candidate model outperforms the currently active model before serializing new artifacts.

---

## Acceptance Criteria
- Candidate Macro-F1 strictly beats baseline floor (0.2905 for sentiment).
- Evaluation runs strictly against committed split manifests and locked test sets.
- Results and confusion matrix are recorded in `EVALUATION.md`.
