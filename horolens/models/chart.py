from dataclasses import dataclass, field


@dataclass
class Chart:
    name: str = ""
    gender: str = ""
    dob: str = ""
    tob: str = ""
    place: str = ""

    latitude: float | None = None
    longitude: float | None = None
    timezone: str = ""

    lagna: str = ""

    rasi: dict = field(default_factory=dict)
    navamsa: dict = field(default_factory=dict)

    ordered_signs: list = field(default_factory=list)
    house_chart: list = field(default_factory=list)

    planet_table: list = field(default_factory=list)
    dasha: list = field(default_factory=list)

    chart_context: dict = field(default_factory=dict)

    lang: str = "en"
    labels: dict = field(default_factory=dict)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        chart = cls()

        for key, value in data.items():
            setattr(chart, key, value)

        return chart
    