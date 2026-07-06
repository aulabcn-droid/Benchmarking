# Dashboard Som Llar - Instrucciones

Este repositorio contiene:

- `dashboard_somllar.html`: página estática que muestra gráficos y el estado del scraper.
- `automatismo_scraping.py`: script Python que consulta las webs y genera `datos_dashboard.json`.
- `datos_dashboard.json`: archivo generado por el scraper (no debe editarse manualmente).
- `requirements.txt`: dependencias Python.

Pasos rápidos:

1. Asegúrate de tener Python instalado (3.11+ recomendado).
2. Instala dependencias:

```powershell
& "C:\\Users\\Aulabcn\\AppData\\Local\\Python\\bin\\python.exe" -m pip install -r requirements.txt
```

3. Ejecuta el scraper (genera `datos_dashboard.json`):

```powershell
& "C:\\Users\\Aulabcn\\AppData\\Local\\Python\\bin\\python.exe" automatismo_scraping.py
```

4. Sirve la carpeta con un servidor HTTP y abre el dashboard en el navegador:

```powershell
cd "c:\\Users\\Aulabcn\\OneDrive - Associació ProHabitatge\\Documentos\\Tareas"
& "C:\\Users\\Aulabcn\\AppData\\Local\\Python\\bin\\python.exe" -m http.server 8000
# Abrir http://localhost:8000/dashboard_somllar.html
```

Notas:
- Si `python` apunta al alias de Microsoft Store, usa la ruta completa al ejecutable como en los ejemplos anteriores o ajusta tus "App execution aliases" en Configuración.
- `dashboard_somllar.html` utiliza CDNs para Chart.js y Tailwind; si trabajas sin conexión, descarga esas librerías localmente.
