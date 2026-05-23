from flask import Blueprint, render_template, request, send_file, jsonify, session
from datetime import datetime
import pytz
import swisseph as swe
from geopy.geocoders import Nominatim

from .astro import (
    PLANET_SYMBOLS,
    PLANET_SHORT_NAMES,
    get_planet_name,
    get_sign_names,
    calc_planets,
    get_nakshatra_name,
    compute_navamsa,
    get_ayanamsa,
    set_sidereal_mode,
    to_sidereal,
    degrees_to_dms,
)

from .dasha import compute_vimsottari
from .geo import geocode_place, get_timezone
from .pdfgen import generate_pdf
from .chart import build_south_chart_context
from .cities import WORLD_CITIES

from .models import Chart


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
        results = geolocator.geocode(
            query,
            exactly_one=False,
            limit=8,
            addressdetails=False,
            language='en'
        )

        locations = [result.address for result in results] if results else []

    except Exception:
        locations = []

    return jsonify(locations)


@bp.route('/result', methods=['POST'])
def result():
    chart = Chart()

    chart.name = request.form.get('name', 'Default').strip() or 'Default'

    chart.gender = request.form.get('gender', 'male')
    if chart.gender not in ('male', 'female'):
        chart.gender = 'male'

    dob_text = request.form.get('dob', '01-Jan-1983').strip()
    tob = request.form.get('tob', '05:48').strip()

    chart.place = request.form.get(
        'place',
        'Chirala, Andhra Pradesh'
    ).strip()

    chart.lang = request.form.get('lang', 'en')
    ayanamsa = request.form.get('ayanamsa', 'lahiri')

    if chart.lang not in LABELS_BY_LANG:
        chart.lang = 'en'

    if ayanamsa not in (
        'lahiri',
        'fagan-bradley',
        'krishnamurti',
        'raman',
        'yukteshwar',
        'true-citra'
    ):
        ayanamsa = 'lahiri'

    chart.labels = LABELS_BY_LANG[chart.lang]

    try:
        dob = datetime.strptime(dob_text, "%d-%b-%Y")
        chart.dob = dob_text

    except ValueError:
        try:
            dob = datetime.strptime(dob_text, "%Y-%m-%d")
            chart.dob = dob.strftime("%d-%b-%Y")

        except ValueError:
            return "Invalid date format. Use DD-MMM-YYYY."

    try:
        time_obj = datetime.strptime(tob, "%H:%M")
        chart.tob = time_obj.strftime("%I:%M %p")

    except ValueError:
        chart.tob = tob

    geo = geocode_place(chart.place)

    if not geo:
        return "Place not found."

    lat, lon = geo

    chart.latitude = lat
    chart.longitude = lon

    tz, tzname = get_timezone(lat, lon)
    chart.timezone = tzname

    local = tz.localize(
        datetime.strptime(
            f"{chart.dob} {tob}",
            "%d-%b-%Y %H:%M"
        )
    )

    utc = local.astimezone(pytz.utc)

    jd = swe.julday(
        utc.year,
        utc.month,
        utc.day,
        utc.hour + utc.minute / 60
    )

    set_sidereal_mode(ayanamsa)

    swe.set_topo(lon, lat)

    pos = calc_planets(jd)

    ayanamsa = get_ayanamsa(jd)

    sign_names = get_sign_names(chart.lang)

    chart.rasi = {s: [] for s in sign_names}
    chart.navamsa = {s: [] for s in sign_names}

    for p, l in pos.items():
        sidereal_lon = to_sidereal(l, jd)

        sign = sign_names[int(sidereal_lon // 30)]

        nak = get_nakshatra_name(sidereal_lon)

        degree_in_sign = sidereal_lon % 30

        planet_label = get_planet_name(p, chart.lang)

        short_name = PLANET_SHORT_NAMES[p]

        dms_str = degrees_to_dms(degree_in_sign)

        chart.rasi[sign].append(f"{short_name} {dms_str}")

        chart.navamsa[
            compute_navamsa(sidereal_lon, chart.lang)
        ].append(f"{PLANET_SYMBOLS[p]} {planet_label}")

        chart.planet_table.append(
            (planet_label, dms_str, sign, nak)
        )

    houses, ascmc = swe.houses_ex(jd, lat, lon, b'A')

    sidereal_asc = (ascmc[0] - ayanamsa) % 360

    lagna_index = int(sidereal_asc // 30)

    lagna_degree_in_sign = sidereal_asc % 30

    lagna_dms = degrees_to_dms(lagna_degree_in_sign)

    chart.lagna = sign_names[lagna_index]

    chart.rasi[chart.lagna].insert(0, f"ASC {lagna_dms}")

    def sort_occupants(occupants):
        asc_entry = None
        planets = []

        for occ in occupants:
            if occ.startswith("ASC"):
                asc_entry = occ
            else:
                planets.append(occ)

        def get_degree(planet_str):
            try:
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

    for sign in chart.rasi:
        chart.rasi[sign] = sort_occupants(chart.rasi[sign])

    chart.ordered_signs = (
        sign_names[lagna_index:] + sign_names[:lagna_index]
    )

    for index, sign in enumerate(chart.ordered_signs, start=1):
        occupants = chart.rasi[sign]

        chart.house_chart.append({
            'house': index,
            'sign': sign,
            'occupants': occupants
        })

    chart.dasha = compute_vimsottari(
        to_sidereal(pos["Moon"], jd),
        local
    )

    chart.chart_context = build_south_chart_context(
        chart.rasi,
        chart.lagna,
        sign_names
    )

    session['chart_data'] = chart.to_dict()
    
    return render_template(
        'result.html',
        chart=chart
    )


@bp.route('/download')
def download_pdf():

    chart_data = session.get('chart_data')

    if not chart_data:
        return "No chart data found."

    chart = Chart.from_dict(chart_data)

    return generate_pdf(chart)