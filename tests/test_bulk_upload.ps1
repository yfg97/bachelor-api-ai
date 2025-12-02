# ==============================================================================
# Bulk-Upload Test für Steuerfahndung KI-Framework
# ==============================================================================
#
# Dieses Skript testet den /api/upload/batch Endpunkt mit mehreren Dateien.
# Es simuliert einen Steuerfahnder, der mehrere Beweismittel auf einmal hochlädt.
#
# Voraussetzungen:
# 1. API läuft auf http://localhost:5000
# 2. Testdateien im Ordner "testdaten" vorhanden
#
# Ausführen:
#   .\tests\test_bulk_upload.ps1
#
# ==============================================================================

$API_URL = "http://localhost:5000"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BULK-UPLOAD TEST - Steuerfahndung KI-Framework" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob API läuft
Write-Host "[1/4] Prüfe API-Status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$API_URL/api/health" -Method GET -TimeoutSec 5
    Write-Host "   ✓ API ist online" -ForegroundColor Green
    Write-Host "   Modell: $($health.model)" -ForegroundColor Gray
    Write-Host "   Ollama: $($health.ollama_status)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ API nicht erreichbar!" -ForegroundColor Red
    Write-Host "   Starte die API mit: cd api && python app.py" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Prüfe Testdateien
Write-Host "[2/4] Suche Testdateien..." -ForegroundColor Yellow
$testdatenOrdner = Join-Path $PSScriptRoot "..\testdaten"

if (-not (Test-Path $testdatenOrdner)) {
    Write-Host "   ✗ Ordner 'testdaten' nicht gefunden!" -ForegroundColor Red
    exit 1
}

# Finde alle unterstützten Dateien
$dateien = Get-ChildItem -Path $testdatenOrdner -Include *.pdf,*.txt,*.docx,*.doc,*.csv,*.eml -Recurse

if ($dateien.Count -eq 0) {
    Write-Host "   ✗ Keine Testdateien gefunden!" -ForegroundColor Red
    Write-Host "   Lege PDF, TXT oder DOCX Dateien im Ordner 'testdaten' ab." -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✓ Gefunden: $($dateien.Count) Dateien" -ForegroundColor Green
foreach ($datei in $dateien) {
    $groesse = [math]::Round($datei.Length / 1KB, 1)
    Write-Host "     - $($datei.Name) ($groesse KB)" -ForegroundColor Gray
}
Write-Host ""

# Bulk-Upload durchführen
Write-Host "[3/4] Starte Bulk-Upload..." -ForegroundColor Yellow
Write-Host "   Dies kann einige Minuten dauern (je nach Anzahl der Dateien)..." -ForegroundColor Gray
Write-Host ""

$startzeit = Get-Date

try {
    # Erstelle Multipart Form
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"

    $bodyLines = @()

    foreach ($datei in $dateien) {
        $fileBytes = [System.IO.File]::ReadAllBytes($datei.FullName)
        $fileEnc = [System.Text.Encoding]::GetEncoding('ISO-8859-1').GetString($fileBytes)

        $bodyLines += "--$boundary"
        $bodyLines += "Content-Disposition: form-data; name=`"files`"; filename=`"$($datei.Name)`""
        $bodyLines += "Content-Type: application/octet-stream$LF"
        $bodyLines += $fileEnc
    }

    $bodyLines += "--$boundary--$LF"

    $body = $bodyLines -join $LF

    # Sende Request
    $response = Invoke-RestMethod -Uri "$API_URL/api/upload/batch" `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body ([System.Text.Encoding]::GetEncoding('ISO-8859-1').GetBytes($body)) `
        -TimeoutSec 300

    $endzeit = Get-Date
    $dauer = ($endzeit - $startzeit).TotalSeconds

    Write-Host "   ✓ Upload erfolgreich!" -ForegroundColor Green
    Write-Host "   Dauer: $([math]::Round($dauer, 1)) Sekunden" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host "   ✗ Upload fehlgeschlagen!" -ForegroundColor Red
    Write-Host "   Fehler: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Ergebnisse anzeigen
Write-Host "[4/4] Ergebnisse:" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "STATISTIK:" -ForegroundColor White
Write-Host "  Hochgeladen:  $($response.total_files) Dateien" -ForegroundColor Gray
Write-Host "  Verarbeitet:  $($response.processed) Dateien" -ForegroundColor Green
if ($response.failed -gt 0) {
    Write-Host "  Fehler:       $($response.failed) Dateien" -ForegroundColor Red
}
Write-Host "  Gesamtzeit:   $($response.total_time_sec) Sekunden" -ForegroundColor Gray
Write-Host "  Modell:       $($response.model)" -ForegroundColor Gray
Write-Host ""

# Einzelergebnisse
Write-Host "EINZELANALYSEN:" -ForegroundColor White
foreach ($result in $response.results) {
    if ($result.success) {
        $relevanzFarbe = switch ($result.relevanz.ToLower()) {
            "hoch" { "Red" }
            "mittel" { "Yellow" }
            "gering" { "Gray" }
            default { "White" }
        }

        Write-Host "  ✓ $($result.filename)" -ForegroundColor Green -NoNewline
        Write-Host " [$($result.relevanz)]" -ForegroundColor $relevanzFarbe
        Write-Host "    Kategorie: $($result.analyse.kategorie)" -ForegroundColor Gray

        if ($result.analyse.zusammenfassung) {
            $summary = $result.analyse.zusammenfassung
            if ($summary.Length -gt 80) {
                $summary = $summary.Substring(0, 80) + "..."
            }
            Write-Host "    $summary" -ForegroundColor DarkGray
        }

        if ($result.analyse.firmen.Count -gt 0) {
            Write-Host "    Firmen: $($result.analyse.firmen -join ', ')" -ForegroundColor DarkCyan
        }

        Write-Host ""
    } else {
        Write-Host "  ✗ $($result.filename)" -ForegroundColor Red
        Write-Host "    Fehler: $($result.error)" -ForegroundColor DarkRed
        Write-Host ""
    }
}

# Querverbindungen
if ($response.cross_references.firmen.Count -gt 0 -or
    $response.cross_references.personen.Count -gt 0 -or
    $response.cross_references.geldbetraege.Count -gt 0) {

    Write-Host "QUERVERBINDUNGEN:" -ForegroundColor White

    if ($response.cross_references.firmen.Count -gt 0) {
        Write-Host "  Firmen in mehreren Dokumenten:" -ForegroundColor Cyan
        foreach ($firma in $response.cross_references.firmen.Keys) {
            $docs = $response.cross_references.firmen[$firma] -join ", "
            Write-Host "    • $firma" -ForegroundColor Gray
            Write-Host "      ➜ $docs" -ForegroundColor DarkGray
        }
        Write-Host ""
    }

    if ($response.cross_references.personen.Count -gt 0) {
        Write-Host "  Personen in mehreren Dokumenten:" -ForegroundColor Cyan
        foreach ($person in $response.cross_references.personen.Keys) {
            $docs = $response.cross_references.personen[$person] -join ", "
            Write-Host "    • $person" -ForegroundColor Gray
            Write-Host "      ➜ $docs" -ForegroundColor DarkGray
        }
        Write-Host ""
    }

    if ($response.cross_references.geldbetraege.Count -gt 0) {
        Write-Host "  Geldbeträge in mehreren Dokumenten:" -ForegroundColor Cyan
        foreach ($betrag in $response.cross_references.geldbetraege.Keys) {
            $docs = $response.cross_references.geldbetraege[$betrag] -join ", "
            Write-Host "    • $betrag" -ForegroundColor Gray
            Write-Host "      ➜ $docs" -ForegroundColor DarkGray
        }
        Write-Host ""
    }
}

# Gesamtübersicht
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GESAMTÜBERSICHT:" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host $response.overview -ForegroundColor Gray
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✓ Test abgeschlossen!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
