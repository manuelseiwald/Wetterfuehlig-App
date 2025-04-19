import streamlit as st
import requests

# Funktion, um die METAR-Daten abzurufen
def get_metar(icao="LOWS"):
    try:
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        if len(lines) >= 2:
            timestamp = lines[0]
            metar = lines[1]
            return metar
        else:
            return "Kein METAR verfügbar."
    except Exception as e:
        return f"Fehler beim Abrufen des METAR: {e}"

# Funktion zur Berechnung von Druckänderungen, Temperatur, Feuchtigkeit und Föhn
def analyze_weather_conditions(metar_data):
    # Hier nehmen wir an, dass der METAR-Datenstring ein Format hat wie: "1012 hPa"
    # Der genaue Parsingprozess hängt vom METAR-Format ab.
    # Beispiel: "1013.25 QNH, 15°C, Wind 10 km/h, Feuchtigkeit 80%"
    
    # Extraktion von Daten aus dem METAR (Dummy-Werte zur Illustration)
    qnh = float(metar_data.split()[1])  # Beispiel: 1013.25 hPa
    temp = float(metar_data.split()[2])  # Beispiel: 15°C
    wind_speed = float(metar_data.split()[3])  # Beispiel: 10 km/h
    humidity = float(metar_data.split()[4])  # Beispiel: 80% Feuchtigkeit
    pressure_change = abs(qnh - 1013)  # Beispiel für Veränderung
    wind_direction = "from the south"  # Beispiel für Föhnrichtung

    # Berechnung des Indikators
    weather_warning = ""
    
    # Schnelle Druckänderungen
    if pressure_change > 3:
        weather_warning += "Warnung: Schnelle Druckänderung (mehr als 3 hPa in kurzer Zeit). "
    
    # Föhn- oder starker Wind
    if wind_speed > 20 and ("from the south" in wind_direction or "Föhn" in wind_direction):
        weather_warning += "Warnung: Föhn (starker warmer Wind), kann Kopfschmerzen und Schlafstörungen verursachen. "
    
    # Hoher Luftdruck
    if qnh > 1025:
        weather_warning += "Warnung: Hoher Luftdruck, kann Kreislaufprobleme verursachen. "
    
    # Niedriger Luftdruck
    if qnh < 1010:
        weather_warning += "Warnung: Niedriger Luftdruck, möglicherweise Müdigkeit und Kreislaufbeschwerden. "
    
    # Temperaturstürze oder plötzliche Temperaturänderungen
    if abs(temp - 15) > 5:
        weather_warning += "Warnung: Schnelle Temperaturänderung, kann Kreislaufprobleme verursachen. "
    
    # Hohe Luftfeuchtigkeit
    if humidity > 85:
        weather_warning += "Warnung: Hohe Luftfeuchtigkeit, kann das Wohlbefinden beeinträchtigen. "
    
    # Gewittergefahr (starker Temperaturabfall in kurzer Zeit)
    if "Gewitter" in metar_data:
        weather_warning += "Warnung: Gewittergefahr. Achten Sie auf plötzliche Druckänderungen und mögliche Kopfschmerzen oder Schwindel. "
    
    # Wenn keine der Bedingungen zutrifft
    if not weather_warning:
        weather_warning = "Aktuell keine Warnung für wetterfühlige Personen."

    return weather_warning

# Streamlit App
st.title("Wetterfühligkeits-Warnung")

# Holen des METAR-Daten
metar_data = get_metar("LOWS")  # Salzburg Flughafen METAR
st.info(f"**Aktueller METAR für Salzburg (LOWS):**\n\n```\n{metar_data}\n```")

# Analyse der Wetterbedingungen
warning = analyze_weather_conditions(metar_data)

# Anzeige der Warnung
st.warning(warning)