import swisseph as swe

# Use Lahiri ayanamsa for sidereal Vedic positions.
# Swiss Ephemeris default mode can differ, so force Lahiri consistency.
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"
}

PLANET_SHORT_NAMES = {
    "Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
    "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"
}

PLANET_NAMES_BY_LANG = {
    "en": {
        "Sun": "Sun",
        "Moon": "Moon",
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Mars": "Mars",
        "Jupiter": "Jupiter",
        "Saturn": "Saturn",
        "Rahu": "Rahu",
        "Ketu": "Ketu"
    },
    "sa": {
        "Sun": "Ravi",
        "Moon": "Chandra",
        "Mercury": "Budha",
        "Venus": "Shukra",
        "Mars": "Mangala",
        "Jupiter": "Guru",
        "Saturn": "Shani",
        "Rahu": "Rahu",
        "Ketu": "Ketu"
    },
    "te": {
        "Sun": "సూర్య",
        "Moon": "చంద్ర",
        "Mercury": "బుద్ధ",
        "Venus": "శుక్ర",
        "Mars": "మంగళ",
        "Jupiter": "గురు",
        "Saturn": "శని",
        "Rahu": "రాహు",
        "Ketu": "కేతు"
    }
}

SIGN_NAMES_BY_LANG = {
    "en": [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
    ],
    "sa": [
        "Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
        "Tula","Vrishchika","Dhanus","Makar","Kumbha","Meena"
    ],
    "te": [
        "మేష","వృషభ","మిథున","కర్కాటక","సింహ","కన్య",
        "తుల","వృష్చిక","ధనుస","మకర","కుంభ","మీనా"
    ]
}

SIGN_NAMES = SIGN_NAMES_BY_LANG["en"]


def get_planet_name(planet, lang="en"):
    return PLANET_NAMES_BY_LANG.get(lang, PLANET_NAMES_BY_LANG["en"]).get(planet, planet)


def get_sign_names(lang="en"):
    return SIGN_NAMES_BY_LANG.get(lang, SIGN_NAMES_BY_LANG["en"])


NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
    "Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadra",
    "Uttara Bhadra","Revati"
]


def compute_navamsa(lon, lang="en"):
    s = int(lon // 30)
    part = (lon % 30) / (30 / 9)
    sign_names = get_sign_names(lang)
    return sign_names[(s * 9 + int(part)) % 12]


SIDEREAL_MODES = {
    'lahiri': swe.SIDM_LAHIRI,
    'fagan-bradley': swe.SIDM_FAGAN_BRADLEY,
    'krishnamurti': swe.SIDM_KRISHNAMURTI,
    'raman': swe.SIDM_RAMAN,
    'yukteshwar': swe.SIDM_YUKTESHWAR,
    'true-citra': swe.SIDM_TRUE_CITRA
}
DEFAULT_SIDEREAL_MODE = 'lahiri'


def get_sidereal_mode(name):
    return SIDEREAL_MODES.get(name, SIDEREAL_MODES[DEFAULT_SIDEREAL_MODE])


def set_sidereal_mode(name):
    swe.set_sid_mode(get_sidereal_mode(name), 0, 0)


def get_ayanamsa(jd):
    if hasattr(swe, 'get_ayanamsa'):
        return swe.get_ayanamsa(jd)
    if hasattr(swe, 'swe_get_ayanamsa'):
        return swe.swe_get_ayanamsa(jd)
    return 0.0


def to_sidereal(lon, jd):
    return (lon - get_ayanamsa(jd)) % 360


def degrees_to_dms(decimal_degrees):
    """Convert decimal degrees to degrees and minutes string (e.g., 16°23')."""
    degrees = int(decimal_degrees)
    minutes = int((decimal_degrees - degrees) * 60)
    return f"{degrees}°{minutes}'"


def calc_planets(jd):
    planets = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]
    ids = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.MEAN_NODE]
    pos = {}
    for n, i in zip(planets, ids):
        result = swe.calc_ut(jd, i)
        lon = result[0][0]
        pos[n] = lon
    pos["Ketu"] = (pos["Rahu"] + 180) % 360
    return pos


def get_moon_nakshatra(lon):
    n = int((lon % 360) / 13.333333)
    return n, (lon % 13.333333) / 13.333333


def get_nakshatra_name(lon):
    index = int(lon/13.333333)
    return NAKSHATRAS[index % 27]
