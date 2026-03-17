import numpy as np
from sentence_transformers import SentenceTransformer
from db.connection import get_db_session
from db.crud import get_embeddings_bulk, save_embeddings_bulk
import ast

# ─── URL PARSER: Flipkart stringified list format ─────────────────────────────

def _extract_first_image_url(raw_url: str) -> str:
    """
    Extracts the first valid image URL from Flipkart's stringified list format.

    The Flipkart dataset stores image URLs as a Python list inside a string:
      '["http://img5a.flixcart.com/abc.jpg", "http://img5a.flixcart.com/def.jpg"]'

    This function safely parses that format and returns the first URL.
    Also handles plain URL strings for other datasets.

    Args:
        raw_url: Raw value from the image/image_url column in CSV

    Returns:
        First valid URL string, or empty string if nothing usable found

    Examples:
        >>> _extract_first_image_url('["http://img5a.flixcart.com/abc.jpg"]')
        'http://img5a.flixcart.com/abc.jpg'
        >>> _extract_first_image_url('http://plain-url.com/img.jpg')
        'http://plain-url.com/img.jpg'
        >>> _extract_first_image_url('')
        ''
    """
    if not raw_url or not isinstance(raw_url, str):
        return ""

    raw_url = raw_url.strip()

    if raw_url.lower() in ("nan", "none", "null", ""):
        return ""

    # Case 1: Flipkart stringified list format — starts with "["
    if raw_url.startswith("["):
        try:
            parsed = ast.literal_eval(raw_url)
            if isinstance(parsed, list) and len(parsed) > 0:
                first_url = str(parsed[0]).strip()
                return first_url if first_url.startswith("http") else ""
        except (ValueError, SyntaxError):
            pass

    # Case 2: Already a plain URL string
    if raw_url.startswith("http"):
        return raw_url

    return ""


# ─── LOAD MODELS ONCE AT IMPORT ───────────────────────────────────────────────
print("[EMB] Loading SBERT model...")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
print("[EMB] SBERT ready ✅")

try:
    from transformers import CLIPModel, CLIPProcessor
    import torch
    from PIL import Image
    import requests
    from io import BytesIO

    clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model = clip_model.to(device)
    clip_model.eval()
    CLIP_AVAILABLE = True
    print(f"[EMB] CLIP ready ✅ on device={device}")
except Exception as e:
    CLIP_AVAILABLE = False
    device = "cpu"
    print(f"[EMB] CLIP not available: {e}")


# ─── COSINE SIMILARITY ────────────────────────────────────────────────────────

def cosine_sim(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity between two numpy vectors."""
    denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


# ─── TEXT: ENCODE ONE ─────────────────────────────────────────────────────────

def encode_text(text: str) -> np.ndarray:
    """Encode a single text string using SBERT."""
    return sbert_model.encode(
        str(text),
        convert_to_numpy=True,
        show_progress_bar=False
    )


# ─── TEXT: ENCODE BATCH — POSTGRESQL FIRST ────────────────────────────────────

def get_text_embeddings_batch(texts: list[str]) -> dict[str, np.ndarray]:
    """
    Main function for bulk text embedding.

    For each text:
      1. Check PostgreSQL first
      2. If found → return stored vector instantly
      3. If not found → run SBERT → save to PostgreSQL

    Returns dict: {text: numpy_array}
    """
    if not texts:
        return {}

    db = next(get_db_session())

    try:
        # ── Step 1: Bulk fetch from PostgreSQL ────────────
        print(f"[EMB] Checking PostgreSQL for {len(texts)} texts...")
        cached = get_embeddings_bulk(db, texts)
        print(f"[EMB] Found {len(cached)} in PostgreSQL cache")

        # ── Step 2: Find which ones are missing ───────────
        missing = [t for t in texts if t not in cached]
        print(f"[EMB] Need to encode {len(missing)} new texts with SBERT")

        # ── Step 3: Batch encode all missing texts ────────
        if missing:
            new_vectors = sbert_model.encode(
                missing,
                batch_size=64,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            # ── Step 4: Save all new embeddings to PostgreSQL
            items = [
                {
                    "key":    text,
                    "vector": new_vectors[i],
                    "source": "text"
                }
                for i, text in enumerate(missing)
            ]
            save_embeddings_bulk(db, items)

            # ── Step 5: Add to result dict ─────────────────
            for i, text in enumerate(missing):
                cached[text] = new_vectors[i]

        return cached

    except Exception as e:
        print(f"[EMB] Error in get_text_embeddings_batch: {e}")
        # Fallback — encode everything fresh without saving
        vectors = sbert_model.encode(
            texts,
            batch_size=64,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return {text: vectors[i] for i, text in enumerate(texts)}

    finally:
        db.close()


# ─── TEXT: SINGLE PAIR SIMILARITY ─────────────────────────────────────────────

def get_text_similarity(text_a: str, text_b: str) -> float:
    """
    Get cosine similarity between two texts.
    Used by single /match route.
    """
    db = next(get_db_session())
    try:
        cached = get_embeddings_bulk(db, [text_a, text_b])

        if text_a in cached:
            emb_a = cached[text_a]
        else:
            emb_a = encode_text(text_a)
            save_embeddings_bulk(db, [{"key": text_a,
                                       "vector": emb_a,
                                       "source": "text"}])

        if text_b in cached:
            emb_b = cached[text_b]
        else:
            emb_b = encode_text(text_b)
            save_embeddings_bulk(db, [{"key": text_b,
                                       "vector": emb_b,
                                       "source": "text"}])

        return round(cosine_sim(emb_a, emb_b), 4)

    finally:
        db.close()


def encode_image_or_text_fallback(
    image_url: str,
    product_name: str,
) -> tuple[np.ndarray, str]:
    """
    Read image URL (parsing Flipkart stringified-list format) and get CLIP embedding
    for similarity comparison. Generates a 512-dim CLIP embedding for a product's
    visual representation.

    Uses a 3-layer fallback strategy to always return a meaningful embedding:
      Layer 1 — Parse URL correctly + fetch real image → CLIP image encoder
      Layer 2 — If image unavailable → CLIP text encoder on product_name
                (CLIP image+text encoders share same 512-dim space — Radford et al. 2021)
      Layer 3 — If CLIP text also fails → return zero vector + log it

    Returns:
        Tuple of (embedding shape (512,), source)
        source is one of: "image", "clip_text", "zero_fallback"
    """
    if not CLIP_AVAILABLE:
        print("[CLIP] ❌ CLIP not available → zero_fallback")
        return np.zeros(512, dtype=np.float32), "zero_fallback"

    # ── Layer 1: Parse URL and attempt real image download
    url = _extract_first_image_url(image_url)

    if url:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "https://www.flipkart.com/",
            }
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content)).convert("RGB")
            inputs = clip_processor(images=image, return_tensors="pt").to(device)
            with torch.no_grad():
                embedding = clip_model.get_image_features(**inputs)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            print(f"[CLIP] ✅ Real image loaded for: {product_name[:50]}")
            return embedding.cpu().numpy().flatten(), "image"

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            print(f"[CLIP] ⚠️  HTTP {status} for '{product_name[:40]}' → text fallback")
        except requests.exceptions.Timeout:
            print(f"[CLIP] ⚠️  Timeout for '{product_name[:40]}' → text fallback")
        except requests.exceptions.ConnectionError:
            print(f"[CLIP] ⚠️  Connection error for '{product_name[:40]}' → text fallback")
        except Exception as e:
            print(f"[CLIP] ⚠️  Image failed ({type(e).__name__}) for '{product_name[:40]}' → text fallback")

    # ── Layer 2: CLIP text encoder fallback
    try:
        name_to_encode = product_name.strip() if product_name.strip() else "unknown product"
        inputs = clip_processor(
            text=[name_to_encode],
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(device)
        with torch.no_grad():
            embedding = clip_model.get_text_features(**inputs)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        print(f"[CLIP] 📝 Text fallback used for: {product_name[:50]}")
        return embedding.cpu().numpy().flatten(), "clip_text"
    except Exception as e:
        print(f"[CLIP] ❌ Total failure for '{product_name[:50]}': {type(e).__name__}: {e}")
        return np.zeros(512, dtype=np.float32), "zero_fallback"


# ─── IMAGE: GET SIMILARITY ────────────────────────────────────────────────────

def get_image_similarity(url_a: str, url_b: str) -> float:
    """
    Get cosine similarity between two product images.
    Checks PostgreSQL first, encodes with CLIP (image or text fallback) if missing.
    """
    if not url_a or not url_b:
        return 0.0

    db = next(get_db_session())
    try:
        cached = get_embeddings_bulk(db, [url_a, url_b])

        emb_a = cached.get(url_a)
        if emb_a is None:
            emb_a, _ = encode_image_or_text_fallback(url_a, url_a)
            save_embeddings_bulk(db, [{"key": url_a, "vector": emb_a, "source": "image"}])

        emb_b = cached.get(url_b)
        if emb_b is None:
            emb_b, _ = encode_image_or_text_fallback(url_b, url_b)
            save_embeddings_bulk(db, [{"key": url_b, "vector": emb_b, "source": "image"}])

        return round(cosine_sim(emb_a, emb_b), 4)

    finally:
        db.close()