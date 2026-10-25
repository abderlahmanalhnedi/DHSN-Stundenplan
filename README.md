# 🎓 DHSN Stundenplan for Home Assistant

**Deutsch** · [English](#english) | **Status:** Experimental / Community integration

A simple, **unofficial**, read-only timetable calendar for [Home Assistant](https://www.home-assistant.io/). Enter your seminar group once; your upcoming lectures appear in the Home Assistant calendar.

> **Independent open-source project.** Not affiliated with, sponsored by or supported by DHSN, Campus Dual, or the university timetable operator. **The publisher has not yet confirmed permission for automated requests.** Please comply with the service's terms and stop using automated fetching if the operator objects.

## Deutsch

### Funktionen
- **Nur Seminargruppe eingeben** (z. B. `3spXX-1`) – keine YAML-Konfiguration.
- Erstellt automatisch einen Kalender in Home Assistant.
- Zeigt **Fächer, Datum/Uhrzeit, Räume und Dozenten** an, soweit die Quelle sie bereitstellt.
- **Automatischer Abgleich alle 60 Minuten**; keine externe Cloud oder zusätzlicher Server erforderlich.
- **Schreibgeschützt:** keine Änderungen am Hochschul-Stundenplan.
- Keine Zugangsdaten, Cookies, Tokens, Tracking oder zentral gespeicherten Stundenpläne.

### Installation über HACS
1. In Home Assistant **HACS** öffnen.
2. Das Menü **⋮ → Benutzerdefinierte Repositories / Custom repositories** öffnen.
3. **`https://github.com/abderlahmanalhnedi/DHSN-Stundenplan`** eingeben; Kategorie **Integration** wählen und hinzufügen.
4. Nach **DHSN Stundenplan** suchen und **Herunterladen / Download** anklicken.
5. **Home Assistant neu starten.**
6. **Einstellungen → Geräte & Dienste → Integration hinzufügen → DHSN Stundenplan** wählen.
7. Eigene **Seminargruppe** eingeben und bestätigen.

Fertig! Der Kalender erscheint automatisch als Entität, etwa `calendar.stundenplan_3sp26_1` (die tatsächliche Entitäts-ID kann abweichen). Öffne **Kalender** und aktiviere ihn.

**Für Dashboard-Nutzer:** Die Standard-Kalenderkarte oder `custom:calendar-card-pro` kann diese Kalender-Entität anzeigen. Wenn die nächsten Vorlesungen erst in mehreren Wochen stattfinden, muss der Anzeigezeitraum entsprechend erweitert werden (z. B. `days_to_show: 90`).

### Einschränkungen & Sicherheit
- Benötigt eine erreichbare Stundenplanquelle. Wenn die Universität Zugriff oder Schnittstelle ändert, können Updates fehlschlagen.
- Kein offizieller API-Vertrag; Verfügbarkeit und Korrektheit werden nicht garantiert. Änderungen immer im offiziellen Stundenplan prüfen.
- Abrufe erfolgen **direkt von deiner Home-Assistant-Instanz** zum Stundenplanserver. Seminargruppenkennungen werden dabei als Teil der Anfrage übertragen.
- Diese Integration umgeht **keine** Authentifizierung, Bezahlschranken oder Zugangsbeschränkungen.
- Bitte **keine HAR-Dateien, Cookies, Zugangsdaten, Tokens oder echten Stundenplandaten** in öffentlichen GitHub-Issues posten.

### Support
Fehler oder Verbesserungsvorschläge: [GitHub Issues](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/issues). Bitte nur nicht-sensitive Logs und eine anonymisierte Beschreibung teilen.

---

## English

### Features
- **Enter only your seminar group** (e.g. `3spXX-1`); no YAML required.
- Creates a native **Home Assistant calendar** automatically.
- Shows **subjects, lecture times, rooms and lecturers** when provided by the timetable.
- **Automatic synchronization every 60 minutes**, directly from Home Assistant; no extra server required.
- Read-only; does not modify university schedules.
- No credentials, cookies, login tokens, telemetry or centralized timetable storage.

### Install with HACS
1. Open **HACS** in Home Assistant.
2. Open **⋮ → Custom repositories**.
3. Enter **`https://github.com/abderlahmanalhnedi/DHSN-Stundenplan`**, select **Integration**, and add it.
4. Find **DHSN Stundenplan** in HACS and click **Download**.
5. **Restart Home Assistant.**
6. Go to **Settings → Devices & services → Add integration → DHSN Stundenplan**.
7. Enter your **seminar group** and submit.

Done! A calendar entity is created automatically (e.g. `calendar.stundenplan_3sp26_1`; your actual entity ID may differ). Enable it in the **Calendar** dashboard.

For dashboard cards that only show upcoming days, increase their display window if the next lecture is farther away (e.g. `days_to_show: 90` in Calendar Card Pro).

### Limitations & privacy
- Requires an accessible timetable source. No guaranteed or official API; changes to the source may break synchronization.
- Requests go directly from your Home Assistant system to the timetable operator and include your seminar group identifier.
- Does **not** bypass authentication or access controls.
- Verify important schedule changes against the official portal.
- Never upload HAR captures, cookies, tokens, credentials, or real timetable exports to public Issues.

### Help
Report bugs or suggestions in [GitHub Issues](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/issues) using sanitized, non-sensitive information.

---

## Development / Entwicklung
Source: `custom_components/dhsn_stundenplan/` · Synthetic offline tests: `tests/`. HACS and hassfest validation run using GitHub Actions. This is an experimental community project; please test carefully before relying on it.

## License / Lizenz
[MIT](LICENSE) applies to the original project code only. University timetable content, institutional names, designs and trademarks are not licensed by this repository.
