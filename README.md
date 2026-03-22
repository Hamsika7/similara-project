# SIMILARA
### Scalable Multimodal Framework for Retail Product Matching

An AI-powered system that automatically detects and removes duplicate product listings from retail catalogs by combining fuzzy text matching, semantic embeddings, and visual similarity.

---

## Problem

Large retail platforms receive the same product from hundreds of suppliers under slightly different names, descriptions, or images — causing catalog duplication, mismatched inventory, and inaccurate pricing. Manual deduplication is slow and impossible to scale.

**Example:** `"Tata Salt 1kg"`, `"TATA SALT 1 KG"`, and `"Tata Iodized Salt 1000g"` are automatically identified as the same product without any human review.

---

## How It Works

SIMILARA fuses three complementary signals into a single similarity score:

| Signal | Model | What It Captures |
|---|---|---|
| Fuzzy Text | RapidFuzz `token_sort_ratio` | Word reordering in product names |
| Semantic Text | SBERT `all-MiniLM-L6-v2` | Meaning, not just keywords (384-dim) |
| Visual | CLIP `ViT-B/32` | Product appearance across different photos (512-dim) |

**Fusion formula:** `score = α·fuzzy + β·text + γ·image`

Weights (α, β, γ) and the decision threshold are tuned via grid search on labeled product pairs to maximize F1 score.

---

## Architecture

```
Raw Input (CSV / Image URL)
        │
        ▼
  Preprocessing
  (text clean · image resize)
        │
        ├──────────────┬──────────────┐
        ▼              ▼              ▼
   RapidFuzz         SBERT           CLIP
   (fuzzy)         (384-dim)       (512-dim)
        │              │              │
        └──────────────┴──────────────┘
                       │
                  Score Fusion
              α·fuzzy + β·text + γ·image
                       │
              Threshold Decision
              → similarity score + is_duplicate
                       │
             ┌─────────┴──────────┐
             ▼                    ▼
         FastAPI               PostgreSQL
    /match · /bulk-match    products · embeddings
    /history                match_results
             │
             ▼
        Streamlit UI
```

**Training vs. Serving:** SBERT and CLIP embeddings are generated on Google Colab (GPU) and saved as `.pkl` files via joblib. The FastAPI server loads precomputed embeddings from PostgreSQL at query time — no re-embedding for existing products.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy |
| AI / ML | Sentence-Transformers, CLIP, RapidFuzz, scikit-learn |
| Data | Pandas, NumPy, Pillow |
| Serialization | joblib |

---

## Evaluation

Evaluated on **83 manually labeled product pairs** from the Flipkart dataset.

```
=== EVALUATION ON 83 PAIRS ===

              precision    recall  f1-score   support

Not Duplicate     0.98      0.80      0.88        55
    Duplicate     0.71      0.96      0.82        28

     accuracy                         0.86        83
    macro avg     0.84      0.88      0.85        83
 weighted avg     0.89      0.86      0.86        83
```

**Key takeaway:** 96% recall on duplicates — the system almost never misses a real duplicate. The conservative threshold is intentional; for catalog cleanup tasks, missing a duplicate is costlier than a false positive.

---

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 14+
- Google Colab (for embedding generation)

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/similara.git
cd similara
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/similara_db
```

**5. Generate embeddings on Google Colab**

Run the four notebooks in order:
```
Notebook_A_Data.ipynb        → EDA, preprocessing, cleaned_products.csv
Notebook_B_Fuzzy.ipynb       → RapidFuzz scoring, threshold exploration
Notebook_C_Embeddings.ipynb  → SBERT + CLIP embeddings → .pkl files
Notebook_D_Fusion_Eval.ipynb → Grid search, evaluation, fusion_weights.pkl
```

Download all outputs from Colab and place them in `similara/models/`.

**6. Run the application**

Terminal 1 — Start the API:
```bash
uvicorn api.main:app --reload --port 8000
```

Terminal 2 — Start the UI:
```bash
streamlit run ui/app.py
```

Open `http://localhost:8501`

---

## API Endpoints

Interactive docs at `http://localhost:8000/docs` — built with FastAPI (OAS 3.1)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health/` | Health check — verify API is running |
| `POST` | `/match/` | Compare a single product pair; returns similarity score + duplicate flag |
| `POST` | `/bulk/` | Bulk match — upload catalog CSV, returns deduplicated results |
| `GET` | `/history/` | Fetch past match results from the database |
| `GET` | `/` | Root — API info and version |
| `DELETE` | `/admin/clear-image-cache` | Clear cached image embeddings (admin only) |

---

## Usage

**Demo credentials:**
- Admin: `admin` / `admin123` — full pipeline access
- Guest — browse and view catalog only

**Workflow:**
1. **Upload** — Drop a raw CSV/Excel product catalog
2. **Browse & Match** — Select any product to inspect similar listings with per-signal score breakdown
3. **Clean & Visualize** — Review duplicate clusters with category and confidence charts
4. **Catalog** — Browse the deduplicated results; export final CSV

---

## Project Structure

```
similara/
├── models/                    ← Colab outputs (embeddings, weights, threshold)
├── api/
│   ├── main.py
│   ├── dependencies.py
│   ├── routes/                ← match.py · bulk.py · history.py
│   ├── schemas/product.py
│   └── services/              ← fuzzy_service · embedding_service · fusion_service
├── db/
│   ├── connection.py
│   ├── models.py
│   └── crud.py
├── ui/
│   └── app.py
├── data/
│   └── sample_catalog.csv
├── .env                       ← not committed
├── requirements.txt
└── README.md
```

---

## Dataset

**Flipkart Products Dataset** (20,000 products). Chosen for accessible image CDN URLs, dedicated brand and specification columns, deep category hierarchy, and natural product variant distribution — well suited for deduplication benchmarking.

Preprocessing applied: image URL extraction from list strings (`ast.literal_eval`), Ruby-style spec hash parsing (regex), null normalization, and unit normalization (`1KG → 1 kg`).

---

## Future Enhancements

- **Scalability via Vector Database Integration** — Integrate FAISS for Approximate Nearest Neighbor (ANN) searches, enabling the system to handle millions of product listings with sub-second query latency.
- **Intelligent Fusion with ML Classifiers** — Replace the hardcoded threshold with a trained XGBoost classifier to dynamically optimize textual and visual score weights, reducing false positives.
- **Deepened Multimodal Intelligence** — Strengthen CLIP image embeddings to ensure reliable product identification even when descriptions are sparse or missing.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributions

Contributions are welcome. Please fork the repository and submit a pull request with your enhancements.

---

## Contact

Hamsika S — [hamsikassnn2004@gmail.com](mailto:hamsikassnn2004@gmail.com)

---

## Acknowledgments

- Flipkart Products Dataset (Kaggle)
- Sentence-Transformers (`all-MiniLM-L6-v2`) — SBERT by UKP Lab
- OpenAI CLIP (`ViT-B/32`) via Hugging Face
- RapidFuzz — C++ powered fuzzy string matching
- Streamlit — rapid ML UI framework
- FastAPI — modern async Python web framework
