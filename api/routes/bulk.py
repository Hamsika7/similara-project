from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from api.services.fuzzy_service import get_fuzzy_score
from api.services.embedding_service import (
    get_text_embeddings_batch,
    cosine_sim,
    encode_image_or_text_fallback,
)
from api.services.fusion_service import fuse_scores
from db.connection import get_db
from db.crud import save_match_result, get_embeddings_bulk
import pandas as pd
import numpy as np
import io
import uuid
from rapidfuzz import fuzz

router = APIRouter()


def get_confidence(score: float) -> str:
    if score >= 0.90:
        return "high"
    elif score >= 0.70:
        return "medium"
    else:
        return "low"


def build_clusters(duplicates: list) -> list:
    adjacency = {}
    for d in duplicates:
        a = d["product_a"]
        if a not in adjacency:
            adjacency[a] = []
        adjacency[a].append(d)

    clusters = []
    seen     = set()

    for d in duplicates:
        a = d["product_a"]
        if a in seen:
            continue
        seen.add(a)

        group   = adjacency.get(a, [])
        removed = []
        for g in group:
            seen.add(g["product_b"])
            removed.append({
                "name":        g["product_b"],
                "fuzzy_score": round(g["fuzzy_score"] * 100),
                "text_sim":    round(g["text_sim"]    * 100),
                "image_sim":   round(g["image_sim"]   * 100),
                "final_score": round(g["final_score"] * 100),
                "reason":      f"Similarity {round(g['final_score']*100)}%"
            })

        if not removed:
            continue

        avg_score = round(
            sum(r["final_score"] for r in removed) / len(removed)
        )

        clusters.append({
            "id":                f"PROD-{str(uuid.uuid4())[:8].upper()}",
            "name":              a,
            "category":          "Uncategorized",
            "subcategory":       "",
            "duplicates_merged": len(removed),
            "trend_score":       avg_score,
            "price_min":         0,
            "price_max":         0,
            "originals":         removed,
            "avg_similarity":    avg_score,
            "confidence":        get_confidence(avg_score / 100),
            "matches": [
                {"name": r["name"], "score": r["final_score"]}
                for r in removed
            ],
            "fuzzy": round(
                sum(r["fuzzy_score"] for r in removed) / len(removed)
            ),
            "text": round(
                sum(r["text_sim"] for r in removed) / len(removed)
            ),
            "image": round(
                sum(r["image_sim"] for r in removed) / len(removed)
            ),
        })

    return clusters


@router.post("/")
async def bulk_match(file: UploadFile = File(...)):

    # ── DB session setup ───────────────────────────────────
    from db.connection import get_db_session

    db_gen = get_db_session()
    db = next(db_gen)

    try:
        # ── Read CSV ───────────────────────────────────────
        try:
            content = await file.read()
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Could not read file. Must be a valid CSV."
            )

        # Normalize column names: "Product Name" -> "product_name", "Image" -> "image"
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        if "product_name" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing column: product_name. Found: {list(df.columns)}"
            )

        df    = df.fillna("").head(500)
        rows  = df.to_dict("records")
        names = [str(r["product_name"]) for r in rows]
        total = len(rows)
        print(f"[BULK] {total} products received")

        # ── Category counts ───────────────────────────────
        cat_col = next(
            (c for c in ["category", "main_category", "Category",
                         "product_category", "type"]
             if c in df.columns),
            None
        )
        category_counts = (
            df[cat_col].fillna("Unknown").value_counts().head(10).to_dict()
            if cat_col else {"Uncategorized": total}
        )

        # ── STEP 1: Get all text embeddings ───────────────
        # PostgreSQL first → SBERT for new ones → save to PostgreSQL
        print("[BULK] Fetching/computing text embeddings...")
        text_embeddings = get_text_embeddings_batch(names)

        # ── STEP 2: Build normalized matrix for fast cosine
        vectors = np.array([
            text_embeddings[name] for name in names
        ])
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors_norm = vectors / norms

        print("[BULK] Computing cosine similarity matrix...")
        sim_matrix = vectors_norm @ vectors_norm.T  # shape (n, n)

        # ── STEP 3: Read image URLs and get CLIP embeddings for similarity ─
        # Read image URL from CSV (raw value; may be "image_url" or "image" column).
        # Flipkart format: raw value is a stringified list e.g. '["http://img5a.flixcart.com/..."]'
        # We pass raw value to encode_image_or_text_fallback which parses it via _extract_first_image_url.
        image_urls = [str(r.get("image_url") or r.get("image", "")) for r in rows]
        img_cache  = {}
        image_source_counts = {"image": 0, "clip_text": 0, "zero_fallback": 0}

        # Try to load any existing embeddings from PostgreSQL by URL key first
        valid_urls = [u for u in image_urls if u]
        if valid_urls:
            print(f"[BULK] Fetching {len(valid_urls)} image embeddings...")
            img_cache = get_embeddings_bulk(db, valid_urls)
            print(f"[BULK] Found {len(img_cache)} image embeddings in PostgreSQL")

        # For any product without an embedding yet, compute via CLIP (image or fallback)
        items_to_save = []
        for idx, row in enumerate(rows):
            url = image_urls[idx]
            name = names[idx]

            # If we already have an embedding in cache, count as image (from previous run)
            if url and url in img_cache:
                image_source_counts["image"] += 1
                continue

            vec, mode = encode_image_or_text_fallback(url, name)
            key = url or name
            img_cache[key] = vec
            if mode in image_source_counts:
                image_source_counts[mode] += 1

            items_to_save.append(
                {"key": key, "vector": vec, "source": "image"}
            )

        if items_to_save:
            from db.crud import save_embeddings_bulk

            save_embeddings_bulk(db, items_to_save)

        # ── STEP 4: Fuzzy pre-filter + fusion ─────────────
        print("[BULK] Running fuzzy pre-filter + fusion...")
        from api.dependencies import get_models

        models = get_models()
        weights = models.get(
            "fusion_weights",
            {"fuzzy": 0.3, "text": 0.5, "image": 0.2},
        )
        threshold = models.get("threshold", 0.7)
        print(f"[BULK] Using fusion weights={weights}, threshold={threshold}")

        FUZZY_PREFILTER = 0.45
        duplicates      = []

        for i in range(total):
            for j in range(i + 1, total):

                # Fast fuzzy name check first
                name_score = fuzz.token_sort_ratio(
                    names[i].lower(), names[j].lower()
                ) / 100.0

                if name_score < FUZZY_PREFILTER:
                    continue

                # Full fuzzy with description
                fuzzy = get_fuzzy_score(
                    names[i], names[j],
                    str(rows[i].get("description", "")),
                    str(rows[j].get("description", ""))
                )

                # Text similarity from pre-built matrix
                text_sim = float(max(0.0, sim_matrix[i, j]))

                # Check image similarity among this pair (CLIP embeddings, same space for image/text fallback)
                url_a     = image_urls[i]
                url_b     = image_urls[j]
                image_sim = 0.0
                key_a = url_a or names[i]
                key_b = url_b or names[j]
                if key_a in img_cache and key_b in img_cache:
                    image_sim = float(
                        max(0.0, cosine_sim(img_cache[key_a], img_cache[key_b]))
                    )

                # Fusion
                final = round(
                    weights["fuzzy"] * fuzzy +
                    weights["text"]  * text_sim +
                    weights["image"] * image_sim,
                    4
                )

                if final >= threshold:
                    duplicates.append({
                        "product_a":   names[i],
                        "product_b":   names[j],
                        "fuzzy_score": fuzzy,
                        "text_sim":    text_sim,
                        "image_sim":   image_sim,
                        "final_score": final,
                        "confidence":  get_confidence(final)
                    })
                    # save_match_result(
                    #     db,
                    #     names[i], names[j],
                    #     fuzzy, text_sim, image_sim,
                    #     final, True
                    # )

        print(f"[BULK] {len(duplicates)} duplicate pairs found")

        # ── STEP 5: Build output ──────────────────────────
        clusters        = build_clusters(duplicates)
        duplicate_names = {d["product_b"] for d in duplicates}
        clean_products  = [r for r in rows
                           if r["product_name"] not in duplicate_names]

        high_c   = sum(1 for d in duplicates if d["confidence"] == "high")
        medium_c = sum(1 for d in duplicates if d["confidence"] == "medium")
        low_c    = sum(1 for d in duplicates if d["confidence"] == "low")

        return {
            "status":           "complete",
            "total_products":   total,
            "duplicate_count":  len(duplicates),
            "clean_count":      len(clean_products),
            "cluster_count":    len(clusters),
            "duplicates":       duplicates,
            "clusters":         clusters,
            "clean_products":   clean_products,
            "category_counts":  category_counts,
            "image_mode": {
                "image_loaded": image_source_counts["image"],
                "text_fallback_used": image_source_counts["clip_text"],
                "note": "CLIP text fallback maintains multimodal scoring even when image CDN blocks requests",
            },
            "image_debug": {
                "real_image_loaded": image_source_counts["image"],
                "clip_text_fallback": image_source_counts["clip_text"],
                "zero_fallback": image_source_counts["zero_fallback"],
                "note": (
                    "real_image_loaded = Flipkart CDN URL fetched successfully. "
                    "clip_text_fallback = CLIP text encoder used (same 512-dim space, valid score). "
                    "zero_fallback = total failure, should be 0."
                ),
            },
            "confidence_dist": {
                "high":   high_c,
                "medium": medium_c,
                "low":    low_c
            }
        }

    finally:
        # Ensure DB session is always closed
        db.close()