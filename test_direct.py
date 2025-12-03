"""
Debug-Skript: Teste rfc822.txt direkt ohne API
"""
import sys
sys.path.insert(0, 'api')

from file_processor import process_file

print("=" * 60)
print("DIREKTER TEST: rfc822.txt")
print("=" * 60)

filepath = "testdaten/rfc822.txt"

print(f"\n1. Datei verarbeiten: {filepath}")
result = process_file(filepath)

print(f"\n2. Ergebnis:")
print(f"   Success: {result.get('success')}")
print(f"   Filetype: {result.get('filetype')}")
print(f"   Char count: {result.get('char_count')}")
print(f"   Is forensic: {result.get('is_forensic_data')}")

if result.get('success'):
    print(f"\n3. Metadata:")
    for key, value in result.get('metadata', {}).items():
        print(f"   {key}: {value}")

    print(f"\n4. Erste 500 Zeichen:")
    print(result.get('text', '')[:500])
else:
    print(f"\n✗ FEHLER: {result.get('error')}")

print("\n" + "=" * 60)
