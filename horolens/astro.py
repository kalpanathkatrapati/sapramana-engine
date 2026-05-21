import swisseph as swe

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"
}

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
    "Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadra",
    "Uttara Bhadra","Revati"
]


def compute_navamsa(lon):
    s = int(lon//30)
    part = (lon%30)/(30/9)
    return SIGN_NAMES[(s*9+int(part))%12]


def calc_planets(jd):
    planets = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]
    ids = [swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,swe.JUPITER,swe.SATURN,swe.MEAN_NODE]
    pos={}
    for n,i in zip(planets,ids):
        result = swe.calc_ut(jd,i)
        # result is a tuple: (array_of_values, status)
        # array_of_values is (lon, lat, distance, lon_speed, lat_speed, dist_speed)
        lon = result[0][0]
        pos[n]=lon
    pos["Ketu"] = (pos["Rahu"]+180)%360
    return pos


def get_moon_nakshatra(lon):
    n = int((lon%360)/13.333333)
    return n, (lon%13.333333)/13.333333


def get_nakshatra_name(lon):
    index = int(lon/13.333333)
    return NAKSHATRAS[index % 27]
