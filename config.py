"""
Konfiguration für Steuerfahndung KI-Framework

Umgebung wechseln:
    - Laptop (Entwicklung): Standard, keine Änderung nötig
    - Arbeits-VM (Produktion): set BA_ENV=production vor dem Start

Oder direkt in dieser Datei die Werte anpassen.
"""

import os

# =============================================================================
# UMGEBUNGSERKENNUNG
# =============================================================================

# Lies Umgebungsvariable oder nutze Standard
ENVIRONMENT = os.getenv('BA_ENV', 'development')

# =============================================================================
# OLLAMA KONFIGURATION
# =============================================================================

if ENVIRONMENT == 'production':
    # ===== ARBEITS-VM EINSTELLUNGEN =====
    OLLAMA_HOST = "10.172.27.248"  # IP der VM mit Ollama
    OLLAMA_PORT = 11434
    MODEL = "llama3.1:70b"         # Großes Modell (mit GPU)
    DEBUG = False
    
else:
    # ===== LAPTOP EINSTELLUNGEN =====
    OLLAMA_HOST = "localhost"
    OLLAMA_PORT = 11434
    MODEL = "llama3.2:3b"          # Kleines Modell (ohne GPU)
    DEBUG = True

# Vollständige URL zusammenbauen
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

# =============================================================================
# API KONFIGURATION
# =============================================================================

API_HOST = "0.0.0.0"  # Auf allen Interfaces lauschen
API_PORT = 5000

# =============================================================================
# DATEI-UPLOAD KONFIGURATION
# =============================================================================

# Maximale Dateigröße in Bytes (32 MB)
MAX_FILE_SIZE = 32 * 1024 * 1024

# Erlaubte Dateiendungen
ALLOWED_EXTENSIONS = {
    'pdf',   # PDF-Dokumente
    'txt',   # Textdateien
    'docx',  # Word 2007+
    'doc',   # Word älter
    'csv',   # Tabellen
    'eml',   # E-Mails
}

# =============================================================================
# LLM KONFIGURATION
# =============================================================================

# Maximale Textlänge für LLM (Zeichen)
MAX_TEXT_LENGTH = 8000

# Timeout für Ollama-Anfragen (Sekunden)
LLM_TIMEOUT = 120

# Standard max_tokens für verschiedene Aufgaben
TOKEN_LIMITS = {
    'summarize': 500,
    'classify': 50,
    'question': 300,
    'entities': 800,
    'analyze': 1500
}

# =============================================================================
# LOGGING
# =============================================================================

# Log-Datei für API-Anfragen
LOG_FILE = "api_log.jsonl"

# Log-Level
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

# =============================================================================
# AUSGABE BEI IMPORT
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("AKTUELLE KONFIGURATION")
    print("=" * 50)
    print(f"Umgebung:     {ENVIRONMENT}")
    print(f"Ollama URL:   {OLLAMA_URL}")
    print(f"Modell:       {MODEL}")
    print(f"API Port:     {API_PORT}")
    print(f"Debug:        {DEBUG}")
    print(f"Max. Datei:   {MAX_FILE_SIZE / 1024 / 1024:.0f} MB")
    print(f"Formate:      {', '.join(ALLOWED_EXTENSIONS)}")
    print("=" * 50)
