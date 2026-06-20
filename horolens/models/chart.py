from dataclasses import dataclass, field


@dataclass
class Chart:

    name: str = ""
    gender: str = ""
    dob: str = ""
    tob: str = ""
    place: str = ""

    latitude: float = None
    longitude: float = None
    timezone: str = ""

    lagna: str = ""

    rasi: dict = field(default_factory=dict)
    navamsa: dict = field(default_factory=dict)

    ordered_signs: list = field(default_factory=list)
    house_chart: list = field(default_factory=list)

    planet_table: list = field(default_factory=list)
    dasha: list = field(default_factory=list)

    chart_context: dict = field(default_factory=dict)

    strengths: dict = field(default_factory=dict)

    lang: str = "en"

    labels: dict = field(default_factory=dict)

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(self):

        return {
            'name': self.name,
            'gender': self.gender,
            'dob': self.dob,
            'tob': self.tob,
            'place': self.place,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone,
            'lagna': self.lagna,
            'rasi': self.rasi,
            'navamsa': self.navamsa,
            'ordered_signs': self.ordered_signs,
            'house_chart': self.house_chart,
            'planet_table': self.planet_table,
            'dasha': self.dasha,
            'chart_context': self.chart_context,
            'strengths': self.strengths,
            'lang': self.lang,
            'labels': self.labels
        }

    @classmethod
    def from_dict(cls, data):

        chart = cls()

        chart.name = data.get('name', '')
        chart.gender = data.get('gender', '')
        chart.dob = data.get('dob', '')
        chart.tob = data.get('tob', '')
        chart.place = data.get('place', '')

        chart.latitude = data.get('latitude')
        chart.longitude = data.get('longitude')
        chart.timezone = data.get('timezone', '')

        chart.lagna = data.get('lagna', '')

        chart.rasi = data.get('rasi', {})
        chart.navamsa = data.get('navamsa', {})

        chart.ordered_signs = data.get(
            'ordered_signs',
            []
        )

        chart.house_chart = data.get(
            'house_chart',
            []
        )

        chart.planet_table = data.get(
            'planet_table',
            []
        )

        chart.dasha = data.get(
            'dasha',
            []
        )

        chart.chart_context = data.get(
            'chart_context',
            {}
        )

        chart.strengths = data.get(
            'strengths',
            {}
        )

        chart.lang = data.get(
            'lang',
            'en'
        )

        chart.labels = data.get(
            'labels',
            {}
        )

        return chart