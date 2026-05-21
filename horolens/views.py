from flask import Blueprint, render_template, request, send_file
from datetime import datetime
import pytz
import swisseph as swe

from .astro import (PLANET_SYMBOLS, SIGN_NAMES, calc_planets,
                    get_nakshatra_name, compute_navamsa)
from .dasha import compute_vimsottari
from .geo import geocode_place, get_timezone
from .pdfgen import generate_pdf

bp = Blueprint('main', __name__)

# module-level storage for last generated data (simple approach)
last_data = None


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/result', methods=['POST'])
def result():
    global last_data
    dob, tob, place = request.form['dob'], request.form['tob'], request.form['place']
    geo = geocode_place(place)
    if not geo: return "Place not found."
    lat, lon = geo
    tz, tzname = get_timezone(lat, lon)
    local = tz.localize(datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M"))
    utc = local.astimezone(pytz.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour+utc.minute/60)
    swe.set_topo(lon, lat)
    pos = calc_planets(jd)

    # Build charts
    rasi={s:[] for s in SIGN_NAMES}
    navamsa={s:[] for s in SIGN_NAMES}
    planet_table=[]

    for p,l in pos.items():
        sign = SIGN_NAMES[int(l//30)]
        nak = get_nakshatra_name(l)
        rasi[sign].append(PLANET_SYMBOLS[p])
        navamsa[compute_navamsa(l)].append(PLANET_SYMBOLS[p])
        planet_table.append((p, round(l,2), sign, nak))

    houses, ascmc = swe.houses_ex(jd, lat, lon, b'A')
    lagna = int(ascmc[0]//30)
    ordered = SIGN_NAMES[lagna:]+SIGN_NAMES[:lagna]

    dasha = compute_vimsottari(pos["Moon"], local)

    last_data = dict(place=place, dob=dob, tob=tob, tz=tzname,
                     rasi=rasi, nav=navamsa, ord=ordered, lagna=SIGN_NAMES[lagna],
                     dasha=dasha, planet_table=planet_table)
    return render_template('result.html', **last_data)


@bp.route('/download')
def download_pdf():
    if not last_data: return "No data."
    buf = generate_pdf(last_data)
    return send_file(buf, as_attachment=True,
                     download_name="horolens.pdf",
                     mimetype="application/pdf")
