import numpy as np
import io
from sqlalchemy.orm import Session
from db.models import MatchResult, Embedding


# ─── EMBEDDING: GET ───────────────────────────────────────────────────────────

def get_embedding(db: Session, content_key: str) -> np.ndarray | None:
    """
    Look up a stored embedding by its key.
    content_key = product_name (for text) or image_url (for images)
    Returns numpy array if found, None if not found.
    """
    row = (
        db.query(Embedding)
        .filter(Embedding.content_key == content_key)
        .first()
    )
    if row is None:
        return None

    # Deserialize bytes → numpy array (support both np.save and legacy pickled format)
    buffer = io.BytesIO(row.vector)
    try:
        return np.load(buffer, allow_pickle=False)
    except ValueError:
        buffer.seek(0)
        return np.load(buffer, allow_pickle=True)


# ─── EMBEDDING: SAVE ──────────────────────────────────────────────────────────

def save_embedding(
    db:          Session,
    content_key: str,
    vector:      np.ndarray,
    source:      str = "text"
) -> None:
    """
    Save a new embedding to PostgreSQL.
    source = "text" for SBERT (384-dim)
           = "image" for CLIP (512-dim)
    Skips silently if key already exists.
    """
    # Check if already exists — never overwrite
    existing = (
        db.query(Embedding)
        .filter(Embedding.content_key == content_key)
        .first()
    )
    if existing:
        return

    # Serialize numpy array → bytes
    buffer = io.BytesIO()
    np.save(buffer, vector, allow_pickle=False)
    vector_bytes = buffer.getvalue()

    row = Embedding(
        content_key = content_key,
        source      = source,
        vector      = vector_bytes,
        dimensions  = len(vector),
    )
    db.add(row)
    db.commit()


# ─── EMBEDDING: GET MANY ──────────────────────────────────────────────────────

def get_embeddings_bulk(
    db:           Session,
    content_keys: list[str]
) -> dict[str, np.ndarray]:
    """
    Fetch multiple embeddings in one query.
    Returns dict: {content_key: numpy_array}
    Only returns keys that were found.
    """
    rows = (
        db.query(Embedding)
        .filter(Embedding.content_key.in_(content_keys))
        .all()
    )
    result = {}
    for row in rows:
        buffer = io.BytesIO(row.vector)
        try:
            result[row.content_key] = np.load(buffer, allow_pickle=False)
        except ValueError:
            buffer.seek(0)
            result[row.content_key] = np.load(buffer, allow_pickle=True)
    return result


# ─── EMBEDDING: SAVE MANY ─────────────────────────────────────────────────────

def save_embeddings_bulk(db: Session, items: list):
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from db.models import Embedding
    import numpy as np
    from datetime import datetime

    if not items:
        return

    rows = []
    for item in items:
        vec = item["vector"]
        if isinstance(vec, np.ndarray):
            buf = io.BytesIO()
            np.save(buf, vec, allow_pickle=False)
            vec = buf.getvalue()
        rows.append({
            "content_key": item["key"],
            "source":      item.get("source", "text"),
            "vector":      vec,
            "dimensions":  len(item["vector"]) if hasattr(item["vector"], "__len__") else 384,
            "created_at":  datetime.utcnow(),
        })

    stmt = pg_insert(Embedding).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["content_key"])
    db.execute(stmt)
    db.commit()
    print(f"[DB] Saved {len(rows)} embeddings (skipped duplicates)")


# ─── MATCH RESULT: SAVE ───────────────────────────────────────────────────────

def save_match_result(
    db:           Session,
    product_a:    str,
    product_b:    str,
    fuzzy_score:  float,
    text_sim:     float,
    image_sim:    float,
    final_score:  float,
    is_duplicate: bool,
) -> None:
    row = MatchResult(
        product_a    = product_a,
        product_b    = product_b,
        fuzzy_score  = fuzzy_score,
        text_sim     = text_sim,
        image_sim    = image_sim,
        final_score  = final_score,
        is_duplicate = is_duplicate,
    )
    db.add(row)
    db.commit()


# ─── MATCH RESULT: GET HISTORY ────────────────────────────────────────────────

def get_match_history(
    db:    Session,
    limit: int = 100
) -> list[MatchResult]:
    return (
        db.query(MatchResult)
        .order_by(MatchResult.created_at.desc())
        .limit(limit)
        .all()
    )