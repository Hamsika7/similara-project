from fastapi import APIRouter
from api.dependencies import get_models
from datetime import datetime

router = APIRouter()

@router.get("/")
def health_check():
    try:
        models = get_models()
        models_loaded = (
            "text_embeddings"  in models and
            "image_embeddings" in models and
            "fusion_weights"   in models and
            "threshold"        in models
        )
        return {
            "status":        "ok",
            "models_loaded": models_loaded,
            "text_cache":    len(models.get("text_embeddings",  {})),
            "image_cache":   len(models.get("image_embeddings", {})),
            "weights":       models.get("fusion_weights", {}),
            "threshold":     models.get("threshold", 0.7),
            "timestamp":     datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status":        "error",
            "models_loaded": False,
            "error":         str(e),
            "timestamp":     datetime.now().isoformat()
        }