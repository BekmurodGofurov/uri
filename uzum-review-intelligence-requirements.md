# Uzum Review Intelligence — Project Requirements

**Duration:** 7 working days
**Team:** 3 engineers
**Goal:** Ship a working service that scores Uzbek-language product reviews for sentiment and tags which aspect a complaint is about, with a dashboard and alerting on top.

**The real goal:** every model that ships must beat a measured baseline, every service must have tests, and no one person may write the whole thing.

---

## 1. Why this project

GSH was built in nine days and worked. But it had no tests, no CI, no model evaluation, and one person wrote 78% of it. The "ML" in it was a rolling Z-score, which is a threshold, not a learned model.

This project is deliberately smaller in engineering scope and much larger in ML rigour. Three things must happen that did not happen in GSH:

1. **A model gets trained, evaluated against a baseline, and rejected if it loses.**
2. **Tests and CI exist from day one, not as a cleanup pass at the end.**
3. **Each person owns a service the others cannot commit to.**

---

## 2. What we're building

Reviews come in. Two models score them. A dashboard shows per-product sentiment and an aspect breakdown, and raises an alert when a product's sentiment drops sharply.

```
                 ┌──────────────────────┐
   reviews  ───► │  ingest + storage    │ ◄── Bekmurod
                 └──────────┬───────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
     ┌─────────────────┐         ┌─────────────────┐
     │ sentiment-svc   │         │  aspect-svc     │
     │   (Hayotbek)    │         │  (Biloliddin)   │
     └────────┬────────┘         └────────┬────────┘
              └─────────────┬─────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ dashboard + alerts   │ ◄── Bekmurod
                 └──────────────────────┘
```

Three repositories, or one repository with three top-level services and enforced CODEOWNERS. Either is fine. What is not fine is one person committing across all three.

---

## 3. Data

Everything is public, already labelled, and downloads in minutes. There is no data collection phase.

### Primary dataset — sentiment

**[risqaliyevds/uzbek-sentiment-analysis](https://huggingface.co/datasets/risqaliyevds/uzbek-sentiment-analysis)**

Uzum Market product reviews. Two fields: `normalized_review_text` and `rating`. Ratings are 1–5, mapping to very poor / poor / fair / good / excellent. 352,151 rows. MIT licensed.

```python
from datasets import load_dataset
ds = load_dataset("risqaliyevds/uzbek-sentiment-analysis")
```

### Primary dataset — aspects

**[Sanatbek/aspect-based-sentiment-analysis-uzbek](https://huggingface.co/datasets/Sanatbek/aspect-based-sentiment-analysis-uzbek)**

Aspect-based sentiment for Uzbek. 6,180 rows, parquet, roughly 330 KB. Small — this is a seed set, not a training set. Expanding it is part of the work.

### Reference: the result you must reproduce or refute

**[sssplash6/uzbek-sentiment-analysis](https://github.com/sssplash6/uzbek-sentiment-analysis)** (MIT)

Someone benchmarked TF-IDF + logistic regression against mBERT, DistilBERT and XLM-RoBERTa on roughly 1,172 Uzbek e-commerce reviews. **TF-IDF + logistic regression beat all three transformers.** Their stated reason: with that little data, transformers cannot leverage their pretraining, while TF-IDF benefits from the predictable vocabulary of e-commerce reviews.

Read this repo on day one. It is the single most important reference in the project.

### Models to fine-tune

| Model | Params | Notes | Link |
|---|---|---|---|
| `tahrirchi/tahrirchi-bert-small` | 67M | Uzbek-only, Latin script, Apache-2.0. Start here. | [HF](https://huggingface.co/tahrirchi/tahrirchi-bert-small) |
| `tahrirchi/tahrirchi-bert-base` | 110M | Same family, larger | [HF](https://huggingface.co/tahrirchi/tahrirchi-bert-base) |
| `xlm-roberta-base` | 279M | Multilingual, handles Russian code-switching | [HF](https://huggingface.co/FacebookAI/xlm-roberta-base) |
| `distilbert-base-multilingual-cased` | 134M | Fast, weaker | [HF](https://huggingface.co/distilbert/distilbert-base-multilingual-cased) |

The Tahrirchi models are case-sensitive and trained on Latin-script Uzbek only. If reviews contain Cyrillic, those models will handle them badly — that is a finding to report, not a bug to hide.

### Optional, if more data is needed

- **[murodbek/uz-text-classification](https://huggingface.co/datasets/murodbek/uz-text-classification)** — 512,750 Uzbek news articles across 15 categories, Latin script. ([Zenodo mirror](https://zenodo.org/records/7677431), [paper](https://arxiv.org/abs/2302.14494))
- **[BERTbek paper](https://aclanthology.org/2024.sigul-1.5.pdf)** — Uzbek-specific BERT evaluation, useful for expected score ranges.

---

## 4. Rules that apply to everyone

These are not suggestions. A pull request that violates one gets closed, not fixed in review.

**R1 — Contracts are frozen on day 1.** The API schemas in section 8 are agreed and merged before anyone writes implementation code. After day 1, changing a contract requires all three people to agree in writing.

**R2 — Nobody commits outside their own service.** If Bekmurod finds a bug in `sentiment-svc`, he opens an issue. He does not fix it. This is the rule that will feel worst and matters most.

**R3 — Pull requests are capped at 400 changed lines.** GSH had a single 2,280-line commit. That is unreviewable. If a change is bigger than 400 lines, it is more than one change.

**R4 — No model merges without a number.** Every PR touching a model must state, in the description: the metric, the value, the baseline it is being compared against, and the exact command that reproduces it. "Improved accuracy" is not a number.

**R5 — The test set is not touched until day 6.** Split the data on day 1 by a hash of the row index, commit the split, and use only train/validation until the final evaluation. Anyone who looks at test scores mid-week has invalidated them.

**R6 — CI must be green to merge.** Set it up on day 1 with a single trivial test, before there is anything to test. Adding CI later never happens.

**R7 — Commit messages follow Conventional Commits.** `feat:`, `fix:`, `docs:`, `chore:`, `test:`. See [conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/).

---

## 5. Hayotbek — `sentiment-svc`

### What you own

A service that takes review text and returns a sentiment label with a confidence score, plus the evaluation report that justifies whichever model is inside it.

### Why this is your assignment

In GSH you shipped ML services built on a rolling Z-score in three bulk commits. A Z-score is a threshold — it has no training, no evaluation, and no way to be wrong in a measurable sense. This week you train an actual model and defend its number. The work is iterative by nature: each run produces a number, and the number is the deliverable, not the code.

### Tasks

**1. Split the data first.** Before any modelling. Hash-based, deterministic, committed as a file. 80/10/10 train/val/test.

**2. Decide the label mapping and write down why.** Ratings are 1–5. You need classes. Obvious mapping is 1–2 → negative, 3 → neutral, 4–5 → positive. But 3-star reviews in e-commerce are frequently mixed rather than neutral ("delivery was slow but the product is fine"), and you may find dropping them gives a cleaner problem. Either choice is acceptable. Not documenting the choice is not.

**3. Check class balance before training anything.** E-commerce ratings skew hard positive. If 80% of reviews are 5-star, a model that predicts "positive" for everything scores 80% accuracy and is worthless. **Report macro-F1, not accuracy.** Include the majority-class baseline in every comparison so the floor is visible.

**4. Normalise the text — carefully.** Uzbek Latin script has multiple encodings of the same apostrophe: `'`, `ʻ`, `'`, `` ` ``. `o'zbek`, `oʻzbek` and `o'zbek` are the same word and will tokenise differently. Write the normaliser, unit-test it, and check how much it changes your baseline score. This is a small task that will measurably move your numbers.

**5. Build the TF-IDF + logistic regression baseline.** [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) and [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). This should take under an hour and gives you a number by end of day 1.

**6. Fine-tune a transformer and try to beat it.** Use the [Transformers Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) or write the loop yourself. Start with `tahrirchi-bert-small` — 67M parameters trains fast on a free T4.

**7. Run the learning curve.** Train on 1k, 5k, 20k, 100k rows and plot macro-F1 for both the baseline and the transformer. Find the crossover point where the transformer starts winning. **This plot is the most valuable artifact you will produce this week.** It answers a question most engineers never test: how much data do you actually need before a big model is worth it?

**8. Error analysis.** Take 50 misclassified validation examples and read them. Categorise the failures. You will find sarcasm, reviews about delivery rather than the product, Russian-language reviews, and reviews whose star rating simply doesn't match the text. Write up what you find.

### Deliverables

- [ ] `sentiment-svc` implementing the contract in section 8
- [ ] Committed data split file
- [ ] `EVALUATION.md`: baseline vs transformer, macro-F1 and per-class F1, confusion matrix, learning curve plot, error analysis
- [ ] Reproducible training script — one command, fixed seed
- [ ] Unit tests for the text normaliser and the label mapper

### Acceptance criteria

- The shipped model beats the TF-IDF baseline on validation macro-F1, **or** you ship the TF-IDF baseline and explain in `EVALUATION.md` why the transformer lost. Shipping the baseline is a valid, successful outcome.
- Per-class F1 is reported, not just accuracy.
- A second person can rerun your training script and get the same number.

### Pitfalls

- Reporting accuracy on imbalanced data. Report macro-F1.
- Tuning on the test set. See R5.
- Assuming a bigger model is better. The reference benchmark says otherwise at low data volumes. Prove which regime you're in.
- Forgetting to set a seed, then being unable to reproduce your own best run.

---

## 6. Biloliddin — `aspect-svc`

### What you own

A service that takes review text and returns which aspects it mentions and the polarity of each — the gold label set behind it, and the evaluation.

### Why this is your assignment

In GSH you wrote `bridge.py` and its Docker wiring — real work, but small, and downstream of decisions other people made. This week you own an open-ended problem end to end: you define the label space, you create the ground truth, you train the model, you report the number. This is the biggest step up of the three. Expect it to be uncomfortable on days 2 and 3.

### Tasks

**1. Define the aspect taxonomy, and get it agreed on day 1.** Proposed starting point: `delivery`, `quality`, `price`, `seller`, `packaging`, `other`. Multi-label — one review can mention several. Look at 100 random reviews before you commit to the list; if the data says you need a different category, change it on day 1, not day 4.

**2. Hand-label 300 reviews yourself. This is your gold set.** It is not optional and it cannot be delegated to a model. You need ground truth that no model has touched. Budget three to four hours. Use [Label Studio](https://labelstud.io/) or a 50-line Streamlit app — do not spend a day building a labelling tool.

**3. Check your own consistency.** Re-label 50 of the 300 the next day without looking at your first answers. Measure agreement with [Cohen's kappa](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html). If you disagree with yourself more than 20% of the time, your taxonomy is ambiguous and no model will do better than you — fix the definitions before training.

**4. Bootstrap a larger training set with an LLM.** Prompt a large model to label several thousand reviews against your taxonomy. This is distant supervision: the labels are noisy and you must treat them as such. Spot-check 100 of them against your own judgement and report the LLM's agreement rate with your gold set. **That agreement rate is a ceiling on what you can expect from a model trained on those labels.**

**5. Establish the baseline.** Two of them: majority-class per aspect, and a keyword-matching rule set (`yetkazib berish` → delivery, `narx` → price, and so on). The keyword baseline will be better than you expect. Beat it or explain why you didn't.

**6. Train the classifier.** Multi-label — that means sigmoid outputs and binary cross-entropy, not softmax. See [Transformers multi-label classification](https://huggingface.co/docs/transformers/tasks/sequence_classification). Same base models as Hayotbek uses; compare notes but train separately.

**7. Report per-aspect F1, not an average.** `delivery` will be common and easy. `packaging` will be rare and hard. An overall F1 hides that completely, and the rare aspects are usually the ones a business actually wants flagged.

### Deliverables

- [ ] `aspect-svc` implementing the contract in section 8
- [ ] `gold_set.jsonl` — 300 hand-labelled reviews, committed
- [ ] `TAXONOMY.md` — each aspect defined with three positive and three negative examples
- [ ] `EVALUATION.md`: per-aspect precision/recall/F1, both baselines, LLM-agreement rate, self-agreement kappa
- [ ] Reproducible training script

### Acceptance criteria

- Gold set exists, is hand-labelled, and was never used for training.
- Per-aspect F1 reported for every aspect, including the rare ones.
- Model beats both baselines on macro-F1 across aspects, or the report explains why not.

### Pitfalls

- Spending two days building a labelling UI. Use an existing tool.
- Treating LLM labels as ground truth. They are noisy training data; your 300 hand-labelled rows are ground truth.
- Using softmax for a multi-label problem. Reviews mention more than one aspect.
- Defining aspects so vaguely that you can't label consistently. The kappa check on day 3 exists to catch this while there's still time.

---

## 7. Bekmurod — platform

### What you own

Ingest, storage, the dashboard, alerting, CI, and the model registry. Everything except the two model services.

### Why this is your assignment

You can already build this. The streaming, the FastAPI services, the dashboard, the alert delivery — you did all of it in GSH in nine days, and you can reuse those patterns directly. That reuse is what makes a one-week schedule possible.

So the platform is not the challenge. The challenge is the three things your GSH history shows you skipped entirely: **there is not a single test file in GSH, there is no CI workflow, and there is no way to roll back a bad deploy.** Those are your actual deliverables this week. The dashboard is the easy part.

The second challenge is R2. You are not allowed to fix the ML services. In GSH you touched 98% of the files in the repository and were the sole author of four services — which means if you left, four services would have no maintainer. This week you practise letting other people's code be broken for a few hours.

### Tasks

**1. Repository skeleton and CI on day 1, before anything else.** [GitHub Actions](https://docs.github.com/en/actions/writing-workflows/quickstart) running [pytest](https://docs.pytest.org/) and [ruff](https://docs.astral.sh/ruff/). One trivial passing test. Branch protection on `main` requiring CI green. Do this in the first two hours.

**2. Publish the frozen contracts.** Pydantic models in a shared package, exactly as in section 8, merged before lunch on day 1. Both ML services import them. This is what makes parallel work possible.

**3. Ingest and storage.** Load the Uzum dataset into Postgres. You do not need TimescaleDB here — resist the urge to reuse the whole GSH stack. Tables: `reviews`, `predictions`, `products`.

**4. Stub both ML services immediately.** Write fake versions that return random labels matching the contract. Now you can build the entire dashboard and alerting on day 2 without waiting for anyone. When the real services land on day 5, you swap the URL.

**5. Model registry with rollback.** Every model artifact is versioned. `model_version` appears in every prediction row. Rolling back to a previous version must be **one command**, and you must demonstrate it working on day 4. [MLflow](https://mlflow.org/docs/latest/index.html) is the standard tool; a versioned directory plus a pointer file is also acceptable if you document it. What is not acceptable is a model file that gets overwritten in place.

**6. Dashboard.** React, as in GSH. Per-product sentiment over time, aspect breakdown, drill-down to individual reviews. Show `model_version` on screen — when a number looks wrong, the first question is always which model produced it.

**7. Alerting.** Flag a product when its negative-sentiment rate over the last N reviews exceeds a threshold. Reuse your GSH Aiogram code. **Include the flood-control delay from the start** — you already solved this once in `fix(alerting): add delay to prevent Telegram flood control`.

**8. Tests. This is the part you have never done.** Target 60% line coverage on non-UI Python. Specifically: contract validation tests (malformed input rejected), an integration test that runs ingest → score → store against the stubs, and a test that the rollback command actually rolls back. Use [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) and [httpx](https://www.python-httpx.org/) for the service calls.

### Deliverables

- [ ] CI green from day 1, branch protection on
- [ ] Shared contracts package, frozen after day 1
- [ ] Ingest, storage, both service stubs
- [ ] Model registry with demonstrated one-command rollback
- [ ] Dashboard and alerting
- [ ] ≥60% test coverage on non-UI Python, reported by CI

### Acceptance criteria

- `git log --author=<you>` shows zero commits inside `sentiment-svc` or `aspect-svc`.
- p95 latency under 300ms for a batch of 32 reviews, measured and recorded.
- Rollback demonstrated live during the day-7 demo.
- Coverage number is printed by CI, not claimed in a README.

### Pitfalls

- Rebuilding the full GSH stack because you have the code. You do not need Redis Streams or TimescaleDB here.
- Fixing the ML services when they break on day 5. File an issue. Wait.
- Leaving tests to day 6. They will not get written.
- One giant PR at the end of the week. Cap at 400 lines, same as everyone.

---

## 8. Frozen contracts

Agreed and merged day 1. Changes after that require all three to sign off.

```python
# shared/contracts.py
from typing import Literal
from pydantic import BaseModel, Field

Sentiment = Literal["negative", "neutral", "positive"]
Aspect = Literal["delivery", "quality", "price", "seller", "packaging", "other"]

class ReviewIn(BaseModel):
    id: str
    text: str = Field(min_length=1, max_length=5000)

class ScoreRequest(BaseModel):
    reviews: list[ReviewIn] = Field(min_length=1, max_length=64)

class SentimentResult(BaseModel):
    id: str
    label: Sentiment
    confidence: float = Field(ge=0.0, le=1.0)

class SentimentResponse(BaseModel):
    results: list[SentimentResult]
    model_version: str

class AspectHit(BaseModel):
    aspect: Aspect
    polarity: Sentiment
    confidence: float = Field(ge=0.0, le=1.0)

class AspectResult(BaseModel):
    id: str
    aspects: list[AspectHit]

class AspectResponse(BaseModel):
    results: list[AspectResult]
    model_version: str
```

Every service exposes:

| Endpoint | Purpose |
|---|---|
| `POST /v1/score` | The main call. Batch of up to 64. |
| `GET /health` | Liveness. Returns 200 only when a model is loaded. |
| `GET /model-info` | `model_version`, training date, headline metric |

`model_version` is mandatory in every response and is stored with every prediction.

---

## 9. Schedule

| Day | Hayotbek | Biloliddin | Bekmurod |
|---|---|---|---|
| **1** | Data split committed. TF-IDF baseline number posted. | Taxonomy agreed. 100 reviews read. | CI green, contracts merged, branch protection on. |
| **2** | Text normaliser + tests. First transformer run. | 300-row gold set hand-labelled. | Ingest + storage + stubs. Dashboard started. |
| **3** | Learning curve sweep started. | Self-agreement kappa. LLM labelling at scale. | Dashboard on stubs. First real tests. |
| **4** | Model selected. Error analysis written. | Baselines measured. First classifier trained. | Model registry + rollback demonstrated. |
| **5** | Service built behind the contract. Handover. | Service built behind the contract. Handover. | Real services wired in, stubs removed. |
| **6** | Test-set evaluation. `EVALUATION.md`. | Test-set evaluation. `EVALUATION.md`. | Alerting. Coverage to 60%. |
| **7** | Demo: present your own number. | Demo: present your own number. | Demo: latency, coverage, live rollback. |

Days 5–7 look light on new modelling. That is deliberate — integration always overruns, and GSH shows this team hits its hardening problems late.

---

## 10. Definition of done

The project is done when all of these are true:

- [ ] CI is green on `main` and has been green since day 1
- [ ] Test coverage on non-UI Python is ≥60% and printed by CI
- [ ] Both `EVALUATION.md` files exist, each with a baseline comparison
- [ ] The 300-row gold set is committed and was never trained on
- [ ] Test-set numbers were computed exactly once, on day 6
- [ ] A model rollback has been demonstrated live
- [ ] No commits from Bekmurod inside either ML service
- [ ] No pull request in the repo exceeds 400 changed lines
- [ ] Every model artifact has a version, and every prediction row records which version produced it

---

## 11. Day-7 demo format

Fifteen minutes each. Each person presents **their own metric**, not the product.

- **Hayotbek:** baseline vs shipped model, the learning curve, and the three most interesting misclassifications with an explanation of each.
- **Biloliddin:** per-aspect F1, self-agreement kappa, LLM-vs-gold agreement rate, and which aspect is hardest and why.
- **Bekmurod:** p95 latency, coverage, and a live rollback from the current model to the previous one.

Then one question to the whole team: **what would you need to double the numbers?** The answer is almost never "a bigger model," and getting them to that conclusion themselves is the point of the week.

---

## 12. If it slips

Cut in this order:

1. Alerting
2. Dashboard down to a plain table
3. Aspect taxonomy from six classes to three (`delivery`, `quality`, `other`)
4. Transformer fine-tuning entirely — ship the TF-IDF baseline

**Never cut:** the baseline comparison, the gold set, the test-set discipline, or CI. Those four are the entire reason for running this project. A team that ships TF-IDF with a proper evaluation has succeeded. A team that ships a transformer with no baseline has not.

---

## Appendix — links

**Data**
- [risqaliyevds/uzbek-sentiment-analysis](https://huggingface.co/datasets/risqaliyevds/uzbek-sentiment-analysis) — 352k Uzum reviews, MIT
- [Sanatbek/aspect-based-sentiment-analysis-uzbek](https://huggingface.co/datasets/Sanatbek/aspect-based-sentiment-analysis-uzbek) — 6.18k aspect rows
- [murodbek/uz-text-classification](https://huggingface.co/datasets/murodbek/uz-text-classification) — 512k news articles, 15 categories
- [Zenodo mirror](https://zenodo.org/records/7677431)

**Reference results**
- [sssplash6/uzbek-sentiment-analysis](https://github.com/sssplash6/uzbek-sentiment-analysis) — TF-IDF beats transformers at low data. Read day 1.
- [Text classification dataset and analysis for Uzbek (arXiv 2302.14494)](https://arxiv.org/abs/2302.14494)
- [BERTbek: A Pretrained Language Model for Uzbek](https://aclanthology.org/2024.sigul-1.5.pdf)

**Models**
- [tahrirchi/tahrirchi-bert-small](https://huggingface.co/tahrirchi/tahrirchi-bert-small) · [tahrirchi-bert-base](https://huggingface.co/tahrirchi/tahrirchi-bert-base)
- [xlm-roberta-base](https://huggingface.co/FacebookAI/xlm-roberta-base) · [distilbert-base-multilingual-cased](https://huggingface.co/distilbert/distilbert-base-multilingual-cased)

**Tooling**
- [HF Datasets](https://huggingface.co/docs/datasets/) · [Transformers Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) · [Sequence classification guide](https://huggingface.co/docs/transformers/tasks/sequence_classification)
- [scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) · [classification_report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html) · [cohen_kappa_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)
- [Label Studio](https://labelstud.io/) · [MLflow](https://mlflow.org/docs/latest/index.html)
- [FastAPI](https://fastapi.tiangolo.com/) · [Pydantic](https://docs.pydantic.dev/latest/) · [pytest](https://docs.pytest.org/) · [ruff](https://docs.astral.sh/ruff/) · [GitHub Actions](https://docs.github.com/en/actions/writing-workflows/quickstart)
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

**Compute** — [Google Colab](https://colab.research.google.com/) or [Kaggle Notebooks](https://www.kaggle.com/code) free T4 tiers are sufficient for `tahrirchi-bert-small`. Cache the tokenised dataset once so reruns are fast.
