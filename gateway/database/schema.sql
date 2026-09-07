-- Schema for Uzum Review Intelligence (URI)
-- Day 2: Ingest and storage

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(128) PRIMARY KEY,
    title TEXT,
    category VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
    id VARCHAR(128) PRIMARY KEY,
    product_id VARCHAR(128) REFERENCES products(id) ON DELETE SET NULL,
    text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    review_id VARCHAR(128) NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    sentiment_label VARCHAR(32) NOT NULL,
    sentiment_confidence REAL NOT NULL,
    aspects JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_version VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_predictions_review_id ON predictions(review_id);
CREATE INDEX IF NOT EXISTS idx_predictions_model_version ON predictions(model_version);
