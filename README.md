# sapramana-engine

Welcome to the sapramana-engine project. This repo contains the HoroLens astrology engine and a small Flask app entrypoint at `app.py`.

## Overview

The app computes planetary positions, Nakshatras and Vimsottari Dasha and can generate a PDF birth-chart report.

## Prerequisites

- Python 3.12 (or compatible 3.x)
- System packages for virtualenv support (`python3-venv`) if creating a venv

## Quickstart (development)

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the app locally:

```bash
python app.py
# Visit http://127.0.0.1:5000/ in your browser
```

## Generate a birth chart

- Using the web UI: open `http://127.0.0.1:5000/`, enter Birth Date (`YYYY-MM-DD`), Time (`HH:MM`) and Place (free-text), submit. The result page shows charts and a `Download` link to get a PDF.

- Using command line (example):

```bash
# POST form data to /result (this sets server-side last_data)
curl -X POST -F "dob=1990-01-01" -F "tob=12:00" -F "place=New York" http://127.0.0.1:5000/result

# then download the generated PDF
curl -o horolens.pdf http://127.0.0.1:5000/download
```

## Production (Gunicorn)

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:8000
```

## Troubleshooting

- If pip refuses to install due to an "externally-managed environment" (PEP 668), create a virtual environment as shown above or use a container.
- If `python3 -m venv` fails, install the OS package `python3-venv` (e.g. `apt install python3.12-venv`) before creating the venv.

## Docker (optional)

You can run the app in a container to avoid host Python environment issues. Example Dockerfile snippet:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```

Build & run:

```bash
docker build -t horolens .
docker run -p 5000:5000 horolens
```

## Contributing

PRs welcome. For changes to the astrology engine prefer small, testable commits (e.g., add unit tests for `horolens.dasha`).

## Support

Open an issue on GitHub for questions or problems.
