# Uzum Review Intelligence (URI) — Dashboard UI

Analytical dashboard for customer review sentiment analysis and aspect extraction.
Fully integrated with the FastAPI Gateway API (`gateway/api/app.py`).

---

## Features

1. **Product Catalog (Product List):**
   - Average rating for each product (1.0 - 5.0).
   - Review counts and volume dynamics.
   - Positive, neutral, and negative sentiment ratio progress bars.
   - Search (by product title or ID), category filtering, and sorting.

2. **Dynamic Visualizations (Sentiment Over Time):**
   - Customer sentiment trends over time (Recharts interactive area chart).
   - Daily breakdown of positive, neutral, and negative review counts.

3. **Aspect Breakdown:**
   - **Quality**
   - **Delivery**
   - **Price**
   - **Seller**
   - **Packaging**
   - Granular satisfaction percentages and counts for each aspect.

4. **Reviews Drill-Down:**
   - Authentic customer review texts.
   - Star ratings and publication dates.
   - Model-predicted sentiment label and confidence score (`sentiment_confidence`).
   - Identified aspect tags with polarity indicators.

5. **Mandatory Requirement — Active Model Version (`model_version`):**
   - Active model version is displayed prominently in the top navigation bar.
   - Product detail headers display all model versions that processed reviews for the selected item.
   - **Every review card** displays the exact model version that generated its predictions with an identifiable badge.

6. **Live AI Scorer Modal:**
   - Test any review text interactively through the Gateway API (`POST /api/score/preview`) and view real-time ML predictions.

---

## Getting Started

### 1. Start Backend Services (via Docker):
Backend microservices (`postgres`, `sentiment-svc`, `aspect-svc`, `gateway`) are started via Docker:
```bash
# In the repository root directory:
docker compose up -d
```
The Backend Gateway runs at `http://localhost:8000` (or the configured `GATEWAY_PORT`).

---

### 2. Dashboard Environment Configuration (`.env`):
The Dashboard sends all API requests to the `VITE_API_URL` configured in `dashboard/.env`.

Check or create the `dashboard/.env` file:
```bash
cd dashboard
cp .env.example .env
```

Inside `dashboard/.env`:
```env
# Backend Gateway API URL
VITE_API_URL=http://localhost:8000
FRONTEND_PORT=3000
```
> **Important:** If `VITE_API_URL` is not provided, the application will display a connection warning and cannot reach the API.

---

### 3. Manual Build and Run:

The dashboard is run directly on the host or inside a container:

#### A) Development Mode (Hot Reload):
```bash
cd dashboard
npm install       # First time only
npm run dev       # Start dev server
```
Open in browser: [http://localhost:3000](http://localhost:3000)

#### B) Production Mode (Build & Preview):
```bash
cd dashboard
npm run build     # Compile TypeScript and bundle via Vite into dist/
npm run preview   # Serve production build
```
Open in browser: [http://localhost:3000](http://localhost:3000)
