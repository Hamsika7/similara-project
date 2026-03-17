from rapidfuzz import fuzz

def get_fuzzy_score(name_a: str, name_b: str,
                    desc_a: str = "", desc_b: str = "") -> float:
    name_score = fuzz.token_sort_ratio(
        str(name_a).lower(),
        str(name_b).lower()
    ) / 100.0

    if desc_a and desc_b:
        desc_score = fuzz.token_set_ratio(
            str(desc_a).lower()[:500],
            str(desc_b).lower()[:500]
        ) / 100.0
        return round(0.7 * name_score + 0.3 * desc_score, 4)

    return round(name_score, 4)