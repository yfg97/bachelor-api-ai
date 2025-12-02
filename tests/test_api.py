import requests
import json

API_URL = "http://localhost:5000"

def test_summarize():
    print("\n📝 Test 1: Zusammenfassung")
    print("-" * 50)
    
    text = """
    Die Oberfinanzdirektion Frankfurt am Main führte am 15.11.2024 eine 
    Durchsuchung bei der Firma XYZ GmbH durch. Dabei wurden 150 E-Mails, 
    50 Rechnungen und 20 Verträge sichergestellt. Es besteht der Verdacht 
    auf Steuerhinterziehung in Höhe von 500.000 Euro.
    """
    
    response = requests.post(
        f"{API_URL}/api/summarize",
        json={'text': text}
    )
    
    result = response.json()
    print(f"Original-Länge: {result['original_length']} Zeichen")
    print(f"\nZusammenfassung:\n{result['summary']}")

def test_classify():
    print("\n🏷️  Test 2: Klassifikation")
    print("-" * 50)
    
    texts = [
        "Rechnung Nr. 12345 vom 01.10.2024 über 5.000 Euro",
        "Sehr geehrte Damen und Herren, hiermit bestätigen wir...",
        "Kaufvertrag zwischen Partei A und Partei B über..."
    ]
    
    for text in texts:
        response = requests.post(
            f"{API_URL}/api/classify",
            json={'text': text}
        )
        result = response.json()
        print(f"Text: {text[:50]}...")
        print(f"Kategorie: {result['category']}\n")

def test_question():
    print("\n❓ Test 3: Fragen beantworten")
    print("-" * 50)
    
    text = """
    Am 10.05.2024 überwies die Firma ABC GmbH einen Betrag von 
    100.000 Euro an die Offshore-Firma XYZ Ltd. auf den Cayman Islands.
    Der Verwendungszweck lautete 'Beratungsleistungen'.
    """
    
    questions = [
        "Wie hoch war der überwiesene Betrag?",
        "An wen wurde das Geld überwiesen?",
        "Was war der Verwendungszweck?"
    ]
    
    for question in questions:
        response = requests.post(
            f"{API_URL}/api/question",
            json={'text': text, 'question': question}
        )
        result = response.json()
        print(f"F: {result['question']}")
        print(f"A: {result['answer']}\n")

if __name__ == "__main__":
    print("🧪 Starte API-Tests...")
    print("=" * 50)
    
    try:
        test_summarize()
        test_classify()
        test_question()
        
        print("\n✅ Alle Tests abgeschlossen!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Fehler: API ist nicht erreichbar!")
        print("Stelle sicher, dass app.py läuft (python api\\app.py)")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")