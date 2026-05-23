from io import BytesIO

from flask import send_file

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# =========================================================
# SOUTH INDIAN CHART DRAWER
# =========================================================

def draw_south_indian_chart(
    c,
    title,
    chart_data,
    start_x,
    start_y
):

    box_w = 85
    box_h = 55

    c.setFont(
        "Helvetica-Bold",
        12
    )

    c.drawString(
        start_x,
        start_y + 15,
        title
    )

    positions = {
        0: (1, 0),   # Mesha
        1: (2, 0),   # Vrishabha
        2: (3, 0),   # Mithuna
        3: (3, 1),   # Karka
        4: (3, 2),   # Simha
        5: (3, 3),   # Kanya
        6: (2, 3),   # Tula
        7: (1, 3),   # Vrischika
        8: (0, 3),   # Dhanu
        9: (0, 2),   # Makara
        10: (0, 1),  # Kumbha
        11: (0, 0),  # Meena
    }

    signs = list(chart_data.keys())

    for index, sign in enumerate(signs):

        col, row = positions[index]

        x = start_x + col * box_w
        y = start_y - row * box_h

        c.rect(
            x,
            y - box_h,
            box_w,
            box_h
        )

        c.setFont(
            "Helvetica-Bold",
            8
        )

        c.drawString(
            x + 4,
            y - 12,
            sign
        )

        occupants = chart_data.get(sign, [])

        c.setFont(
            "Helvetica",
            7
        )

        text_y = y - 24

        for occ in occupants[:5]:

            c.drawString(
                x + 4,
                text_y,
                str(occ)
            )

            text_y -= 9


# =========================================================
# PDF GENERATOR
# =========================================================

def generate_pdf(chart):

    buf = BytesIO()

    c = canvas.Canvas(
        buf,
        pagesize=A4
    )

    width, height = A4

    # =====================================================
    # TITLE
    # =====================================================

    c.setFont(
        "Helvetica-Bold",
        16
    )

    c.drawCentredString(
        width / 2,
        height - 40,
        "HoroLens Horoscope Report"
    )

    # =====================================================
    # BASIC INFO
    # =====================================================

    y = height - 80

    c.setFont(
        "Helvetica",
        11
    )

    c.drawString(
        50,
        y,
        f"Name: {chart.name}"
    )

    y -= 16

    c.drawString(
        50,
        y,
        f"Gender: {chart.gender}"
    )

    y -= 16

    c.drawString(
        50,
        y,
        f"Place: {chart.place}"
    )

    y -= 16

    c.drawString(
        50,
        y,
        f"Date & Time: {chart.dob} {chart.tob}"
    )

    y -= 16

    c.drawString(
        50,
        y,
        f"Lagna: {chart.lagna}"
    )

    # =====================================================
    # RASI CHART
    # =====================================================

    y -= 45

    draw_south_indian_chart(
        c,
        "Rāśi Chart",
        chart.rasi,
        50,
        y
    )

    # =====================================================
    # NAVAMSA TABLE
    # =====================================================

    c.setFont(
        "Helvetica-Bold",
        12
    )

    c.drawString(
        430,
        y + 15,
        "Navāṁśa Chart"
    )

    table_y = y - 5

    c.setFont(
        "Helvetica-Bold",
        9
    )

    c.drawString(
        430,
        table_y,
        "Sign"
    )

    c.drawString(
        510,
        table_y,
        "Occupants"
    )

    table_y -= 14

    c.setFont(
        "Helvetica",
        8
    )

    for sign in chart.ordered_signs:

        occupants = ", ".join(
            chart.navamsa.get(sign, [])
        )

        c.drawString(
            430,
            table_y,
            sign
        )

        c.drawString(
            510,
            table_y,
            occupants
        )

        table_y -= 11

    # =====================================================
    # HOUSE CHART TABLE
    # =====================================================

    y -= 300

    c.setFont(
        "Helvetica-Bold",
        13
    )

    c.drawString(
        50,
        y,
        "House Chart"
    )

    y -= 20

    c.setFont(
        "Helvetica-Bold",
        10
    )

    c.drawString(
        50,
        y,
        "House"
    )

    c.drawString(
        120,
        y,
        "Sign"
    )

    c.drawString(
        250,
        y,
        "Occupants"
    )

    y -= 15

    c.setFont(
        "Helvetica",
        9
    )

    for house in chart.house_chart:

        occupants = ", ".join(
            house.get('occupants', [])
        )

        c.drawString(
            50,
            y,
            str(house.get('house'))
        )

        c.drawString(
            120,
            y,
            house.get('sign', '')
        )

        c.drawString(
            250,
            y,
            occupants
        )

        y -= 14

        if y < 80:

            c.showPage()

            y = height - 50

    # =====================================================
    # PLANETARY POSITIONS
    # =====================================================

    y -= 15

    if y < 180:

        c.showPage()

        y = height - 50

    c.setFont(
        "Helvetica-Bold",
        13
    )

    c.drawString(
        50,
        y,
        "Planetary Positions"
    )

    y -= 20

    c.setFont(
        "Helvetica",
        9
    )

    for p, lon, sign, nak in chart.planet_table:

        line = (
            f"{p:12s} "
            f"{str(lon):10s} "
            f"{sign:15s} "
            f"({nak})"
        )

        c.drawString(
            60,
            y,
            line
        )

        y -= 13

        if y < 60:

            c.showPage()

            y = height - 50

    # =====================================================
    # DASHA
    # =====================================================

    y -= 15

    if y < 180:

        c.showPage()

        y = height - 50

    c.setFont(
        "Helvetica-Bold",
        13
    )

    c.drawString(
        50,
        y,
        "Vimśottarī Daśā"
    )

    y -= 20

    for maha, start, end, antars in chart.dasha:

        c.setFont(
            "Helvetica-Bold",
            10
        )

        c.drawString(
            60,
            y,
            f"{maha} ({start} → {end})"
        )

        y -= 14

        c.setFont(
            "Helvetica",
            8
        )

        for sub, s2, e2 in antars:

            c.drawString(
                80,
                y,
                f"- {sub}: {s2} → {e2}"
            )

            y -= 11

            if y < 60:

                c.showPage()

                y = height - 50

    # =====================================================
    # FINALIZE
    # =====================================================

    c.showPage()

    c.save()

    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="horolens.pdf",
        mimetype="application/pdf"
    )