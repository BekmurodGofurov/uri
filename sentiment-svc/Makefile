# sentiment-svc/Makefile
# One-command reproducible training pipeline.
#
# Usage:
#   make train          — full pipeline: download → split → train → evaluate
#   make train-tfidf    — train only (assumes data/ already exists)
#   make evaluate       — evaluate the shipped model on test set
#   make test           — run the unit/API test suite
#   make clean          — remove generated data and model artifacts
#
# Requirements: pip install -r requirements.txt
# Run from inside sentiment-svc/ OR from repo root as: make -C sentiment-svc <target>

PYTHON := python

DATA_DIR   := data
MODEL_DIR  := models
LABELLED   := $(DATA_DIR)/labelled.csv
TRAIN_CSV  := $(DATA_DIR)/train.csv
VAL_CSV    := $(DATA_DIR)/val.csv
TEST_CSV   := $(DATA_DIR)/test.csv
MODEL_PATH := $(MODEL_DIR)/tfidf_v1.joblib

.PHONY: train train-tfidf evaluate test clean

## Full pipeline: download → label → split → train → evaluate
train: $(LABELLED) $(TRAIN_CSV) $(MODEL_PATH)
	$(PYTHON) training/evaluate.py \
		--model $(MODEL_PATH) \
		--test  $(TEST_CSV) \
		--type  tfidf

## Step 1: Download HuggingFace dataset and map ratings to labels
$(LABELLED):
	$(PYTHON) training/prepare_data.py

## Step 2: Deterministic hash-based split (70/15/15)
$(TRAIN_CSV): $(LABELLED)
	$(PYTHON) training/split_data.py \
		--input  $(LABELLED) \
		--output $(DATA_DIR)/

## Step 3: Train TF-IDF + Logistic Regression
$(MODEL_PATH): $(TRAIN_CSV)
	@mkdir -p $(MODEL_DIR)
	$(PYTHON) training/train_tfidf.py \
		--train $(TRAIN_CSV) \
		--val   $(VAL_CSV) \
		--out   $(MODEL_PATH)

## Train only (skip download/split if data/ already exists)
train-tfidf: $(TRAIN_CSV)
	@mkdir -p $(MODEL_DIR)
	$(PYTHON) training/train_tfidf.py \
		--train $(TRAIN_CSV) \
		--val   $(VAL_CSV) \
		--out   $(MODEL_PATH)

## Evaluate shipped model on held-out test set
evaluate: $(MODEL_PATH) $(TEST_CSV)
	$(PYTHON) training/evaluate.py \
		--model $(MODEL_PATH) \
		--test  $(TEST_CSV) \
		--type  tfidf

## Run the test suite (unit + API tests, no data files required)
test:
	pytest tests/ -v --tb=short

## Remove generated artefacts (does NOT delete model registry entries)
clean:
	rm -rf $(DATA_DIR)/labelled.csv \
	        $(DATA_DIR)/train.csv \
	        $(DATA_DIR)/val.csv \
	        $(DATA_DIR)/test.csv \
	        $(DATA_DIR)/split_manifest.json \
	        evaluation_result.json
