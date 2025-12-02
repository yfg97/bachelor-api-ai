"""
Steuerfahndung KI-Framework API
Version 2.0 - Mit Datei-Upload Support

Endpunkte:
- POST /api/summarize        - Text zusammenfassen
- POST /api/classify         - Text klassifizieren  
- POST /api/question         - Frage zu Text stellen
- POST /api/extract-entities - Entitäten extrahieren
- POST /api/upload           - Datei hochladen und verarbeiten
- POST /api/upload/summarize - Datei hochladen und zusammenfassen
- POST /api/upload/analyze   - Datei hochladen und komplett analysieren

Starten mit:
    python app.py
    
Oder für Produktion:
    set BA_ENV=production
    python app.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename

# Eigene Module
from file_processor import process_file, get_supported_formats, truncate_text

# =============================================================================
# KONFIGURATION
# =============================================================================

# Umgebung erkennen
ENVIRONMENT = os.getenv('BA_ENV', 'development')

if ENVIRONMENT == 'production':
    # Arbeits-VM
    OLLAMA_URL = "http://10.172.27.248:11434/api/generate"
    MODEL = "llama3.1:70b"
    DEBUG = False
    print("🏢 Produktions-Modus (Arbeits-VM)")
else:
    # Entwicklung (Laptop)
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "llama3.2:3b"
    DEBUG = True
    print("💻 Entwicklungs-Modus (Laptop)")

# Upload-Konfiguration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc', 'csv', 'eml'}
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max

# Ordner erstellen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)  # Für Frontend-Zugriff


# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

def allowed_file(filename: str) -> bool:
    """Prüft ob Dateiendung erlaubt ist."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def call_ollama(prompt: str, max_tokens: int = 2000) -> dict:
    """
    Sendet Anfrage an Ollama und gibt strukturiertes Ergebnis zurück.
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result.get('response', ''),
                "model": MODEL,
                "response_time_sec": round(elapsed, 2)
            }
        else:
            return {
                "success": False,
                "error": f"Ollama Fehler: Status {response.status_code}",
                "response_time_sec": round(elapsed, 2)
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout - Anfrage dauerte zu lange"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Verbindungsfehler - Läuft Ollama auf {OLLAMA_URL}?"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unbekannter Fehler: {str(e)}"
        }


def log_request(endpoint: str, input_size: int, output_size: int, duration: float):
    """Loggt API-Anfragen für Evaluation."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "input_chars": input_size,
        "output_chars": output_size,
        "duration_sec": round(duration, 2),
        "model": MODEL,
        "environment": ENVIRONMENT
    }
    
    # In Datei schreiben (append)
    log_file = os.path.join(os.path.dirname(__file__), 'api_log.jsonl')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


# =============================================================================
# API ENDPUNKTE - TEXT
# =============================================================================

@app.route('/')
def home():
    """Startseite mit API-Dokumentation."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Steuerfahndung KI-Framework API</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }}
            h1 {{ color: #2c3e50; }}
            .endpoint {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .method {{ background: #27ae60; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
            .method-post {{ background: #2980b9; }}
            code {{ background: #ecf0f1; padding: 2px 5px; border-radius: 3px; }}
            .info {{ background: #e8f4f8; padding: 10px; border-left: 4px solid #3498db; }}
        </style>
    </head>
    <body>
        <h1>🔍 Steuerfahndung KI-Framework API</h1>
        
        <div class="info">
            <strong>Status:</strong> ✅ Aktiv<br>
            <strong>Modell:</strong> {MODEL}<br>
            <strong>Umgebung:</strong> {ENVIRONMENT}<br>
            <strong>Unterstützte Formate:</strong> {', '.join(ALLOWED_EXTENSIONS)}
        </div>
        
        <h2>📝 Text-Endpunkte</h2>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/summarize</code><br>
            Text zusammenfassen<br>
            <small>Body: {{"text": "..."}}</small>
        </div>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/classify</code><br>
            Text klassifizieren (E-Mail, Rechnung, Vertrag, Sonstiges)<br>
            <small>Body: {{"text": "..."}}</small>
        </div>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/question</code><br>
            Frage zu einem Text stellen<br>
            <small>Body: {{"text": "...", "question": "..."}}</small>
        </div>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/extract-entities</code><br>
            Entitäten extrahieren (Firmen, Beträge, Daten, IBANs)<br>
            <small>Body: {{"text": "..."}}</small>
        </div>
        
        <h2>📁 Datei-Endpunkte</h2>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/upload</code><br>
            Datei hochladen und Text extrahieren<br>
            <small>Form-Data: file=@dokument.pdf</small>
        </div>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/upload/summarize</code><br>
            Datei hochladen und direkt zusammenfassen<br>
            <small>Form-Data: file=@dokument.pdf</small>
        </div>
        
        <div class="endpoint">
            <span class="method method-post">POST</span> <code>/api/upload/analyze</code><br>
            Datei hochladen und komplett analysieren (Zusammenfassung + Klassifikation + Entitäten)<br>
            <small>Form-Data: file=@dokument.pdf</small>
        </div>
        
        <h2>🧪 Test mit cURL</h2>
        <pre>
# Text zusammenfassen
curl -X POST http://localhost:5000/api/summarize \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "Die Firma ABC hat 2024 einen Umsatz von 1 Million Euro erzielt."}}'

# Datei hochladen und analysieren  
curl -X POST http://localhost:5000/api/upload/analyze \\
  -F "file=@dokument.pdf"
        </pre>
    </body>
    </html>
    """


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """Text zusammenfassen."""
    start = time.time()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine JSON-Daten gesendet'}), 400
    
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'Kein Text gesendet'}), 400
    
    # Text kürzen falls zu lang
    text = truncate_text(text, 6000)
    
    prompt = f"""Fasse folgenden Text in 3-4 prägnanten Sätzen auf Deutsch zusammen. 
Fokussiere auf die wichtigsten Fakten: Wer, Was, Wann, Wie viel.

Text:
{text}

Zusammenfassung:"""
    
    result = call_ollama(prompt)
    
    if result['success']:
        log_request('/api/summarize', len(text), len(result['response']), time.time() - start)
        return jsonify({
            'original_length': len(data.get('text', '')),
            'summary': result['response'],
            'model': result['model'],
            'response_time_sec': result['response_time_sec']
        })
    else:
        return jsonify({'error': result['error']}), 500


@app.route('/api/classify', methods=['POST'])
def classify():
    """Text klassifizieren."""
    start = time.time()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine JSON-Daten gesendet'}), 400
    
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'Kein Text gesendet'}), 400
    
    text = truncate_text(text, 4000)
    
    prompt = f"""Klassifiziere den folgenden Text in GENAU EINE dieser Kategorien:
- E-Mail
- Rechnung
- Vertrag
- Protokoll
- Finanzbericht
- Sonstiges

Antworte NUR mit dem Kategorienamen, nichts anderes!

Text:
{text}

Kategorie:"""
    
    result = call_ollama(prompt, max_tokens=50)
    
    if result['success']:
        # Bereinige Antwort
        category = result['response'].strip().split('\n')[0].strip()
        
        log_request('/api/classify', len(text), len(category), time.time() - start)
        return jsonify({
            'category': category,
            'text_length': len(data.get('text', '')),
            'model': result['model'],
            'response_time_sec': result['response_time_sec']
        })
    else:
        return jsonify({'error': result['error']}), 500


@app.route('/api/question', methods=['POST'])
def question():
    """Frage zu Text beantworten."""
    start = time.time()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine JSON-Daten gesendet'}), 400
    
    text = data.get('text', '')
    question_text = data.get('question', '')
    
    if not text:
        return jsonify({'error': 'Kein Text gesendet'}), 400
    if not question_text:
        return jsonify({'error': 'Keine Frage gesendet'}), 400
    
    text = truncate_text(text, 5000)
    
    prompt = f"""Beantworte die folgende Frage basierend NUR auf dem gegebenen Text.
Wenn die Antwort nicht im Text steht, sage "Information nicht im Text gefunden."

Text:
{text}

Frage: {question_text}

Antwort:"""
    
    result = call_ollama(prompt)
    
    if result['success']:
        log_request('/api/question', len(text), len(result['response']), time.time() - start)
        return jsonify({
            'question': question_text,
            'answer': result['response'],
            'model': result['model'],
            'response_time_sec': result['response_time_sec']
        })
    else:
        return jsonify({'error': result['error']}), 500


@app.route('/api/extract-entities', methods=['POST'])
def extract_entities():
    """Entitäten aus Text extrahieren."""
    start = time.time()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine JSON-Daten gesendet'}), 400
    
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'Kein Text gesendet'}), 400
    
    text = truncate_text(text, 4000)
    
    prompt = f"""Extrahiere alle relevanten Entitäten aus dem folgenden Text.

Antworte im folgenden Format (eine Zeile pro Kategorie, "keine" wenn nichts gefunden):
FIRMEN: [Liste]
PERSONEN: [Liste]
GELDBETRAEGE: [Liste]
DATEN: [Liste]
IBANS: [Liste]
STEUERNUMMERN: [Liste]
ORTE: [Liste]

Text:
{text}

Extrahierte Entitäten:"""
    
    result = call_ollama(prompt)
    
    if result['success']:
        # Parse strukturierte Antwort
        entities = parse_entity_response(result['response'])
        
        log_request('/api/extract-entities', len(text), len(result['response']), time.time() - start)
        return jsonify({
            'entities': entities,
            'raw_response': result['response'],
            'model': result['model'],
            'response_time_sec': result['response_time_sec']
        })
    else:
        return jsonify({'error': result['error']}), 500


def parse_entity_response(response: str) -> dict:
    """Parst die strukturierte Entity-Antwort vom LLM."""
    entities = {
        "firmen": [],
        "personen": [],
        "geldbetraege": [],
        "daten": [],
        "ibans": [],
        "steuernummern": [],
        "orte": []
    }
    
    mapping = {
        'FIRMEN': 'firmen',
        'PERSONEN': 'personen',
        'GELDBETRAEGE': 'geldbetraege',
        'GELDBETRÄGE': 'geldbetraege',
        'DATEN': 'daten',
        'IBANS': 'ibans',
        'STEUERNUMMERN': 'steuernummern',
        'ORTE': 'orte'
    }
    
    for line in response.split('\n'):
        line = line.strip()
        for key, field in mapping.items():
            if line.upper().startswith(key):
                value = line.split(':', 1)[-1].strip()
                if value.lower() not in ['keine', 'keine gefunden', '-', '[]', '']:
                    # Parse Liste
                    value = value.strip('[]')
                    items = [item.strip().strip('"\'') for item in value.split(',')]
                    entities[field] = [item for item in items if item and item.lower() != 'keine']
                break
    
    return entities


# =============================================================================
# API ENDPUNKTE - DATEI-UPLOAD
# =============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Datei hochladen und Text extrahieren."""
    
    if 'file' not in request.files:
        return jsonify({'error': 'Keine Datei im Request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Dateityp nicht erlaubt',
            'allowed': list(ALLOWED_EXTENSIONS)
        }), 400
    
    # Datei sicher speichern
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    try:
        file.save(filepath)
        
        # Text extrahieren
        result = process_file(filepath)
        
        # Datei nach Verarbeitung löschen (Datenschutz!)
        os.remove(filepath)
        
        if result['success']:
            return jsonify({
                'success': True,
                'filename': filename,
                'filetype': result['filetype'],
                'char_count': result['char_count'],
                'word_count': result['word_count'],
                'line_count': result.get('line_count', 0),
                'text': result['text'][:10000],  # Max 10k Zeichen zurückgeben
                'metadata': result.get('metadata', {}),
                'truncated': len(result['text']) > 10000
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        # Aufräumen bei Fehler
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Fehler beim Verarbeiten: {str(e)}'}), 500


@app.route('/api/upload/summarize', methods=['POST'])
def upload_and_summarize():
    """Datei hochladen und direkt zusammenfassen."""
    start = time.time()
    
    if 'file' not in request.files:
        return jsonify({'error': 'Keine Datei im Request'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Ungültige Datei'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
    
    try:
        file.save(filepath)
        
        # Text extrahieren
        file_result = process_file(filepath)
        os.remove(filepath)
        
        if not file_result['success']:
            return jsonify(file_result), 400
        
        # Text zusammenfassen
        text = truncate_text(file_result['text'], 6000)
        
        prompt = f"""Fasse das folgende Dokument in 4-5 prägnanten Sätzen zusammen.
Fokussiere auf: Hauptthema, beteiligte Parteien, wichtige Zahlen/Daten, Kernaussagen.

Dokument ({filename}):
{text}

Zusammenfassung:"""
        
        llm_result = call_ollama(prompt)
        
        if llm_result['success']:
            log_request('/api/upload/summarize', file_result['char_count'], 
                       len(llm_result['response']), time.time() - start)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filetype': file_result['filetype'],
                'original_chars': file_result['char_count'],
                'original_words': file_result['word_count'],
                'summary': llm_result['response'],
                'model': llm_result['model'],
                'response_time_sec': llm_result['response_time_sec']
            })
        else:
            return jsonify({'error': llm_result['error']}), 500
            
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/analyze', methods=['POST'])
def upload_and_analyze():
    """
    Datei hochladen und komplett analysieren:
    - Zusammenfassung
    - Klassifikation
    - Entity Extraction
    """
    start = time.time()
    
    if 'file' not in request.files:
        return jsonify({'error': 'Keine Datei im Request'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Ungültige Datei'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
    
    try:
        file.save(filepath)
        
        # Text extrahieren
        file_result = process_file(filepath)
        os.remove(filepath)
        
        if not file_result['success']:
            return jsonify(file_result), 400
        
        text = file_result['text']
        text_for_llm = truncate_text(text, 5000)
        
        # Kombinierter Prompt für Effizienz
        prompt = f"""Analysiere das folgende Dokument und gib eine strukturierte Antwort.

DOKUMENT:
{text_for_llm}

Antworte im folgenden Format:

KATEGORIE: [E-Mail/Rechnung/Vertrag/Protokoll/Finanzbericht/Sonstiges]

ZUSAMMENFASSUNG:
[3-4 Sätze]

FIRMEN: [Liste oder "keine"]
PERSONEN: [Liste oder "keine"]
GELDBETRAEGE: [Liste oder "keine"]
DATEN: [Liste oder "keine"]
AUFFAELLIGKEITEN: [Liste ungewöhnlicher Aspekte oder "keine"]

Analyse:"""
        
        llm_result = call_ollama(prompt, max_tokens=1500)
        
        if llm_result['success']:
            # Parse Antwort
            analysis = parse_full_analysis(llm_result['response'])
            
            log_request('/api/upload/analyze', file_result['char_count'],
                       len(llm_result['response']), time.time() - start)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filetype': file_result['filetype'],
                'file_info': {
                    'char_count': file_result['char_count'],
                    'word_count': file_result['word_count'],
                    'line_count': file_result.get('line_count', 0)
                },
                'analysis': analysis,
                'raw_response': llm_result['response'],
                'model': llm_result['model'],
                'total_time_sec': round(time.time() - start, 2)
            })
        else:
            return jsonify({'error': llm_result['error']}), 500
            
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500


def parse_full_analysis(response: str) -> dict:
    """Parst die vollständige Analyse-Antwort."""
    analysis = {
        "kategorie": "Sonstiges",
        "zusammenfassung": "",
        "firmen": [],
        "personen": [],
        "geldbetraege": [],
        "daten": [],
        "auffaelligkeiten": []
    }
    
    lines = response.split('\n')
    current_section = None
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('KATEGORIE:'):
            analysis['kategorie'] = line.replace('KATEGORIE:', '').strip()
        elif line.startswith('ZUSAMMENFASSUNG:'):
            current_section = 'summary'
        elif line.startswith('FIRMEN:'):
            current_section = None
            value = line.replace('FIRMEN:', '').strip()
            analysis['firmen'] = parse_list_value(value)
        elif line.startswith('PERSONEN:'):
            current_section = None
            value = line.replace('PERSONEN:', '').strip()
            analysis['personen'] = parse_list_value(value)
        elif line.startswith('GELDBETRAEGE:') or line.startswith('GELDBETRÄGE:'):
            current_section = None
            value = line.split(':', 1)[-1].strip()
            analysis['geldbetraege'] = parse_list_value(value)
        elif line.startswith('DATEN:'):
            current_section = None
            value = line.replace('DATEN:', '').strip()
            analysis['daten'] = parse_list_value(value)
        elif line.startswith('AUFFAELLIGKEITEN:') or line.startswith('AUFFÄLLIGKEITEN:'):
            current_section = None
            value = line.split(':', 1)[-1].strip()
            analysis['auffaelligkeiten'] = parse_list_value(value)
        elif current_section == 'summary' and line:
            summary_lines.append(line)
    
    analysis['zusammenfassung'] = ' '.join(summary_lines)
    
    return analysis


def parse_list_value(value: str) -> list:
    """Parst einen Listen-Wert aus der LLM-Antwort."""
    if not value or value.lower() in ['keine', 'keine gefunden', '-', '[]', 'n/a']:
        return []
    
    value = value.strip('[]')
    items = [item.strip().strip('"\'') for item in value.split(',')]
    return [item for item in items if item and item.lower() not in ['keine', '']]


# =============================================================================
# HEALTH CHECK & INFO
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health-Check Endpunkt."""
    # Teste Ollama-Verbindung
    try:
        response = requests.get(f"{OLLAMA_URL.replace('/api/generate', '')}/api/tags", timeout=5)
        ollama_status = "online" if response.status_code == 200 else "offline"
    except:
        ollama_status = "offline"
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'environment': ENVIRONMENT,
        'model': MODEL,
        'ollama_url': OLLAMA_URL,
        'ollama_status': ollama_status,
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })


# =============================================================================
# START
# =============================================================================

if __name__ == '__main__':
    print()
    print("=" * 60)
    print("🔍 STEUERFAHNDUNG KI-FRAMEWORK API")
    print("=" * 60)
    print(f"📍 URL: http://localhost:5000")
    print(f"🤖 Modell: {MODEL}")
    print(f"🌐 Ollama: {OLLAMA_URL}")
    print(f"📁 Upload-Ordner: {UPLOAD_FOLDER}")
    print(f"📎 Formate: {', '.join(ALLOWED_EXTENSIONS)}")
    print("=" * 60)
    print("📝 Drücke STRG+C zum Beenden")
    print()
    
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
