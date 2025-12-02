# 🔍 Steuerfahndung KI-Framework

**Bachelorarbeit: KI-gestützte Beweismittelsichtung**  
Oberfinanzdirektion Frankfurt am Main

---

## 📋 SCHRITT-FÜR-SCHRITT-PLAN

Dieser Plan führt dich durch alle Schritte, um den Prototypen auf deinem Laptop zu entwickeln und später auf die Arbeits-VM zu übertragen.

---

## PHASE 1: ENTWICKLUNGSUMGEBUNG (Laptop)

### Schritt 1.1: Voraussetzungen prüfen

```powershell
# PowerShell öffnen und prüfen:

# 1. Ollama läuft?
ollama list

# 2. Python installiert?
python --version

# 3. Modell vorhanden?
ollama run llama3.2:3b "Hallo, funktionierst du?"
# Beenden mit: /bye
```

### Schritt 1.2: Projekt-Ordner einrichten

```powershell
# Zum Projekt-Ordner navigieren
cd $HOME\Desktop\BA-Projekt

# Ordnerstruktur sollte so aussehen:
# BA-Projekt/
# ├── api/
# │   ├── app.py              (Flask API)
# │   ├── file_processor.py   (Datei-Verarbeitung)
# │   └── uploads/            (temporäre Uploads)
# ├── tests/
# │   └── test_upload.py      (Test-Skripte)
# ├── evaluation/             (für Nutzwertanalyse)
# └── requirements.txt
```

### Schritt 1.3: Python-Pakete installieren

```powershell
# Alle Abhängigkeiten installieren
pip install -r requirements.txt

# Oder einzeln:
pip install flask flask-cors requests PyMuPDF python-docx
```

### Schritt 1.4: API starten

```powershell
# Im BA-Projekt Ordner:
cd api
python app.py

# Du solltest sehen:
# ============================================================
# 🔍 STEUERFAHNDUNG KI-FRAMEWORK API
# ============================================================
# 📍 URL: http://localhost:5000
# 🤖 Modell: llama3.2:3b
# ...
```

**Lass dieses Fenster offen!**

### Schritt 1.5: API testen

```powershell
# NEUES PowerShell-Fenster öffnen!

# Test 1: Health-Check
Invoke-RestMethod -Uri "http://localhost:5000/api/health"

# Test 2: Text zusammenfassen
$body = @{
    text = "Die Firma ABC GmbH hat am 15.03.2024 eine Zahlung von 100.000 Euro durchgeführt."
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5000/api/summarize" -Method POST -Body $body -ContentType "application/json; charset=utf-8"
```

### Schritt 1.6: Datei-Upload testen

```powershell
# Test-Datei erstellen
$testContent = @"
TESTDOKUMENT: Verdächtige Transaktion

Am 15.03.2024 überwies die ABC GmbH (Steuernummer: 012/345/67890) 
einen Betrag von 150.000 Euro an die XYZ Holdings Ltd. auf den Cayman Islands.
IBAN: DE89 3704 0044 0532 0130 00
Geschäftsführer: Hans Müller (h.mueller@abc-gmbh.de)
"@

$testContent | Out-File -FilePath "test.txt" -Encoding UTF8

# Datei analysieren lassen
$filePath = (Get-Item "test.txt").FullName
Invoke-RestMethod -Uri "http://localhost:5000/api/upload/analyze" -Method POST -Form @{file = Get-Item $filePath}

# Aufräumen
Remove-Item "test.txt"
```

---

## PHASE 2: FUNKTIONEN ERWEITERN

### Schritt 2.1: Mit echter Testdatei testen

```powershell
# Deine rfc822.txt Datei testen
$filePath = "C:\Pfad\zu\deiner\rfc822.txt"
Invoke-RestMethod -Uri "http://localhost:5000/api/upload/analyze" -Method POST -Form @{file = Get-Item $filePath}
```

### Schritt 2.2: PDF testen (wenn vorhanden)

```powershell
# PDF-Datei analysieren
$pdfPath = "C:\Pfad\zu\dokument.pdf"
Invoke-RestMethod -Uri "http://localhost:5000/api/upload/summarize" -Method POST -Form @{file = Get-Item $pdfPath}
```

### Schritt 2.3: Test-Suite ausführen

```powershell
# Zurück zum BA-Projekt Ordner
cd $HOME\Desktop\BA-Projekt

# Test-Suite starten
python tests\test_upload.py
```

---

## PHASE 3: EVALUATION (für BA)

### Schritt 3.1: Evaluation-Framework erstellen

Erstelle `evaluation/evaluator.py` mit Metriken für:
- Antwortzeit
- Genauigkeit (manuell bewerten)
- Token-Verbrauch

### Schritt 3.2: Test-Datensatz anlegen

Erstelle 20-30 anonymisierte Test-Dokumente:
- 5x E-Mails
- 5x Rechnungen
- 5x Verträge
- 5x Sonstige Dokumente

### Schritt 3.3: Modellvergleich

```powershell
# Verschiedene Modelle herunterladen
ollama pull mistral:7b
ollama pull qwen2.5:7b

# In app.py das Modell ändern und Tests wiederholen
```

---

## PHASE 4: TRANSFER AUF ARBEITS-VM

### Schritt 4.1: Projekt kopieren

```powershell
# Ganzen Ordner auf USB-Stick oder Netzlaufwerk kopieren
Copy-Item -Path "$HOME\Desktop\BA-Projekt" -Destination "E:\BA-Projekt" -Recurse
```

### Schritt 4.2: Auf VM konfigurieren

```powershell
# Auf der VM: Umgebungsvariable setzen
$env:BA_ENV = "production"

# API starten
cd E:\BA-Projekt\api
python app.py

# Modell wird automatisch auf llama3.1:70b gesetzt
# Ollama-URL wird auf 10.172.27.248 gesetzt
```

### Schritt 4.3: Verbindung testen

```powershell
# Von anderem Rechner im Netzwerk:
Invoke-RestMethod -Uri "http://[VM-IP]:5000/api/health"
```

---

## 📁 PROJEKTSTRUKTUR

```
BA-Projekt/
├── api/
│   ├── app.py                 # Haupt-API (Flask)
│   ├── file_processor.py      # Datei-Extraktion
│   ├── uploads/               # Temporäre Uploads (wird automatisch geleert)
│   └── api_log.jsonl          # Request-Logging
│
├── tests/
│   ├── test_upload.py         # Upload-Tests
│   └── test_data/             # Test-Dokumente
│
├── evaluation/
│   ├── evaluator.py           # Metriken & Benchmark
│   ├── test_cases.py          # Testfälle mit Ground-Truth
│   └── results/               # Ergebnisse (CSV, JSON)
│
├── docs/
│   ├── architektur.md         # Für BA
│   └── api-dokumentation.md   # Für BA
│
├── requirements.txt           # Python-Abhängigkeiten
├── config.py                  # Konfiguration (optional)
└── README.md                  # Diese Datei
```

---

## 🔧 API-ENDPUNKTE

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/health` | GET | Status-Check |
| `/api/summarize` | POST | Text zusammenfassen |
| `/api/classify` | POST | Text klassifizieren |
| `/api/question` | POST | Frage zu Text |
| `/api/extract-entities` | POST | Entitäten extrahieren |
| `/api/upload` | POST | Datei → Text |
| `/api/upload/summarize` | POST | Datei → Zusammenfassung |
| `/api/upload/analyze` | POST | Datei → Vollanalyse |

---

## 🐛 PROBLEMLÖSUNG

### "Ollama nicht erreichbar"
```powershell
# Ollama starten
ollama serve

# In neuem Fenster prüfen
ollama list
```

### "Modul nicht gefunden"
```powershell
pip install PyMuPDF python-docx flask flask-cors requests
```

### "Datei konnte nicht gelesen werden"
- Prüfe ob Dateiformat unterstützt wird (.pdf, .txt, .docx, .csv, .eml)
- Prüfe Dateigröße (max. 32 MB)

### "Timeout bei großen Dateien"
- Text wird automatisch auf 6000 Zeichen gekürzt
- Bei sehr großen PDFs dauert Extraktion länger

---

## 📊 FÜR DIE BACHELORARBEIT

### Wichtige Metriken sammeln:
1. **Antwortzeit** pro Endpunkt (wird in `api_log.jsonl` gespeichert)
2. **Genauigkeit** der Zusammenfassungen (manuell bewerten)
3. **Recall** der Entity Extraction (wie viele gefunden?)
4. **Ressourcenverbrauch** (RAM, CPU während Verarbeitung)

### Screenshots für BA:
- [ ] API-Startbildschirm
- [ ] Beispiel-Anfrage in PowerShell
- [ ] Beispiel-Antwort mit Zusammenfassung
- [ ] Entity Extraction Ergebnis
- [ ] Health-Check Ausgabe

---

## ✅ CHECKLISTE

- [ ] Ollama läuft mit llama3.2:3b
- [ ] Python-Pakete installiert
- [ ] API startet ohne Fehler
- [ ] Health-Check funktioniert
- [ ] Text-Zusammenfassung funktioniert
- [ ] Datei-Upload funktioniert
- [ ] Test-Suite läuft durch
- [ ] Eigene Test-Dokumente erstellt
- [ ] Evaluation-Framework eingerichtet
- [ ] Transfer auf Arbeits-VM geplant
