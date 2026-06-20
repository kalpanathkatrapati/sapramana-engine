from horolens.config.dignities import (
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    OWN_SIGNS
)


# =========================================================
# DIGNITY STRENGTH
# =========================================================

def calculate_dignity_strength(
    planet,
    sign
):

    result = {
        "score": 0,
        "reason": "Neutral"
    }

    exalted_sign = EXALTATION_SIGNS.get(
        planet
    )

    debilitated_sign = DEBILITATION_SIGNS.get(
        planet
    )

    own_signs = OWN_SIGNS.get(
        planet,
        []
    )

    # =====================================================
    # EXALTATION
    # =====================================================

    if sign == exalted_sign:

        result["score"] = 20

        result["reason"] = "Exalted"

        return result

    # =====================================================
    # DEBILITATION
    # =====================================================

    if sign == debilitated_sign:

        result["score"] = -20

        result["reason"] = "Debilitated"

        return result

    # =====================================================
    # OWN SIGN
    # =====================================================

    if sign in own_signs:

        result["score"] = 15

        result["reason"] = "Own Sign"

        return result

    return result


# =========================================================
# FULL STRENGTH ENGINE
# =========================================================

def calculate_all_strengths(chart):

    strengths = {}

    for row in chart.planet_table:

        planet = row[0]

        sign = row[2]

        dignity = calculate_dignity_strength(
            planet,
            sign
        )

        total = dignity["score"]

        strengths[planet] = {

            "total": total,

            "components": {

                "dignity": dignity
            }
        }

    return strengths