"""
Test-Skript für die Datei-Upload API
Testet alle Upload-Endpunkte mit verschiedenen Dateitypen.

Ausführen:
    python test_upload.py
    
Voraussetzung:
    - API läuft (python api/app.py)
    - Test-Dateien im gleichen Ordner
"""

import requests
import os
import json

API_URL = "http://localhost:5000"


def print_header(title: str):
    """Gibt formatierten Header aus."""
    print()
    print("=" * 60)
    print(f"📋 {title}")
    print("=" * 60)


def print_result(result: dict, max_text: int = 500):
    """Gibt Ergebnis formatiert aus."""
    if result.get('success') or 'summary' in result or 'analysis' in result:
        print("✅ Erfolg!")
        
        # Je nach Endpunkt verschiedene Ausgaben
        if 'summary' in result:
            print(f"\n📝 Zusammenfassung:\n{result['summary']}")
        
        if 'analysis' in result:
            a = result['analysis']
            print(f"\n🏷️  Kategorie: {a.get('kategorie', 'N/A')}")
            print(f"\n📝 Zusammenfassung:\n{a.get('zusammenfassung', 'N/A')}")
            
            if a.get('firmen'):
                print(f"\n🏢 Firmen: {', '.join(a['firmen'])}")
            if a.get('personen'):
                print(f"👤 Personen: {', '.join(a['personen'])}")
            if a.get('geldbetraege'):
                print(f"💰 Beträge: {', '.join(a['geldbetraege'])}")
            if a.get('daten'):
                print(f"📅 Daten: {', '.join(a['daten'])}")
            if a.get('auffaelligkeiten'):
                print(f"⚠️  Auffälligkeiten: {', '.join(a['auffaelligkeiten'])}")
        
        if 'text' in result:
            text = result['text']
            if len(text) > max_text:
                text = text[:max_text] + "..."
            print(f"\n📄 Extrahierter Text:\n{text}")
        
        # Metadaten
        print(f"\n📊 Statistik:")
        for key in ['char_count', 'word_count', 'response_time_sec', 'total_time_sec']:
            if key in result:
                print(f"   - {key}: {result[key]}")
    else:
        print(f"❌ Fehler: {result.get('error', 'Unbekannt')}")


def test_health():
    """Testet den Health-Check Endpunkt."""
    print_header("Health Check")
    
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Umgebung: {result.get('environment')}")
        print(f"Modell: {result.get('model')}")
        print(f"Ollama: {result.get('ollama_status')}")
        print(f"Formate: {', '.join(result.get('supported_formats', []))}")
        
        return result.get('ollama_status') == 'online'
        
    except requests.exceptions.ConnectionError:
        print("❌ API nicht erreichbar!")
        print("   Starte die API mit: python api/app.py")
        return False


def test_text_upload():
    """Testet Upload einer TXT-Datei."""
    print_header("Test: TXT-Datei Upload")
    
    # Erstelle Test-Datei
    test_content = """BULK EXTRACTOR ANALYSE - TESTDATEN

Betreff: Verdächtige Transaktionen ABC GmbH

Am 15.03.2024 wurde eine Überweisung von 150.000 Euro von der ABC GmbH 
(Steuernummer: 012/345/67890) an die XYZ Holdings Ltd. auf den Cayman Islands 
durchgeführt. Die Zahlung erfolgte über IBAN DE89 3704 0044 0532 0130 00.

Der Geschäftsführer Hans Müller gab als Verwendungszweck "Beratungsleistungen Q1" an.
Eine Gegenleistung konnte bisher nicht nachgewiesen werden.

Weitere verdächtige E-Mail gefunden:
Von: h.mueller@abc-gmbh.de
An: offshore@xyz-holdings.ky
Datum: 14.03.2024
Betreff: Re: Zahlungsanweisung

"Bitte die Zahlung wie besprochen durchführen. Keine Dokumentation nötig."
"""
    
    test_file = "test_dokument.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Test 1: Nur Upload (Text extrahieren)
        print("\n1️⃣  Nur Text extrahieren:")
        with open(test_file, 'rb') as f:
            response = requests.post(
                f"{API_URL}/api/upload",
                files={'file': f}
            )
        print_result(response.json())
        
        # Test 2: Upload + Zusammenfassung
        print("\n2️⃣  Upload + Zusammenfassung:")
        with open(test_file, 'rb') as f:
            response = requests.post(
                f"{API_URL}/api/upload/summarize",
                files={'file': f}
            )
        print_result(response.json())
        
        # Test 3: Upload + Vollständige Analyse
        print("\n3️⃣  Upload + Vollständige Analyse:")
        with open(test_file, 'rb') as f:
            response = requests.post(
                f"{API_URL}/api/upload/analyze",
                files={'file': f}
            )
        print_result(response.json())
        
    finally:
        # Aufräumen
        if os.path.exists(test_file):
            os.remove(test_file)


def test_with_custom_file(filepath: str):
    """Testet mit einer benutzerdefinierten Datei."""
    print_header(f"Test: {os.path.basename(filepath)}")
    
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return
    
    try:
        print("\n📤 Lade Datei hoch und analysiere...")
        with open(filepath, 'rb') as f:
            response = requests.post(
                f"{API_URL}/api/upload/analyze",
                files={'file': f},
                timeout=120
            )
        
        if response.status_code == 200:
            print_result(response.json())
        else:
            print(f"❌ Fehler: Status {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Analyse dauerte zu lange")
    except Exception as e:
        print(f"❌ Fehler: {e}")


def test_text_endpoints():
    """Testet die Text-basierten Endpunkte."""
    print_header("Test: Text-Endpunkte")
    
    test_text = """Die Firma Müller & Partner GmbH hat am 01.04.2024 einen Vertrag 
    mit der Investment Corp. auf Malta geschlossen. Der Vertragswert beträgt 
    500.000 Euro über eine Laufzeit von 3 Jahren. Ansprechpartner ist Dr. Klaus Weber, 
    erreichbar unter k.weber@mueller-partner.de. Die Zahlung erfolgt auf 
    IBAN MT84 MALT 0110 0001 2345 6789 0123 456."""
    
    # Test Zusammenfassung
    print("\n1️⃣  Zusammenfassung:")
    response = requests.post(
        f"{API_URL}/api/summarize",
        json={"text": test_text}
    )
    print_result(response.json())
    
    # Test Klassifikation
    print("\n2️⃣  Klassifikation:")
    response = requests.post(
        f"{API_URL}/api/classify",
        json={"text": test_text}
    )
    result = response.json()
    print(f"✅ Kategorie: {result.get('category', 'N/A')}")
    
    # Test Frage
    print("\n3️⃣  Frage beantworten:")
    response = requests.post(
        f"{API_URL}/api/question",
        json={
            "text": test_text,
            "question": "Wie hoch ist der Vertragswert?"
        }
    )
    result = response.json()
    print(f"✅ Antwort: {result.get('answer', 'N/A')}")
    
    # Test Entity Extraction
    print("\n4️⃣  Entitäten extrahieren:")
    response = requests.post(
        f"{API_URL}/api/extract-entities",
        json={"text": test_text}
    )
    result = response.json()
    if 'entities' in result:
        for key, values in result['entities'].items():
            if values:
                print(f"   {key}: {', '.join(values)}")


def main():
    """Hauptfunktion."""
    print()
    print("🧪 " + "=" * 56)
    print("🧪  STEUERFAHNDUNG KI-FRAMEWORK - API TESTS")
    print("🧪 " + "=" * 56)
    
    # Health Check
    if not test_health():
        print("\n⚠️  API oder Ollama nicht verfügbar!")
        print("   1. Starte Ollama: ollama serve")
        print("   2. Starte API: python api/app.py")
        return
    
    # Text-Endpunkte testen
    test_text_endpoints()
    
    # Datei-Upload testen
    test_text_upload()
    
    # Optional: Eigene Datei testen
    # test_with_custom_file("pfad/zu/deiner/datei.pdf")
    
    print()
    print("=" * 60)
    print("✅ ALLE TESTS ABGESCHLOSSEN")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
