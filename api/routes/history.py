from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.connection import get_db
from db.crud import get_match_history

router = APIRouter()

@router.get("/")
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    history = get_match_history(db, limit)
    return [
        {
            "id":           h.id,
            "product_a":    h.product_a,
            "product_b":    h.product_b,
            "fuzzy_score":  h.fuzzy_score,
            "text_sim":     h.text_sim,
            "image_sim":    h.image_sim,
            "final_score":  h.final_score,
            "is_duplicate": h.is_duplicate,
            "matched_at":   str(h.matched_at)
        }
        for h in history
    ]