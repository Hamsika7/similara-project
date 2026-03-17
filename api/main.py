from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.dependencies import load_models
from api.routes import match, bulk, history, health
from db.connection import init_db, get_db
from db.models import Embedding

app = FastAPI(
    title="SIMILARA API",
    description="Multimodal Product Matching API",
    version="1.0.0"
)

# ── CORS — allows Streamlit to talk to FastAPI ────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    load_models()

# ── Routes ────────────────────────────────────────────
app.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)
app.include_router(
    match.router,
    prefix="/match",
    tags=["Match"]
)
app.include_router(
    bulk.router,
    prefix="/bulk",
    tags=["Bulk"]
)
app.include_router(
    history.router,
    prefix="/history",
    tags=["History"]
)

@app.get("/")
def root():
    return {
        "message":  "SIMILARA API is running ✅",
        "version":  "1.0.0",
        "docs":     "http://127.0.0.1:8000/docs"
    }


@app.delete("/admin/clear-image-cache", tags=["Admin"])
def clear_image_embedding_cache(db: Session = Depends(get_db)):
    """
    Clears all cached image embeddings from PostgreSQL.

    Use this ONCE after fixing the image embedding logic.
    Forces the next bulk run to re-generate all image embeddings
    using the corrected URL parser and CLIP function.

    Returns:
        Count of deleted cache entries and a status message
    """
    try:
        deleted_count = (
            db.query(Embedding)
            .filter(Embedding.source == "image")
            .delete()
        )
        db.commit()
        print(f"[CACHE] 🗑️  Cleared {deleted_count} stale image embeddings")
        return {
            "status": "success",
            "deleted_image_embeddings": deleted_count,
            "message": (
                "Image cache cleared. Next POST /bulk/ will re-embed "
                "all products using the fixed URL parser."
            ),
        }
    except Exception as e:
        db.rollback()
        print(f"[CACHE] ❌ Failed to clear image cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))