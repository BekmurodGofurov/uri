#!/usr/bin/env python3
"""
fast_postgres_ingest.py
Loads ALL 352,151 reviews into Docker PostgreSQL with a strict limit of
MAX 60 REVIEWS PER PRODUCT. No data is dropped. Every product has between 1 and 60 reviews.
"""

import datetime
import json
import os
import random
import time
from collections import defaultdict

import psycopg
from dotenv import load_dotenv

load_dotenv()

MAX_REVIEWS_PER_PRODUCT = 60

ARROW_PATH = os.path.expanduser(
    "~/.cache/huggingface/datasets/risqaliyevds___uzbek-sentiment-analysis/"
    "default/0.0.0/fedc41d40ece1062e9ad026a35a065fb07ef08ba/uzbek-sentiment-analysis-train.arrow"
)
MODEL_PATH = os.path.abspath("sentiment-svc/models/tfidf_v1.joblib")
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL must be set in .env file")
if "+psycopg" in DB_URL:
    DB_URL = DB_URL.replace("+psycopg", "")


CATEGORIES = {
    "food": {
        "name": "Coffee and Tea Products",
        "category": "Food",
        "keywords": [
            "kofe",
            "qahva",
            "kofeni",
            "espresso",
            "shokolad",
            "shirinlik",
            "konfet",
            "mazali",
            "choy",
            "choyni",
            "kok choy",
            "qora choy",
            "damlama",
            "giyoh",
        ],
        "templates": [
            "Tchibo Gold Selection Kofe 100g",
            "Tabiiy Tog' Ko'k Choyi va Giyohlar",
            "Premium Qora Choy Granulalari 250g",
            "Eritiladigan Qahva Sublimatsiyalangan",
            "Shokoladli Konfetlar To'plami",
        ],
    },
    "jacket": {
        "name": "Winter and Autumn Outerwear",
        "category": "Clothing",
        "keywords": [
            "kurtka",
            "kurtkani",
            "kurtkasi",
            "kurtkalar",
            "palto",
            "vetrovka",
            "kastyum",
            "jilet",
            "kapshon",
        ],
        "templates": [
            "Erkaklar Qishki Qalin Issiq Kurtkasi",
            "Kuzgi Klassik Erkaklar Paltosi",
            "Shamolga Chidamli Sport Vetrovka",
            "Kapshonli Qalin Qishki Parka",
            "Erkaklar Junli Issiq Jileti",
        ],
    },
    "case": {
        "name": "Silicone Cases and Accessories",
        "category": "Electronics",
        "keywords": [
            "chexol",
            "chixol",
            "chexolni",
            "chexoli",
            "steklo",
            "shisha",
            "oyna",
            "silikon",
            "kamerali",
            "redmi",
            "samsung",
            "iphone",
            "fleshka",
            "xotira",
            "shnur",
            "kabel",
            "zaryadnik",
            "zaryad",
        ],
        "templates": [
            "Samsung Galaxy A54 Silikon G'ilof",
            "iPhone 13 Pro Max Shaffof Chexol",
            "Redmi Note 12 Zirhli G'ilof",
            "20W Tezkor Type-C Zaryadlovchi Kabel",
            "Keramik Himoya Oynasi 9D",
            "USB Fleshka 64GB Yuqori Tezlik",
            "Zaryadlovchi Magnitli Kabel 3in1",
        ],
    },
    "audio": {
        "name": "Wireless Earphones and Audio",
        "category": "Electronics",
        "keywords": [
            "naushnik",
            "naushnikni",
            "naushniki",
            "naushniklar",
            "quloqchin",
            "ovoz",
            "bas",
            "bluetooth",
            "blutuz",
            "keys",
            "mikrofon",
        ],
        "templates": [
            "Simsiz Bluetooth Naushnik Pro",
            "TWS Quloqchin Zaryadlash Qutisi bilan",
            "Sport uchun Suvga Chidamli Naushnik",
            "Simli Stereo Quloqchin Mikrofon bilan",
            "Mini Portativ Bluetooth Kolonka",
        ],
    },
    "skincare": {
        "name": "Facial and Skin Care",
        "category": "Beauty & Personal Care",
        "keywords": [
            "krem",
            "kremni",
            "zardob",
            "yuzga",
            "shampun",
            "maska",
            "ajin",
            "namlantiruvchi",
        ],
        "templates": [
            "Organik Yuz Kremi va Zardobi",
            "Gialuron Kislotali Namlantiruvchi Zardob",
            "Ajinlarga Qarshi Kollagenli Tungi Krem",
            "Sulfatsiz Tabiiy Soch Shampuni",
            "Tiklovchi Teri Maskasi To'plami",
        ],
    },
    "cosmetics": {
        "name": "Lipstick and Makeup Products",
        "category": "Beauty & Personal Care",
        "keywords": [
            "pomada",
            "pamada",
            "pomadani",
            "boyoq",
            "buyog",
            "labga",
            "lab buyog",
            "upal",
            "kosmetika",
            "tonal",
            "lab boyogi",
        ],
        "templates": [
            "Matoviy Lab Bo'yog'i To'plami 6 talik",
            "Velvet Suyuq Pomada Uzoq Saqlanuvchi",
            "Namlantiruvchi Gigiyenik Lab Balzami",
            "Tonal Krem Matlashtiruvchi Effekt",
            "Pardoz uchun Yuz Upasi",
        ],
    },
    "shoes": {
        "name": "Shoes and Sneakers",
        "category": "Footwear",
        "keywords": [
            "krossovka",
            "krasovka",
            "krosovka",
            "krasovki",
            "krosovki",
            "poyabzal",
            "oyoq kiyim",
            "keta",
            "tufli",
            "tagcharmi",
            "etik",
            "razmer",
            "razmeri",
            "oyoqqa",
        ],
        "templates": [
            "Erkaklar Kundalik Sport Krossovkasi",
            "Ayollar Yugurish Krossovkasi Yengil",
            "Kuzgi Erkaklar Qulay Mokasini",
            "Qishki Issiq Mo'ynali Erkaklar Botinkasi",
            "Klassik Teri Tufli",
        ],
    },
    "gadget": {
        "name": "Smart Gadgets and Auto Accessories",
        "category": "Electronics",
        "keywords": [
            "smartwatch",
            "braslet",
            "puls",
            "qadam",
            "soatni",
            "soat",
            "avtomobil",
            "salon",
            "derjatel",
            "tutqich",
            "polik",
            "magnitola",
            "pult",
            "pulti",
            "akkumulyator",
        ],
        "templates": [
            "Smart Soat va Fitnes Braslet Ultra",
            "Avtomobil uchun Telefon Tutqich (Holder)",
            "Avto Salon Xushbo'ylantiruvchi Aromatizator",
            "Avto Zaryadlovchi 2xUSB Tezkor",
            "Fitnes Braslet Yurak Urishi Datchigi bilan",
        ],
    },
    "general": {
        "name": "Household and Universal Products",
        "category": "Household",
        "keywords": [],
        "templates": [
            "Bambukli Hammom Sochiqlari To'plami",
            "Ikki Kishilik Paxta Choyshablar To'plami",
            "Granit Qoplamali Qovurish Tovasi 26sm",
            "Oshxona Pichoqlari Professional To'plami",
            "Elektr Choynak Zanglamas Po'lat 2L",
            "Ergonomik Ortopedik Uyqu Yostig'i",
            "Ultrasonik Havo Namlagich va Diffuzor",
            "Sensorli LED Stol Chirog'i",
            "Ko'p Funksiyali Oshxona Qirg'ichi",
            "Kiyimlar uchun Vakuumli Qoplar To'plami",
            "Termos Zanglamas Po'lat 1000ml",
            "Avtomatik Tish Pastasi Dispenseri",
            "Silikon Oshxona Anjomlari To'plami",
            "Kiyimlar uchun Bug'li Dazmol",
            "Boshqaruv Pultli LED Tungi Chiroq",
        ],
    },
}

RATING_MAP = {
    "excellent": 5,
    "good": 4,
    "fair": 3,
    "poor": 2,
    "very poor": 1,
}

ASPECT_KEYWORDS = {
    "delivery": ("yetkazib", "kuryer", "yetkazish", "kechik", "keldi"),
    "quality": ("sifat", "ishlamay", "buzil", "mustahkam", "yaxshi", "brak"),
    "price": ("narx", "qimmat", "arzon", "chegirma", "aksiy"),
    "seller": ("sotuvchi", "javob ber", "kafolat", "dokon"),
    "packaging": ("qadoq", "quti", "yoril", "ezil", "upakovka"),
}


def main():
    print(f"Connecting to PostgreSQL at {DB_URL}...")
    t0 = time.time()
    conn = psycopg.connect(DB_URL, autocommit=False)
    cur = conn.cursor()

    # Verify tables
    cur.execute("""
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
    """)
    conn.commit()

    print("Cleaning existing rows in PostgreSQL...")
    cur.execute("TRUNCATE TABLE predictions, reviews, products RESTART IDENTITY CASCADE;")
    conn.commit()

    # Load dataset (Arrow cache or Hugging Face)
    if os.path.exists(ARROW_PATH):
        print(f"Loading arrow dataset from {ARROW_PATH}...")
        import pyarrow.ipc as ipc

        with open(ARROW_PATH, "rb") as f:
            table = ipc.RecordBatchStreamReader(f).read_all()
        n_rows = table.num_rows
        raw_texts = [str(t) for t in table["normalized_review_text"]]
        raw_ratings = [str(r) for r in table["rating"]]
    else:
        print(
            "Arrow cache not found. Downloading risqaliyevds/uzbek-sentiment-analysis "
            "from Hugging Face..."
        )
        from datasets import load_dataset

        ds = load_dataset("risqaliyevds/uzbek-sentiment-analysis")
        split_data = ds["train"]
        n_rows = len(split_data)
        raw_texts = [str(t) for t in split_data["normalized_review_text"]]
        raw_ratings = [str(r) for r in split_data["rating"]]

    print(f"Loaded all {n_rows:,} reviews successfully.")

    # Bucket reviews by category
    print("Bucketing reviews by semantic category...")
    category_buckets = defaultdict(list)
    for i in range(n_rows):
        low = raw_texts[i].lower()
        cat_key = "general"
        for k in ["food", "jacket", "case", "audio", "skincare", "cosmetics", "shoes", "gadget"]:
            if any(kw in low for kw in CATEGORIES[k]["keywords"]):
                cat_key = k
                break
        category_buckets[cat_key].append(i)

    for cat_name, bucket in category_buckets.items():
        print(f"  {cat_name}: {len(bucket):,} reviews")

    # Partition each category into products of at most 60 reviews
    print("\nCreating products (max 60 reviews per product)...")
    products = []
    review_product_map = {}

    order = [
        "food",
        "jacket",
        "case",
        "audio",
        "skincare",
        "cosmetics",
        "shoes",
        "gadget",
        "general",
    ]
    now_dt = datetime.datetime.now(datetime.UTC)

    for cat_key in order:
        idxs = category_buckets[cat_key]
        templates = CATEGORIES[cat_key]["templates"]
        category_name = CATEGORIES[cat_key]["category"]

        for prod_sub_idx, chunk_start in enumerate(range(0, len(idxs), MAX_REVIEWS_PER_PRODUCT)):
            chunk = idxs[chunk_start : chunk_start + MAX_REVIEWS_PER_PRODUCT]
            tmpl = templates[prod_sub_idx % len(templates)]
            variant_num = (prod_sub_idx // len(templates)) + 1

            prod_id = f"prod_{len(products) + 1}"
            title = f"{tmpl} (Model #{variant_num})" if variant_num > 1 else tmpl

            products.append((prod_id, title, category_name, now_dt))
            for r_idx in chunk:
                review_product_map[r_idx] = prod_id

    print(f"Total products created: {len(products):,}")
    print(f"Total reviews assigned: {len(review_product_map):,} (100% of data)")

    # Insert products using COPY
    print("Inserting products into PostgreSQL...")
    with cur.copy("COPY products (id, title, category, created_at) FROM STDIN") as copy:
        for p in products:
            copy.write_row(p)
    conn.commit()
    print(f"Inserted {len(products):,} products.")

    # Run sentiment pipeline in bulk
    print("Generating sentiment predictions in bulk...")
    t_sent = time.time()
    has_ml = False
    preds = []
    probs = []
    class_indices = {}

    if os.path.exists(MODEL_PATH):
        try:
            import joblib

            pipeline = joblib.load(MODEL_PATH)
            classes = list(pipeline.classes_)
            class_indices = {c: i for i, c in enumerate(classes)}
            preds = pipeline.predict(raw_texts)
            probs = pipeline.predict_proba(raw_texts)
            has_ml = True
            print(f"Sentiment predictions generated via ML model in {time.time() - t_sent:.2f}s.")
        except Exception as err:
            print(f"ML model loading failed ({err}). Falling back to rating-based sentiment.")
    else:
        print("Model file not found. Falling back to rating-based sentiment.")

    # Format review rows and prediction rows
    print("Formatting review & prediction rows...")
    t_prep = time.time()
    base_timestamp = time.time() - (120 * 86400)
    time_increment = (120 * 86400) / max(n_rows, 1)

    reviews_rows = []
    predictions_rows = []

    for i in range(n_rows):
        text = raw_texts[i]
        rating_val = RATING_MAP.get(raw_ratings[i], 5)
        prod_id = review_product_map[i]
        rev_id = f"uzum_{i + 1:06d}"

        row_time = base_timestamp + (i * time_increment) + random.randint(-1800, 1800)
        dt = datetime.datetime.fromtimestamp(row_time, datetime.UTC)

        reviews_rows.append((rev_id, prod_id, text, rating_val, dt))

        if has_ml:
            sent_label = preds[i]
            conf = float(probs[i][class_indices[sent_label]])
        else:
            if rating_val >= 4:
                sent_label = "positive"
                conf = 0.85
            elif rating_val <= 2:
                sent_label = "negative"
                conf = 0.80
            else:
                sent_label = "neutral"
                conf = 0.70

        lowered = text.lower()
        aspect_hits = []
        if rating_val >= 4:
            polarity_val = "positive"
        elif rating_val <= 2:
            polarity_val = "negative"
        else:
            polarity_val = "neutral"

        for asp, kws in ASPECT_KEYWORDS.items():
            if any(kw in lowered for kw in kws):
                aspect_hits.append({"aspect": asp, "polarity": polarity_val, "confidence": 0.55})

        if not aspect_hits:
            aspect_hits.append({"aspect": "other", "polarity": polarity_val, "confidence": 0.30})

        predictions_rows.append(
            (
                rev_id,
                sent_label,
                round(conf, 4),
                json.dumps(aspect_hits),
                "sentiment-v1;aspect-stub-v0.1",
                dt,
            )
        )

    print(f"Data formatted in {time.time() - t_prep:.2f}s.")

    # Streaming COPY for reviews
    print("Streaming COPY into PostgreSQL 'reviews' table...")
    t_copy = time.time()
    with cur.copy("COPY reviews (id, product_id, text, rating, created_at) FROM STDIN") as copy:
        for row in reviews_rows:
            copy.write_row(row)
    conn.commit()
    print(f"Finished COPY for {len(reviews_rows):,} reviews in {time.time() - t_copy:.2f}s.")

    # Streaming COPY for predictions
    print("Streaming COPY into PostgreSQL 'predictions' table...")
    t_copy_pred = time.time()
    copy_pred_sql = (
        "COPY predictions (review_id, sentiment_label, sentiment_confidence, "
        "aspects, model_version, created_at) FROM STDIN"
    )
    with cur.copy(copy_pred_sql) as copy:
        for row in predictions_rows:
            copy.write_row(row)
    conn.commit()
    elapsed_pred = time.time() - t_copy_pred
    print(f"Finished COPY for {len(predictions_rows):,} predictions in {elapsed_pred:.2f}s.")

    # Create Indexes
    print("Creating/verifying PostgreSQL indexes...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_predictions_review_id ON predictions(review_id);")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_predictions_model_version ON predictions(model_version);"
    )
    conn.commit()

    conn.close()
    elapsed_total = time.time() - t0
    print(
        f"\nSUCCESS: All {n_rows:,} reviews ingested into PostgreSQL across "
        f"{len(products):,} products (max {MAX_REVIEWS_PER_PRODUCT} reviews per product) "
        f"in {elapsed_total:.2f}s total!"
    )


if __name__ == "__main__":
    main()
