from flask import Flask, render_template, request, send_file
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

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

DASHA_YEARS = {
    "Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,
    "Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17
}
DASHA_SEQUENCE = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

def compute_navamsa(lon):
    s = int(lon//30)
    part = (lon%30)/(30/9)
    return SIGN_NAMES[(s*9+int(part))%12]

def get_timezone(lat, lon):
    tf = TimezoneFinder()
    name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
    return pytz.timezone(name), name

def calc_planets(jd):
    planets = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]
    ids = [swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,swe.JUPITER,swe.SATURN,swe.MEAN_NODE]
    pos={}
    for n,i in zip(planets,ids):
        lon,_,_,_ = swe.calc_ut(jd,i)
        pos[n]=lon
    pos["Ketu"] = (pos["Rahu"]+180)%360
    return pos

def get_moon_nakshatra(lon):
    n = int((lon%360)/13.333333)
    return n, (lon%13.333333)/13.333333

def get_nakshatra_name(lon):
    index = int(lon/13.333333)
    return NAKSHATRAS[index % 27]

# --- Compute Dasha & Antardasha ---
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    dob, tob, place = request.form['dob'], request.form['tob'], request.form['place']
    geo = Nominatim(user_agent="horolens").geocode(place)
    if not geo: return "Place not found."
    lat, lon = geo.latitude, geo.longitude
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

    houses, ascmc, _ = swe.houses_ex(jd, lat, lon, b'A')
    lagna = int(ascmc[0]//30)
    ordered = SIGN_NAMES[lagna:]+SIGN_NAMES[:lagna]

    dasha = compute_vimsottari(pos["Moon"], local)

    global last_data
    last_data = dict(place=place, dob=dob, tob=tob, tz=tzname,
                     rasi=rasi, nav=navamsa, ord=ordered, lagna=SIGN_NAMES[lagna],
                     dasha=dasha, planet_table=planet_table)
    return render_template('result.html', **last_data)

@app.route('/download')
def download_pdf():
    if not last_data: return "No data."
    buf=BytesIO()
    c=canvas.Canvas(buf,pagesize=A4)
    c.setFont("Helvetica-Bold",14)
    c.drawString(180,810,"HoroLens Horoscope Report")
    c.setFont("Helvetica",11)
    c.drawString(50,780,f"Place: {last_data['place']}")
    c.drawString(50,765,f"Date: {last_data['dob']} {last_data['tob']} ({last_data['tz']})")
    c.drawString(50,750,f"Lagna: {last_data['lagna']}")

    y=720
    c.setFont("Helvetica-Bold",12)
    c.drawString(50,y,"Planetary Positions:")
    y-=20
    c.setFont("Helvetica",10)
    for p, lon, sign, nak in last_data['planet_table']:
        c.drawString(60,y,f"{p:9s} {lon:7.2f}°  {sign:10s}  ({nak})")
        y-=14
        if y<60:
            c.showPage()
            y=800

    y-=10
    c.setFont("Helvetica-Bold",12)
    c.drawString(50,y,"Vimśottarī Daśā with Antardaśā:")
    y-=20
    c.setFont("Helvetica",9)
    for maha, start, end, antars in last_data['dasha']:
        c.setFont("Helvetica-Bold",10)
        c.drawString(60,y,f"{maha}  ({start} → {end})")
        y-=14
        c.setFont("Helvetica",9)
        for sub, s2, e2 in antars:
            c.drawString(80,y,f"- {sub:8s}  {s2} → {e2}")
            y-=12
            if y<60:
                c.showPage()
                y=800
    c.showPage()
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name="horolens.pdf",
                     mimetype="application/pdf")

if __name__=="__main__":
    app.run(debug=True)
