import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path('sources.json')

# Valores por defecto si no existe sources.json
DEFAULT_YEARS = [2024, 2025, 2026]
DEFAULT_SOURCES = [
    {"nombre": "Som Llar", "url": "https://somllar.example.org/transparencia"},
    {"nombre": "Habitat3", "url": "https://www.habitat3.cat/transparencia"},
    {"nombre": "Provivienda", "url": "https://www.provivienda.org/transparencia/"},
    {"nombre": "Fundació Mambré", "url": "https://fundaciomambre.org/ca/transparencia/"}
]


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            years = cfg.get('years', DEFAULT_YEARS)
            sources = cfg.get('sources', DEFAULT_SOURCES)
            return years, sources
        except Exception:
            pass
    return DEFAULT_YEARS, DEFAULT_SOURCES


def extract_found_years(text, years):
    found = []
    for y in years:
        if str(y) in text:
            found.append(int(y))
    return found


def check_updates():
    years, sources = load_config()
    results = []
    year_pattern = re.compile(r"\b(19|20)\d{2}\b")

    for org in sources:
        item = {
            "nombre": org.get('nombre'),
            "url": org.get('url'),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        try:
            resp = requests.get(org.get('url'), timeout=15, headers={"User-Agent": "automatismo/1.0 (+https://example.org)"})
            resp.raise_for_status()
            text = resp.text
            item['status_code'] = resp.status_code
            # detectamos años disponibles en la página y los que nos interesan
            detected_years = sorted(set([int(m.group(0)) for m in year_pattern.finditer(text)]))
            item['detected_years'] = detected_years
            item['found_years'] = [y for y in years if str(y) in text]
            item['snippet'] = text[:600]
        except Exception as e:
            item['error'] = str(e)
            item['status_code'] = None
            item['detected_years'] = []
            item['found_years'] = []
            item['snippet'] = ''

        results.append(item)

    out_path = Path('datos_dashboard.json')
    payload = {
        "generated_at": datetime.utcnow().isoformat() + 'Z',
        "config_years": years,
        "sources": results
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Resultados guardados en {out_path}")
    return results


if __name__ == '__main__':
    check_updates()