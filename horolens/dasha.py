from datetime import timedelta
from .astro import get_moon_nakshatra

DASHA_YEARS = {
    "Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,
    "Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17
}

DASHA_SEQUENCE = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]


def compute_vimsottari(moon_lon, birth_dt):
    nak_index, frac = get_moon_nakshatra(moon_lon)
    start_lord = DASHA_SEQUENCE[nak_index % 9]
    rem = (1 - frac) * DASHA_YEARS[start_lord]

    sequence=[]
    lord = start_lord
    dt = birth_dt

    for i in range(9):
        years = DASHA_YEARS[lord]
        if i==0:
            years = rem
        end = dt + timedelta(days=years*365.25)
        antars = compute_antardasha(lord, dt, end)
        sequence.append((lord, dt.date(), end.date(), antars))
        lord = DASHA_SEQUENCE[(DASHA_SEQUENCE.index(lord)+1)%9]
        dt = end
    return sequence


def compute_antardasha(maha_lord, start_dt, end_dt):
    total_days = (end_dt - start_dt).days
    antars=[]
    for sublord in DASHA_SEQUENCE:
        proportion = DASHA_YEARS[sublord]/120.0
        days = total_days * proportion
        sub_end = start_dt + timedelta(days=days)
        antars.append((sublord, start_dt.date(), sub_end.date()))
        start_dt = sub_end
    return antars
