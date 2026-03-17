from api.dependencies import get_models

def fuse_scores(fuzzy: float, text_sim: float,
                image_sim: float) -> tuple:
    models    = get_models()
    weights   = models["fusion_weights"]
    threshold = models["threshold"]

    final = (
        weights["fuzzy"] * fuzzy +
        weights["text"]  * text_sim +
        weights["image"] * image_sim
    )
    final        = round(final, 4)
    is_duplicate = bool(final >= threshold)

    return final, is_duplicate