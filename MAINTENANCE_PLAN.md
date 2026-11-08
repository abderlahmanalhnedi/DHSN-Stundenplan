# DHSN-Stundenplan – Wartungsplan / Maintenance Roadmap

**Stand: 2026-11-08** · Projekt: inoffizielle Home-Assistant-Integration für die Duale Hochschule Sachsen (DHSN), derzeit **nur Dresden verifiziert** · Beta 0.x · Keine bestätigte Genehmigung des Stundenplanbetreibers für automatisierte Anfragen.

## 1. Gesicherte Befunde (keine Hypothese als Ursache ausgeben)

| Transport | User-Agent | HTTP | Plan-Tabellen | erkannte Wochen | Termine |
| --- | --- | ---: | ---: | ---: | ---: |
| urllib | Mozilla/5.0 | 200 | 8 | 8 | 62 |
| aiohttp | Standard | 200 | 3 | 3 | 10 |
| aiohttp | Mozilla/5.0 | 200 | 1 | 1 | 0 |

Die Tests liefen zu verschiedenen Zeiten. **Weder User-Agent noch Server-/Session-Verhalten sind als alleinige Ursache nachgewiesen**. Der Parser lieferte jeweils konsistent die Inhalte des erhaltenen HTML. Keine weiteren wiederholten Live-Proben erzwingen; keinen automatischen Canary aktivieren, bevor der Betreiber dies erlaubt.

## 2. Ist-Zustand im Repository

- `custom_components/dhsn_stundenplan/__init__.py`: bereits `DataUpdateCoordinator`, ein Abruf pro 60 Minuten und Konfigurations-Eintrag, beschränkte Antwortgröße, Timeouts, privater Last-known-good-Snapshot.
- `parse.py`: BeautifulSoup, Kalenderereignisse und Validierungsgründe, aber abhängig vom externen HTML-Format. Inhaltlich verkürzte HTTP-200-Antworten können trotz gültigem Parsergebnis auftreten.
- `config_flow.py`: bisher nur Seminargruppe; dieser Entwurfs-PR fügt bei **neuen** Setups eine explizite Bestätigung der Zugriffsregeln hinzu. Bestehende Nutzer erhalten keinen Zwang zur Neueinrichtung.
- `calendar.py`, `sensor.py`: etablierte `unique_id`s und Sync-/Zeitstempel-Sensoren. Keine Umbenennung bei Wartungsarbeiten.
- `tests/test_parser.py`: nur synthetische Offline-Tests. CI mit HACS/hassfest/Unittest; keine vollständigen HA-Laufzeittests.
- `README.md`, `NOTICE.md`, `PRIVACY.md`, `PUBLICATION_CHECKLIST.md`: rechtliche Einordnung, Datenflüsse, fehlende Erlaubnis dokumentiert.

## P0 – **Jetzt im Draft PR**: Richtigkeit und Schutz

- [x] Nicht belegten Browser-User-Agent-Fix aus dem **Produktivpfad** entfernen; optionaler Diagnosevergleich bleibt als isoliertes Skript erhalten.
- [x] HTTP-200 mit leerem Kalender **nicht** als erfolgreiche Synchronisierung behandeln; letzten gültigen Snapshot behalten. Bereits gespeicherte, aber unvollständige 10 Termine lassen sich dadurch nicht rückwirkend korrigieren.
- [x] Sichere Diagnosezähler für gelesene Tabellen, Termine, HTTP-Status und Fehlertyp (keine HTML-Seiten, Tokens, Dozentennamen oder vollständigen URLs ausgeben).
- [x] Explizite Bestätigung bei **neuen** ConfigFlows; keine Veränderung der bestehenden Dresden-ConfigEntries.
- [x] Reproduzierbare rein synthetische Tests für eine leere Woche sowie acht Wochen.
- [ ] PR-CI, HACS und hassfest kontrollieren; in sauberer Home-Assistant-Testumgebung verifizieren.
- [ ] Operatorregelung zur automatischen Abfrage klären; keine offizielle Freigabe behaupten.

## P1 – HTTP-Rücksichtnahme / Netzwerk (separater PR)

1. Hochschule/Betreiber nach offiziell erlaubten Zugriffen, Aktualisierungsrate und ggf. ICS/CalDAV/API fragen; Antwort dokumentieren.
2. Auf `401/403` automatische Anfragen stoppen, eine verständliche Repair-Meldung anbieten und erst nach bewusster Bestätigung wieder starten; keine Schutzmaßnahmen umgehen.
3. `429` und `Retry-After` respektieren; bei 5xx exponentielles Backoff und **nicht unter** 60 Minuten fallen; positive Jitter-Zeit zur Entzerrung nutzen.
4. `ETag`/`Last-Modified` nur falls vom Betreiber unterstützt; `304` muss die letzte verifizierte Version erhalten. Bedingte Requests senken normalerweise Übertragungsvolumen, **nicht** die Anzahl der Requests.
5. Alle Anforderungen mit simulierten HTTP-Antworten testen; kein automatischer Live-CI-Workflow gegen Universitätssysteme.

Dateien: HTTP-Schicht aus `__init__.py` in `client.py`/ `coordinator.py` extrahieren; `tests/test_client.py`, `tests/test_coordinator.py`.

## P2 – Parser und Architektur (separater PR)

- HTTP Client, reinem HTML-Parser und optionalen standortspezifischen Adaptern trennen. **Nur Dresden** als verifiziert darstellen.
- Strukturvalidierung für Wochenüberschriften, Wochentage, Kurszellen, Zeitzonen, Terminzeiten und Mehrwochen-Konsistenz. Keine allgemein gültige Mindest-Wochenzahl erfinden.
- Zwischen "offiziell leer", "vorübergehend verkürzt" und "kaputtes HTML" erst unterscheiden, wenn ein verlässliches Signal existiert. Bis dahin `stale` plus ursprünglichen Cache zeigen.
- Echte Fixtures **nur nach Berechtigung**, vollständig anonymisiert (keine Lehrenden, Räume, Gruppenkennungen, persönliche Hinweise); ansonsten ausschließlich synthetische Daten.
- `pytest` + `pytest-homeassistant-custom-component` für `config_flow`, `coordinator`, `calendar`, Wiederherstellung, Migration und Deinstallation. Snapshot-Tests ohne Live-Netz.
- `diagnostics.py` mit kompletter Redaction sensibler Informationen; HA Repairs für wiederholte Fehler.

Dateien: `parse.py`, `client.py`, `coordinator.py`, `config_flow.py`, `diagnostics.py`, `tests/test_parser.py`, `tests/test_config_flow.py`, `tests/test_coordinator.py`.

## P3 – Dokumentation, Veröffentlichung, Rollback

- README DE/EN, Datenschutz, Rechte, bekannte Einschränkungen und Kompatibilitätstabelle: Dresden **getestet**, andere Standorte **nicht verifiziert**.
- `0.x` als Beta kennzeichnen; keine Zuverlässigkeitsversprechen ohne Belege.
- Installation via HACS, Altinstallation/Upgrade von v0.2.6, Cache, Fehlschlag/Teilantwort, Neustart, Deaktivieren und Entfernen mit simuliertem Netz testen.
- GitHub CI: HACS Action, hassfest, pytest, keine deaktivierten Checks; Release Notes + konsistente Version `manifest.json`, Tag und Release.
- Sicherer Rollback: Home Assistant Backup vor dem Update; letzte veröffentlichte HACS-Version wieder installieren; bestehende Entitäts-IDs und Cache-Schlüssel erhalten.
- Vor Freigabe prüfen: Genehmigungsstatus, keine personenbezogenen echten Fixtures, 401/403-Schutz, keine Erhöhung der Serverlast, funktionierender Rollback.

## Wie Informationen beschaffen?

| Quelle | Gesucht | Vorbehalt |
| --- | --- | --- |
| GitHub Repository/Actions | Manifest, Workflow, Fehler, Änderungen | Keine Live-Serverdaten |
| [HA-Developer-Dokumentation](https://contributors.home-assistant.io/architecture/core/data-updates/) | Coordinator, Tests, Diagnostics, Repairs | API-Version prüfen |
| [HACS-Integration](https://hacs.dev/docs/publish/integration/) | HACS- und hassfest-Anforderungen | CI ist kein Laufzeittest |
| Hochschul-IT / Betreiber | Vertragliche Erlaubnis, ICS/API, Intervall | **Noch keine Zusage** |
| Lokaler isolierter HA-Test | Update, Stale-Zustände, Migration | Stub-/Fixture-HTTP, kein Scraping |

**Release Gate:** Kein neuer öffentlicher Fix-Release allein aufgrund grüner CI; erst ein verifizierter Wiederherstellungspfad mit vollständiger Multiweek-Antwort, reproduzierbare Offline-Tests, rückwärtskompatibler HA-Test und geklärte Nutzungsvorgaben.
