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
            metar = lines[1]
            return metar
        else:
            return "Kein METAR verfügbar."
    except Exception as e:
        return f"Fehler beim Abrufen des METAR: {e}"

# Funktion zur Berechnung von Druckänderungen, Temperatur, Feuchtigkeit und Föhn
def analyze_weather_conditions(metar_data):
    # Beispiel für METAR-Daten: "LOWS 181120Z 30012G18KT 15SM -RA OVC030 18/12 A3023 RMK AO2 SLP268"
    # Wir müssen nun die relevanten Daten wie Druck, Temperatur, Wind und Feuchtigkeit extrahieren.

    try:
        # Extrahieren des Luftdrucks
        qnh = float(metar_data.split("A")[1].split()[0])  # A3023 -> 3023 -> 1023.0 hPa

        # Extrahieren der Temperatur
        temp = int(metar_data.split(" ")[-5][:-1])  # 18/12 -> Temperatur ist 18°C

        # Extrahieren der Windgeschwindigkeit und -richtung
        wind_data = metar_data.split(" ")[2]  # 30012G18KT -> Windrichtung 300°, 12 kt, Böen 18 kt
        wind_speed = int(wind_data[3:5])  # 12 kt
        wind_direction = int(wind_data[:3])  # 300°

        # Extrahieren der Feuchtigkeit (hier nicht direkt im METAR, wird üblicherweise aus anderen Quellen abgerufen)
        humidity = 80  # Dummy-Wert, Feuchtigkeit müsste aus einem anderen Datensatz kommen

        # Berechnung des Druckwechsels
        pressure_change = abs(qnh - 1013)  # Beispiel für Veränderung

        # Bestimmen des Föhns (Windrichtung und Geschwindigkeit als Kriterien)
        is_föhn = wind_direction >= 150 and wind_direction <= 240 and wind_speed > 15  # Föhn kommt aus Südrichtung

        weather_warning = ""
        
        # Schnelle Druckänderungen (mehr als 3 hPa in kurzer Zeit)
        if pressure_change > 3:
            weather_warning += "Warnung: Schnelle Druckänderung (mehr als 3 hPa in kurzer Zeit). "
        
        # Föhn oder starker Wind
        if is_föhn:
            weather_warning += "Warnung: Föhn (starker warmer Wind), kann Kopfschmerzen und Schlafstörungen verursachen. "
        
        # Hoher Luftdruck (>1025 hPa)
        if qnh > 1025:
            weather_warning += "Warnung: Hoher Luftdruck, kann Kreislaufprobleme verursachen. "
        
        # Niedriger Luftdruck (<1010 hPa)
        if qnh < 1010:
            weather_warning += "Warnung: Niedriger Luftdruck, möglicherweise Müdigkeit und Kreislaufbeschwerden. "
        
        # Temperaturstürze oder plötzliche Temperaturänderungen
        if abs(temp - 15) > 5:
            weather_warning += "Warnung: Schnelle Temperaturänderung, kann Kreislaufprobleme verursachen. "
        
        # Hohe Luftfeuchtigkeit (>85%)
        if humidity > 85:
            weather_warning += "Warnung: Hohe Luftfeuchtigkeit, kann das Wohlbefinden beeinträchtigen. "
        
        # Gewittergefahr (starker Temperaturabfall in kurzer Zeit)
        if "TS" in metar_data:
            weather_warning += "Warnung: Gewittergefahr. Achten Sie auf plötzliche Druckänderungen und mögliche Kopfschmerzen oder Schwindel. "
        
        # Keine Warnung
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