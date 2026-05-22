from typing import List, Dict, Any

# Grid mapping for a fixed South Indian chart layout.
# Each entry is an index into the sign names list (0=Aries,...,11=Pisces).
# None marks an empty cell (visual spacer).
# Standard South-Indian fixed layout (4 rows x 4 cols) with the central 2×2 cells blank.
# The signs run clockwise around the border of the chart.
GRID_IDX = [
    [11, 0, 1, 2],
    [10, None, None, 3],
    [9, None, None, 4],
    [8, 7, 6, 5]
]


def build_south_chart_context(rasi: Dict[str, List[str]], lagna: str, sign_names: List[str]):
    """Build a context structure for rendering a South Indian chart.

    Args:
        rasi: mapping sign name -> list of occupant strings (e.g. ['☉ Sun 12.34°'])
        lagna: sign name of the ascendant (e.g. 'Aries')
        sign_names: ordered list of 12 sign names starting from Aries

    Returns:
        dict with `rows`: list of rows; each row is list of cell dicts with keys
        `sign`, `occupants`, `is_lagna`.
    """
    rows = []
    for row in GRID_IDX:
        cells = []
        for idx in row:
            if idx is None:
                cells.append({'empty': True})
                continue
            sign = sign_names[idx]
            occupants = rasi.get(sign, [])
            cells.append({
                'empty': False,
                'sign': sign,
                'occupants': occupants,
                'is_lagna': (sign == lagna)
            })
        rows.append(cells)
    return {'rows': rows}


__all__ = ['build_south_chart_context']
