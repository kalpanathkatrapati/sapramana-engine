from flask import Blueprint, render_template, request, send_file, jsonify
from datetime import datetime
import pytz
import swisseph as swe
from geopy.geocoders import Nominatim

from .astro import (PLANET_SYMBOLS, PLANET_SHORT_NAMES, get_planet_name, get_sign_names,
                    calc_planets, get_nakshatra_name, compute_navamsa,
                    get_ayanamsa, set_sidereal_mode, to_sidereal, degrees_to_dms)
from .dasha import compute_vimsottari
from .geo import geocode_place, get_timezone
from .pdfgen import generate_pdf
from .chart import build_south_chart_context
from .cities import WORLD_CITIES

LABELS_BY_LANG = {
    'en': {
        'title': 'HoroLens Horoscope Report',
        'name': 'Name',
        'place': 'Place',
        'datetime': 'Date & Time',
        'lagna': 'Lagna',
        'planetary_positions': 'Planetary Positions',
        'sign': 'Sign',
        'nakshatra': 'Nakshatra',
        'south_chart': 'South Indian Chart',
        'house': 'House',
        'grahas': 'Grahas',
        'vimsottari': 'Vimśottarī Daśā',
        'download': '📄 Download PDF'
    },
    'sa': {
        'title': 'HoroLens Horoscope Report',
        'name': 'Name',
        'place': 'Place',
        'datetime': 'Date & Time',
        'lagna': 'Lagna',
        'planetary_positions': 'Planetary Positions',
        'sign': 'Sign',
        'nakshatra': 'Nakshatra',
        'south_chart': 'South Indian Chart',
        'house': 'House',
        'grahas': 'Grahas',
        'vimsottari': 'Vimśottarī Daśā',
        'download': '📄 Download PDF'
    },
    'te': {
        'title': 'హరోలెన్స్ జ్యోతిష్య నివేదిక',
        'name': 'పేరు',
        'place': 'స్థలం',
        'datetime': 'తేదీ & సమయం',
        'lagna': 'లగ్నం',
        'planetary_positions': 'గ్రహ స్థితులు',
        'sign': 'రాశి',
        'nakshatra': 'నక్షత్రం',
        'south_chart': 'దక్షిణ భారత శైలీ చార్ట్',
        'house': 'గృహం',
        'grahas': 'గ్రహాలు',
        'vimsottari': 'విమ్ శోత్తరి దశా',
        'download': '📄 PDF డౌన్లోడ్'
    }
}

bp = Blueprint('main', __name__)

# module-level storage for last generated data (simple approach)
last_data = None


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/api/cities')
def get_cities():
    return jsonify(WORLD_CITIES)


@bp.route('/api/location')
def search_location():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    try:
        geolocator = Nominatim(user_agent='horolens')
        results = geolocator.geocode(query, exactly_one=False, limit=8, addressdetails=False, language='en')
        locations = [result.address for result in results] if results else []
    except Exception:
        locations = []
    return jsonify(locations)


@bp.route('/result', methods=['POST'])
def result():
    global last_data
    name = request.form.get('name', 'Default').strip() or 'Default'
    gender = request.form.get('gender', 'male')
    if gender not in ('male', 'female'):
        gender = 'male'
    dob_text = request.form.get('dob', '01-Jan-1983').strip()
    tob = request.form.get('tob', '05:48').strip()
    place = request.form.get('place', 'Chirala, Andhra Pradesh').strip()
    lang = request.form.get('lang', 'en')
    ayanamsa = request.form.get('ayanamsa', 'lahiri')
    if lang not in LABELS_BY_LANG:
        lang = 'en'
    if ayanamsa not in ('lahiri', 'fagan-bradley', 'krishnamurti', 'raman', 'yukteshwar', 'true-citra'):
        ayanamsa = 'lahiri'

    try:
        dob = datetime.strptime(dob_text, "%d-%b-%Y")
        dob_display = dob_text
    except ValueError:
        try:
            dob = datetime.strptime(dob_text, "%Y-%m-%d")
            dob_display = dob.strftime("%d-%b-%Y")
        except ValueError:
            return "Invalid date format. Use DD-MMM-YYYY."

    # Convert time to 12-hour format
    try:
        time_obj = datetime.strptime(tob, "%H:%M")
        tob_12h_display = time_obj.strftime("%I:%M %p")
    except ValueError:
        tob_12h_display = tob

    geo = geocode_place(place)
    if not geo:
        return "Place not found."
    lat, lon = geo
    tz, tzname = get_timezone(lat, lon)
    local = tz.localize(datetime.strptime(f"{dob_display} {tob}", "%d-%b-%Y %H:%M"))
    utc = local.astimezone(pytz.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60)
    set_sidereal_mode(ayanamsa)
    swe.set_topo(lon, lat)
    pos = calc_planets(jd)
    ayanamsa = get_ayanamsa(jd)

    sign_names = get_sign_names(lang)
    rasi = {s: [] for s in sign_names}
    navamsa = {s: [] for s in sign_names}
    planet_table = []

    for p, l in pos.items():
        sidereal_lon = to_sidereal(l, jd)
        sign = sign_names[int(sidereal_lon // 30)]
        nak = get_nakshatra_name(sidereal_lon)
        degree_in_sign = sidereal_lon % 30
        planet_label = get_planet_name(p, lang)
        short_name = PLANET_SHORT_NAMES[p]
        dms_str = degrees_to_dms(degree_in_sign)
        # Chart display: short name with DMS
        rasi[sign].append(f"{short_name} {dms_str}")
        navamsa[compute_navamsa(sidereal_lon, lang)].append(f"{PLANET_SYMBOLS[p]} {planet_label}")
        # For planet table: store full info with DMS format
        planet_table.append((planet_label, dms_str, sign, nak))

    houses, ascmc = swe.houses_ex(jd, lat, lon, b'A')
    sidereal_asc = (ascmc[0] - ayanamsa) % 360
    lagna = int(sidereal_asc // 30)
    lagna_degree_in_sign = sidereal_asc % 30
    lagna_dms = degrees_to_dms(lagna_degree_in_sign)
    
    # Add lagna (ascendant) indicator with degrees to its sign
    lagna_sign = sign_names[lagna]
    rasi[lagna_sign].insert(0, f"ASC {lagna_dms}")
    
    # Sort planets by degrees (descending) within each sign, keeping ASC at top
    def sort_occupants(occupants):
        """Sort occupants: ASC always first, then other planets by decreasing degrees."""
        asc_entry = None
        planets = []
        for occ in occupants:
            if occ.startswith("ASC"):
                asc_entry = occ
            else:
                planets.append(occ)
        
        # Extract degree from planet string (e.g., "Su 16°23'" -> 16)
        def get_degree(planet_str):
            try:
                # Format: "XX d°m'" where XX is planet short name
                parts = planet_str.split()
                if len(parts) >= 2:
                    deg_str = parts[1].split('°')[0]
                    return int(deg_str)
            except (ValueError, IndexError):
                return 0
            return 0
        
        planets.sort(key=get_degree, reverse=True)
        result = []
        if asc_entry:
            result.append(asc_entry)
        result.extend(planets)
        return result
    
    # Apply sorting to all signs
    for sign in rasi:
        rasi[sign] = sort_occupants(rasi[sign])
    
    ordered = sign_names[lagna:] + sign_names[:lagna]
    house_chart = []
    for index, sign in enumerate(ordered, start=1):
        occupants = rasi[sign]
        house_chart.append({'house': index, 'sign': sign, 'occupants': occupants})

    dasha = compute_vimsottari(to_sidereal(pos["Moon"], jd), local)

    # build a rendering-friendly chart_context for the South Indian chart partial
    chart_context = build_south_chart_context(rasi, sign_names[lagna], sign_names)

    last_data = dict(name=name, gender=gender, place=place, dob=dob_display, tob=tob_12h_display, tz=tzname,
                     rasi=rasi, nav=navamsa, ord=ordered,
                     lagna=sign_names[lagna], dasha=dasha, planet_table=planet_table,
                     house_chart=house_chart, chart_context=chart_context,
                     lang=lang, labels=LABELS_BY_LANG[lang])
    return render_template('result.html', **last_data)


@bp.route('/download')
def download_pdf():
    if not last_data: return "No data."
    buf = generate_pdf(last_data)
    return send_file(buf, as_attachment=True,
                     download_name="horolens.pdf",
                     mimetype="application/pdf")
