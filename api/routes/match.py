from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.schemas.product import MatchRequest, MatchResponse
from api.services.fuzzy_service import get_fuzzy_score
from api.services.embedding_service import get_text_similarity, get_image_similarity
from api.services.fusion_service import fuse_scores
from db.connection import get_db
from db.crud import save_match_result

router = APIRouter()

@router.post("/", response_model=MatchResponse)
def match_products(request: MatchRequest, db: Session = Depends(get_db)):
    a = request.product_a
    b = request.product_b

    # Compute all 3 scores
    fuzzy     = get_fuzzy_score(a.name, b.name,
                                a.description, b.description)
    text_sim  = get_text_similarity(a.name, b.name)
    image_sim = get_image_similarity(a.image_url, b.image_url)

    # Fuse scores
    final, is_duplicate = fuse_scores(fuzzy, text_sim, image_sim)

    # Save to database
    save_match_result(db, a.name, b.name, fuzzy,
                      text_sim, image_sim, final, is_duplicate)

    return MatchResponse(
        product_a    = a.name,
        product_b    = b.name,
        fuzzy_score  = fuzzy,
        text_sim     = text_sim,
        image_sim    = image_sim,
        final_score  = final,
        is_duplicate = is_duplicate
    )