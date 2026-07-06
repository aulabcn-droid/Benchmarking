import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Lista de organizaciones a monitorizar
competidores = [
    {"nombre": "Habitat3", "url": "https://www.habitat3.cat/transparencia"},
    {"nombre": "Provivienda", "url": "https://www.provivienda.org/transparencia/"},
    {"nombre": "Fundació Mambré", "url": "https://fundaciomambre.org/ca/transparencia/"}
]

def check_updates():
    results = []
    for org in competidores:
        item = {"nombre": org['nombre'], "url": org['url'], "timestamp": datetime.utcnow().isoformat() + 'Z'}
        try:
            response = requests.get(org['url'], timeout=15)
            response.raise_for_status()
            text = response.text
            item['status_code'] = response.status_code
            item['found_2024'] = '2024' in text
            # pequeña muestra para facilitar inspección
            item['snippet'] = text[:400]
        except Exception as e:
            item['error'] = str(e)
            item['status_code'] = None
            item['found_2024'] = False
            item['snippet'] = ''
        results.append(item)

    # Guardar resultados en JSON para que el dashboard los consuma
    out_path = 'datos_dashboard.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({"generated_at": datetime.utcnow().isoformat() + 'Z', "sources": results}, f, ensure_ascii=False, indent=2)

    print(f"Resultados guardados en {out_path}")
    return results


if __name__ == "__main__":
    check_updates()