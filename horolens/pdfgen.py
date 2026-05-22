from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_pdf(data):
    labels = data.get('labels', {})
    title = labels.get('title', 'HoroLens Horoscope Report')
    name_label = labels.get('name', 'Name')
    place_label = labels.get('place', 'Place')
    datetime_label = labels.get('datetime', 'Date & Time')
    lagna_label = labels.get('lagna', 'Lagna')
    planetary_positions_label = labels.get('planetary_positions', 'Planetary Positions')
    vimsottari_label = labels.get('vimsottari', 'Vimśottarī Daśā with Antardaśā')

    buf = BytesIO()
    c = canvas.Canvas(buf,pagesize=A4)
    c.setFont("Helvetica-Bold",14)
    c.drawString(180,810,title)
    c.setFont("Helvetica",11)
    c.drawString(50,780,f"{name_label}: {data.get('name','')}")
    c.drawString(50,765,f"{place_label}: {data['place']}")
    c.drawString(50,750,f"{datetime_label}: {data['dob']} {data['tob']} ({data['tz']})")
    c.drawString(50,735,f"{lagna_label}: {data['lagna']}")

    y=720
    c.setFont("Helvetica-Bold",12)
    c.drawString(50,y,planetary_positions_label)
    y-=20
    c.setFont("Helvetica",10)
    for p, lon, sign, nak in data['planet_table']:
        c.drawString(60,y,f"{p:9s} {lon:7.2f}°  {sign:10s}  ({nak})")
        y-=14
        if y<60:
            c.showPage()
            y=800

    y-=10
    c.setFont("Helvetica-Bold",12)
    c.drawString(50,y,vimsottari_label)
    y-=20
    c.setFont("Helvetica",9)
    for maha, start, end, antars in data['dasha']:
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
    return buf
