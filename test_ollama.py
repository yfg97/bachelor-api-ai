import requests 
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def test_ollama():
    print("Teste Verbindung zu Ollama...")
    
    # Payload erstellen
    payload = {
        "model": "llama3.2:3b",
        "prompt": "Fasse folgenden Text in 2 Sätzen zusammen: Die Firma ABC GmbH hat im Geschäftsjahr 2024 einen Umsatz von 1,5 Millionen Euro erzielt. Dies entspricht einer Steigerung von 20% gegenüber dem Vorjahr.",
        "stream": False
    }
    
    # Anfrage an Ollama senden
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Erfolg! Hier ist die Antwort von Ollama:\n")
            print(result['response'])
        else:
            print(f"❌ Fehler: Status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        print("\nTipp: Läuft Ollama? Prüfe mit 'ollama list'")

if __name__ == "__main__":
    test_ollama()