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
            metrics = cfg.get('metrics', [])
            return years, sources, metrics
        except Exception:
            pass
    return DEFAULT_YEARS, DEFAULT_SOURCES, []


def parse_number(value):
    if value is None:
        return None
    normalized = value.strip().replace(' ', '')
    if ',' in normalized and '.' in normalized:
        if normalized.find('.') < normalized.find(','):
            normalized = normalized.replace('.', '').replace(',', '.')
        else:
            normalized = normalized.replace(',', '')
    elif ',' in normalized:
        normalized = normalized.replace('.', '').replace(',', '.')
    else:
        normalized = normalized.replace('.', '')
    try:
        if '.' in normalized:
            return float(normalized)
        return int(normalized)
    except ValueError:
        return None


def search_patterns(text, patterns):
    for pattern in patterns:
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        except re.error:
            continue
        if match and match.groups():
            number = parse_number(match.group(1))
            if number is not None:
                return number
    return None


def extract_metrics(text, metrics_config, years):
    metrics = {}
    metrics_by_year = {str(year): {} for year in years}

    for metric in metrics_config:
        key = metric['key']
        patterns = metric.get('patterns', [])
        year_patterns = metric.get('year_patterns', [])
        metrics[key] = search_patterns(text, patterns)

        for year in years:
            year_key = str(year)
            year_specific = None
            for pattern in year_patterns:
                try:
                    formatted = pattern.format(year=year)
                except Exception:
                    formatted = pattern
                year_specific = search_patterns(text, [formatted])
                if year_specific is not None:
                    break
            metrics_by_year[year_key][key] = year_specific

    return metrics, metrics_by_year


def check_updates():
    years, sources, metrics_config = load_config()
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
            detected_years = sorted(set([int(m.group(0)) for m in year_pattern.finditer(text)]))
            item['detected_years'] = detected_years
            item['found_years'] = [y for y in years if str(y) in text]
            item['metrics'], item['metrics_by_year'] = extract_metrics(text, metrics_config, years)
            item['snippet'] = text[:600]
        except Exception as e:
            item['error'] = str(e)
            item['status_code'] = None
            item['detected_years'] = []
            item['found_years'] = []
            item['metrics'] = {}
            item['metrics_by_year'] = {str(year): {} for year in years}
            item['snippet'] = ''

        results.append(item)

    out_path = Path('datos_dashboard.json')
    payload = {
        "generated_at": datetime.utcnow().isoformat() + 'Z',
        "config_years": years,
        "metrics_config": metrics_config,
        "sources": results
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Resultados guardados en {out_path}")
    return results


if __name__ == '__main__':
    check_updates()