from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz


def geocode_place(place, user_agent="horolens"):
    geo = Nominatim(user_agent=user_agent).geocode(place)
    if not geo:
        return None
    return geo.latitude, geo.longitude


def get_timezone(lat, lon):
    tf = TimezoneFinder()
    name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
    return pytz.timezone(name), name
