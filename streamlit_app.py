import streamlit as st
import requests
import re

# Funktion, um die METAR-Daten abzurufen
def get_metar(icao="LOWS"):
    try:
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        if len(lines) >= 2:
            metar = lines[1]
            return metar
        else:
            return "Kein METAR verfügbar."
    except Exception as e:
        return f"Fehler beim Abrufen des METAR: {e}"

# Funktion zur Berechnung von Druckänderungen, Temperatur, Feuchtigkeit und Föhn
def analyze_weather_conditions(metar_data):
    try:
        # Extrahieren des Luftdrucks (Axxx -> xxx hPa, z. B. A3023 -> 1023.0 hPa)
        pressure_match = re.search(r"A(\d{4})", metar_data)
        if pressure_match:
            qnh = float(pressure_match.group(1)) / 100  # Beispiel: 3023 -> 1023.0 hPa
        else:
            qnh = None  # Keine Druckdaten gefunden

        # Extrahieren der Temperatur (z. B. "18/12" -> 18°C)
        temp_match = re.search(r"(\d{2})/(\d{2})", metar_data)
        if temp_match:
            temp = int(temp_match.group(1))  # Beispiel: 18
        else:
            temp = None  # Keine Temperatur gefunden

        # Extrahieren der Windgeschwindigkeit und -richtung (z. B. "30012G18KT")
        wind_match = re.search(r"(\d{3})(\d{2})G(\d{2})KT", metar_data)
        if wind_match:
            wind_direction = int(wind_match.group(1))  # Beispiel: 300°
            wind_speed = int(wind_match.group(2))  # Beispiel: 12 kt
            gust_speed = int(wind_match.group(3))  # Beispiel: 18 kt (Böen)
        else:
            wind_direction = None
            wind_speed = None
            gust_speed = None

        # Beispielhafte Feuchtigkeit (Dummy-Wert)
        humidity = 80  # Dummy-Wert für Feuchtigkeit

        # Berechnung des Druckwechsels (Differenz zum Standard-QNH 1013 hPa)
        if qnh is not None:
            pressure_change = abs(qnh - 1013)
        else:
            pressure_change = None

        # Föhn-Erkennung (Windrichtung aus Südrichtung und ausreichende Windgeschwindigkeit)
        is_föhn = False
        if wind_direction and wind_speed:
            if 150 <= wind_direction <= 240 and wind_speed > 15:  # Föhn kommt aus Südrichtung
                is_föhn = True

        # Generiere die Warnung basierend auf den gesammelten Daten
        weather_warning = ""

        # Schnelle Druckänderungen
        if pressure_change and pressure_change > 3:
            weather_warning += "Warnung: Schnelle Druckänderung (mehr als 3 hPa in kurzer Zeit). "

        # Föhn oder starker Wind
        if is_föhn:
            weather_warning += "Warnung: Föhn (starker warmer Wind), kann Kopfschmerzen und Schlafstörungen verursachen. "

        # Hoher Luftdruck (>1025 hPa)
        if qnh and qnh > 1025:
            weather_warning += "Warnung: Hoher Luftdruck, kann Kreislaufprobleme verursachen. "

        # Niedriger Luftdruck (<1010 hPa)
        if qnh and qnh < 1010:
            weather_warning += "Warnung: Niedriger Luftdruck, möglicherweise Müdigkeit und Kreislaufbeschwerden. "

        # Temperaturstürze oder plötzliche Temperaturänderungen
        if temp and abs(temp - 15) > 5:
            weather_warning += "Warnung: Schnelle Temperaturänderung, kann Kreislaufprobleme verursachen. "

        # Hohe Luftfeuchtigkeit (>85%)
        if humidity > 85:
            weather_warning += "Warnung: Hohe Luftfeuchtigkeit, kann das Wohlbefinden beeinträchtigen. "

        # Gewittergefahr (sieht nach Gewitter aus)
        if "TS" in metar_data:
            weather_warning += "Warnung: Gewittergefahr. Achten Sie auf plötzliche Druckänderungen und mögliche Kopfschmerzen oder Schwindel. "

        # Wenn keine Warnungen
        if not weather_warning:
            weather_warning = "Aktuell keine Warnung für wetterfühlige Personen."

        return weather_warning

    except Exception as e:
        return f"Fehler bei der Analyse der METAR-Daten: {e}"

# Streamlit App
st.title("Wetterfühligkeits-Warnung")

# Holen des METAR-Daten
metar_data = get_metar("LOWS")  # Salzburg Flughafen METAR
st.info(f"**Aktueller METAR für Salzburg (LOWS):**\n\n```\n{metar_data}\n```")

# Analyse der Wetterbedingungen
warning = analyze_weather_conditions(metar_data)

# Anzeige der Warnung
st.warning(warning)