from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session
)

from geopy.geocoders import Nominatim

from .cities import WORLD_CITIES
from .models import Chart
from .pdfgen import generate_pdf
from .services import generate_chart


bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/api/cities')
def get_cities():
    return jsonify(WORLD_CITIES)


@bp.route('/api/location')
def search_location():

    query = request.args.get(
        'q',
        ''
    ).strip()

    if not query:
        return jsonify([])

    try:

        geolocator = Nominatim(
            user_agent='horolens'
        )

        results = geolocator.geocode(
            query,
            exactly_one=False,
            limit=8,
            addressdetails=False,
            language='en'
        )

        locations = [
            result.address
            for result in results
        ] if results else []

    except Exception:
        locations = []

    return jsonify(locations)


@bp.route('/result', methods=['POST'])
def result():

    try:

        chart = generate_chart(
            request.form
        )

    except ValueError as e:
        return str(e)

    session['chart_data'] = chart.to_dict()
    
    print(chart.strengths)
    
    return render_template(
        'result.html',
        chart=chart
    )


@bp.route('/download')
def download_pdf():

    chart_data = session.get(
        'chart_data'
    )

    if not chart_data:
        return 'No chart data found.'

    chart = Chart.from_dict(
        chart_data
    )

    return generate_pdf(chart)