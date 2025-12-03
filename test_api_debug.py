"""
Debug-Skript: Teste API-Upload mit ausführlichem Error-Handling
"""
import requests
import json

print("=" * 60)
print("API-TEST: rfc822.txt Upload")
print("=" * 60)

filepath = "testdaten/rfc822.txt"

print(f"\n1. Datei öffnen: {filepath}")
with open(filepath, 'rb') as f:
    files = {'files': (filepath, f, 'text/plain')}

    print(f"2. POST zu /api/upload/batch...")
    try:
        response = requests.post(
            'http://localhost:5000/api/upload/batch',
            files=files,
            timeout=300  # 5 Minuten
        )

        print(f"\n3. Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")

        print(f"\n4. Response Body:")
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if data.get('results'):
            print(f"\n5. Detaillierte Ergebnisse:")
            for result in data['results']:
                print(f"\n   Datei: {result.get('filename')}")
                print(f"   Success: {result.get('success')}")
                if not result.get('success'):
                    print(f"   ERROR: {result.get('error')}")
                    if 'error_details' in result:
                        print(f"   Details:\n{result['error_details']}")

    except requests.exceptions.Timeout:
        print("\n✗ TIMEOUT - Request dauerte zu lange!")
    except requests.exceptions.ConnectionError:
        print("\n✗ CONNECTION ERROR - Läuft die API?")
    except Exception as e:
        print(f"\n✗ FEHLER: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
