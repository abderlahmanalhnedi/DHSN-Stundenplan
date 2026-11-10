# 🎓 DHSN Stundenplan for Home Assistant

![DHSN Stundenplan – calendar and clock icon](custom_components/dhsn_stundenplan/brand/icon.png)

**Unofficial community integration for Duale Hochschule Sachsen (DHSN) / Inoffizielle Community-Integration für die Duale Hochschule Sachsen (DHSN)**

[![Open repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=abderlahmanalhnedi&repository=DHSN-Stundenplan&category=integration)
[![Add integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dhsn_stundenplan)

[![Validate](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/actions/workflows/validate.yml/badge.svg)](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/actions/workflows/validate.yml)
[![GitHub Issues](https://img.shields.io/badge/Report%20a%20bug-GitHub-blue?logo=github)](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/issues/new?template=bug_report.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

**Quick links / Direktlinks:** [HACS installation](#installation-über-hacs) · [English setup](#install-with-hacs) · [Privacy / Datenschutz](PRIVACY.md) · [Legal notice / Rechtliches](NOTICE.md)

> **HACS default repository / Standard-Katalog:** DHSN Stundenplan is listed in the official HACS catalog. **Search for "DHSN Stundenplan" directly in HACS** and download it. The HACS button above is an optional direct shortcut to the repository page, **not a required custom-repository setup**. / **Suche in HACS direkt nach „DHSN Stundenplan“** und lade die Integration herunter. Der HACS-Button oben ist nur ein optionaler Direktlink.

**Deutsch** · [English](#english) | **Status:** Experimental / Community integration

A simple, **unofficial**, read-only timetable calendar for [Home Assistant](https://www.home-assistant.io/). Enter your seminar group once; your upcoming lectures appear in the Home Assistant calendar.

> **Independent open-source project.** Not affiliated with, sponsored by or supported by DHSN, Campus Dual, or the university timetable operator. **The publisher has not yet confirmed permission for automated requests.** Please comply with the service's terms and stop using automated fetching if the operator objects.

## Projektstatus / Project status

**Die Duale Hochschule Sachsen (DHSN) hat diese Integration nicht beauftragt, genehmigt oder unterstützt.** Das Projekt ist nicht mit der Hochschule, Campus Dual oder dem Betreiber des Stundenplans verbunden. Die Verwendung des Hochschulnamens dient nur zur Identifizierung des Anwendungsbereichs. Es werden weder offizielle Logos noch kopierte Stundenpläne veröffentlicht. Derzeit liegt **keine bestätigte Erlaubnis für automatisierte Anfragen** vor; die geltenden Nutzungsbedingungen sind zu beachten. Ein öffentlich erreichbarer Endpunkt bedeutet nicht automatisch eine Erlaubnis zum Polling.

**Independent and unofficial.** This project is not commissioned, approved, affiliated with or supported by Duale Hochschule Sachsen, Campus Dual or the timetable operator. University names are used only for factual identification. **Authorization for automated timetable polling has not been confirmed.** Public accessibility alone does not establish permission. See [Legal notice](NOTICE.md), [Privacy](PRIVACY.md) and [Publication checklist](PUBLICATION_CHECKLIST.md).

## Deutsch

Diese Integration richtet sich an Studierende der **Dualen Hochschule Sachsen (DHSN)**. Die Entwicklung und ein erster lokaler Test basieren auf dem Stundenplansystem des Standorts Dresden. Andere Standorte sind **nicht nachweislich unterstützt**.

### Funktionen
- **Nur Seminargruppe eingeben** (z. B. `3spXX-1`) – keine YAML-Konfiguration.
- Erstellt automatisch einen Kalender in Home Assistant.
- Zeigt **Fächer, Datum/Uhrzeit, Räume und Dozenten** an, soweit die Quelle sie bereitstellt.
- **Automatischer Abgleich alle 60 Minuten**; keine externe Cloud oder zusätzlicher Server erforderlich.
- **Letzter gültiger Stundenplan bleibt erhalten**, wenn die Hochschule vorübergehend nicht antwortet, auch nach einem Home-Assistant-Neustart (privater lokaler Cache).
- **Zwei Diagnose-Sensoren**: `Stundenplan ... Sync-Status` (`up_to_date` oder `stale`) und `Stundenplan ... Letzte erfolgreiche Synchronisierung` (Zeitstempel).
- **Schreibgeschützt:** keine Änderungen am Hochschul-Stundenplan.
- Keine Zugangsdaten, Cookies, Tokens, Tracking oder zentral gespeicherten Stundenpläne.

### Installation über HACS

**Standardinstallation (empfohlen — keine benutzerdefinierte Repository-URL nötig):**

1. In Home Assistant **HACS** öffnen.
2. Nach **DHSN Stundenplan** suchen.
3. Die Integration auswählen und auf **Herunterladen / Download** klicken.
4. **Home Assistant neu starten.**
5. **Einstellungen → Geräte & Dienste → Integration hinzufügen → DHSN Stundenplan** wählen.
6. Die eigene **Seminargruppe** eingeben und bestätigen.

Fertig! Der Kalender erscheint automatisch als Entität, etwa `calendar.stundenplan_3spxx_1` (die tatsächliche Entitäts-ID kann abweichen). Unter **Kalender** kannst du ihn einblenden.

**Direktlinks:** [DHSN Stundenplan in HACS öffnen](https://my.home-assistant.io/redirect/hacs_repository/?owner=abderlahmanalhnedi&repository=DHSN-Stundenplan&category=integration) · [Integration konfigurieren](https://my.home-assistant.io/redirect/config_flow_start/?domain=dhsn_stundenplan)

<details>
<summary>Wenn die Integration in der HACS-Suche noch nicht angezeigt wird</summary>

Prüfe, ob HACS seine Repository-Daten aktualisiert hat, und versuche die Suche erneut. Nur falls weiterhin nötig: **HACS → ⋮ → Benutzerdefinierte Repositories / Custom repositories** öffnen, `https://github.com/abderlahmanalhnedi/DHSN-Stundenplan` mit Kategorie **Integration** hinzufügen und danach herunterladen. Diese manuelle Methode ist seit der Aufnahme in den HACS-Katalog normalerweise **nicht erforderlich**.

</details>

**Bestehende manuelle Installation:** Vor dem Wechsel auf HACS bitte die Home-Assistant-Konfiguration sichern. Nicht zwei Kopien von `dhsn_stundenplan` parallel installieren. Die Migration bestehender Konfigurationen wurde noch nicht umfassend getestet.

**Sicherheitsregel ab v0.2.6:** Ein vermeintlich erfolgreich abgerufenes HTML mit **null erkannten Terminen** gilt nicht mehr als erfolgreiche Synchronisierung. Solche Antworten werden nicht mehr über den letzten gültigen Stundenplan geschrieben. In den Attributen des Kalenders und des Sync-Status-Sensors erscheint `event_count` zur Diagnose. Das verhindert, dass ein verändertes HTML-Layout den gespeicherten Stundenplan unbemerkt durch eine leere Liste ersetzt. **Einschränkung:** Auch ein tatsächlich komplett leerer Plan wird vorsichtshalber als `stale`/Fehler angezeigt, bis sich ein eindeutiger Leerplan sicher erkennen lässt. Wurde der alte Cache bereits unter v0.2.5 durch einen leeren überschrieben, kann er nicht automatisch aus diesem Cache zurückgeholt werden.

**Bei Ausfällen wichtig:** Der Kalender zeigt weiter die letzte erfolgreich heruntergeladene Version an. **Die angezeigten Termine können veraltet sein** (auch ausgefallene oder verschobene Vorlesungen). Der Sync-Status wechselt bei einem fehlgeschlagenen Abruf zu `stale`. Prüfe bei Zweifeln den Original-Stundenplan. Bei einer erstmaligen Einrichtung ohne einen erfolgreichen Abruf steht noch kein Cache zur Verfügung. Die lokale Kopie wird im privaten Home-Assistant-Speicher `.storage` verwahrt; sie wird beim Entfernen des Integrationseintrags gelöscht. Bereits erstellte Backups sind davon ausgenommen.

**Für Dashboard-Nutzer:** Die Standard-Kalenderkarte oder `custom:calendar-card-pro` kann diese Kalender-Entität anzeigen. Wenn die nächsten Vorlesungen erst in mehreren Wochen stattfinden, muss der Anzeigezeitraum entsprechend erweitert werden (z. B. `days_to_show: 90`).

### Verantwortungsvolle Nutzung

- Automatisierte Abrufe bitte nur durchführen, wenn die Hochschule bzw. der zuständige Betreiber diese Nutzung erlaubt. Vor öffentlicher Bewerbung sollte eine schriftliche Klärung erfolgen.
- Wenn der Betreiber den Zugriff untersagt oder einschränkt, die Integration **sofort deaktivieren**.
- Keine automatisierten Massenabfragen, keine systematische Suche nach Seminargruppen und keine Mehrfachinstallationen für dieselbe Gruppe.
- Standardmäßig erfolgt eine direkte Abfrage etwa **einmal pro Stunde je Integration**. Ein Serverbetreiber kann IP-Adresse, Gruppenkennung und Anfragezeitpunkt sehen.
- Details: [Rechtliche Hinweise](NOTICE.md) · [Datenschutz](PRIVACY.md) · [Sicherheit](SECURITY.md).

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

This integration is intended for students of **Duale Hochschule Sachsen (DHSN)**. It has initially been tested with the timetable service used by the **Dresden campus**; compatibility with other DHSN locations is **not verified**.

### Features
- **Enter only your seminar group** (e.g. `3spXX-1`); no YAML required.
- Creates a native **Home Assistant calendar** automatically.
- Shows **subjects, lecture times, rooms and lecturers** when provided by the timetable.
- **Automatic synchronization every 60 minutes**, directly from Home Assistant; no extra server required.
- Read-only; does not modify university schedules.
- No credentials, cookies, login tokens, telemetry or centralized timetable storage.

### Install with HACS

**Recommended installation (now in the default HACS catalog — no custom repository required):**

1. Open **HACS** in Home Assistant.
2. Search for **DHSN Stundenplan**.
3. Select the integration and click **Download**.
4. **Restart Home Assistant.**
5. Go to **Settings → Devices & services → Add integration → DHSN Stundenplan**.
6. Enter your **seminar group** and submit.

Done! The integration automatically creates a calendar entity (for example `calendar.stundenplan_3spxx_1`; your actual entity ID may differ). Enable it on the **Calendar** dashboard.

**Shortcuts:** [Open DHSN Stundenplan in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=abderlahmanalhnedi&repository=DHSN-Stundenplan&category=integration) · [Set up integration](https://my.home-assistant.io/redirect/config_flow_start/?domain=dhsn_stundenplan)

<details>
<summary>If you cannot find the integration in HACS search yet</summary>

Let HACS refresh its catalog and search again. Only if necessary, open **HACS → ⋮ → Custom repositories**, add `https://github.com/abderlahmanalhnedi/DHSN-Stundenplan` as an **Integration**, and download it. This fallback is **normally unnecessary** because the repository is included in the HACS default catalog.

</details>

**Migrating a manual installation:** Back up Home Assistant first; do not install duplicate `dhsn_stundenplan` copies. Migrating existing configurations has not been fully tested yet.

For dashboard cards that only show upcoming days, increase their display window if the next lecture is farther away (e.g. `days_to_show: 90` in Calendar Card Pro).

### Responsible use

- Only poll the timetable service where automated access is permitted by the relevant operator. Written clarification is recommended before wide promotion.
- **Disable the integration immediately** if the service operator objects or restricts automated access.
- Do not enumerate group codes, bulk scrape timetables or install duplicate integrations for the same group.
- Normally one direct request is made **per hour per integration**. The receiving server may log IP address, seminar-group identifier and request time.
- See [Legal notice](NOTICE.md), [Privacy](PRIVACY.md) and [Security](SECURITY.md).

### Limitations & privacy
- Requires an accessible timetable source. No guaranteed or official API; changes to the source may break synchronization.
- Requests go directly from your Home Assistant system to the timetable operator and include your seminar group identifier.
- Does **not** bypass authentication or access controls.
- Verify important schedule changes against the official portal.
- Never upload HAR captures, cookies, tokens, credentials, or real timetable exports to public Issues.

### Help
Report bugs or suggestions in [GitHub Issues](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/issues) using sanitized, non-sensitive information.

---

## Icon / Symbol

Home Assistant 2026.3+ supports local integration branding through `custom_components/dhsn_stundenplan/brand/icon.png` (and optionally `icon@2x.png`). If the icon appears correctly in **Settings → Devices & services** but HACS still shows **“Icon not available”**, this may be a [known HACS frontend issue](https://github.com/hacs/integration/issues/5402) affecting local brand assets. This is not a timetable synchronization error.

**Deutsch:** Das Integrationssymbol wird lokal mitgeliefert. Falls nur HACS „Icon not available“ anzeigt, kann dies an einem bekannten Darstellungsproblem von HACS liegen, nicht an der Integration selbst.

### Release v0.2.8 – More reliable multiweek retrieval (experimental)

**Deutsch:** Version `v0.2.8` ersetzt den bisherigen `aiohttp`-Abruf durch **einen einzelnen `urllib`-HTTPS-Abruf im Home-Assistant-Executor**. Ein Nutzervergleich am 8. November 2026 zeigte für `urllib` einen vollständigen 8-Wochen-Plan mit 62 Terminen, während `aiohttp` nur 1–3 Wochen zurücklieferte. Dieser Ansatz ist aussichtsreicher, aber **noch nicht live auf der Home-Assistant-Instanz verifiziert**. HTTP-200-Antworten mit weniger als vier erkannten Wochentabellen werden zum Schutz der gespeicherten Termine verworfen und als `stale` gemeldet. Ein tatsächlich kürzerer Plan kann damit ebenfalls als `stale` gelten. Keine zusätzlichen automatischen Abfragen, keine Änderungen an Entitäts-IDs oder Cache-Schlüsseln. **Der Web-Endpunkt lieferte im Test acht Wochen, nicht unbegrenzt viele Monate.** Für einen längeren Zeitraum wäre ein offizieller iCal-/ICS-Link vorzuziehen, sofern der Hochschulbetreiber diesen für Dresden anbietet und freigibt.

**English:** `v0.2.8` uses **one bounded `urllib` request executed in Home Assistant's executor** instead of `aiohttp`, matching the transport that returned eight weeks / 62 events in the user's controlled test. Runtime success on the actual Home Assistant host is not yet proven. Short HTTP-200 responses containing fewer than four recognized weeks are rejected and cannot overwrite cached events; even a legitimately shorter timetable may therefore be flagged `stale`. Hourly cadence and entity IDs remain unchanged. The tested page exposed about eight weeks, **not an unlimited number of future months**. A documented, authorized university iCal feed would be preferable if offered for Dresden.

### Release v0.2.7 – Safer timetable handling / Sicherere Stundenplanverarbeitung

**Deutsch:** Version `v0.2.7` enthält die sicheren Diagnose- und Cache-Schutzmaßnahmen aus PR #4 sowie die ausdrückliche Bestätigung der Zugriffsregeln bei **neuen** Installationen. Bereits eingerichtete Stundenpläne behalten ihre Konfiguration und Entitäts-IDs. **Dies ist noch keine bestätigte Lösung für den teilweise unvollständig gelieferten Stundenplan!** Ein erfolgreicher HTTP-Status kann weiterhin nur wenige Wochen enthalten; bitte wichtige Termine im Originalsystem prüfen.

**English:** `v0.2.7` adds sanitized diagnostics, additional protection against truncated future coverage, and an operator-policy acknowledgement for new configurations. Existing entity IDs and configuration entries remain unchanged. **This is not a verified fix for incomplete university responses.** Some HTTP 200 responses still contain only part of the timetable; check important dates against the official portal.

## Known multiweek sync issue / Bekannter Synchronisationsfehler

**Deutsch (Test am 8. November 2026):** Eine erfolgreiche HTTP-200-Antwort kann einen unvollständigen Plan enthalten. Ein Nutzer erhielt im Einzelabruf mit `urllib` **8 Wochentabellen und 62 Termine**, mit standardmäßigem `aiohttp` dagegen **3 Tabellen und 10 Termine** und mit Browser-`User-Agent` plus `aiohttp` sogar nur **1 Tabelle und 0 Termine**. **Der User-Agent allein ist also keine bestätigte Lösung.** Der HTML-Parser extrahierte jeweils korrekt, was er erhalten hatte. Bis zur Klärung kann die letzte gespeicherte Kalenderansicht veraltet oder unvollständig sein. Bitte bei wichtigen Änderungen den Originalplan prüfen.

**English:** HTTP 200 does not prove a complete timetable. Separate read-only tests returned **8 weeks/62 events** (`urllib`), **3 weeks/10 events** (default `aiohttp`), and **1 week/0 events** (`aiohttp` with browser User-Agent). Therefore changing only the User-Agent is **not** a demonstrated fix. The experimental reliability changes are tracked in a draft PR, not in a published release.

**New setup acknowledgement / Hinweis bei neuer Einrichtung:** The development branch requires users to explicitly confirm they have checked the operator's access rules before an initial scheduled fetch. This does **not** constitute university approval; previously configured Dresden entities are not changed. See [MAINTENANCE_PLAN.md](MAINTENANCE_PLAN.md).

## Development / Entwicklung
Source: `custom_components/dhsn_stundenplan/` · Synthetic offline tests: `tests/`. HACS and hassfest validation run using GitHub Actions. This is an experimental community project; please test carefully before relying on it.

## License / Lizenz
[MIT](LICENSE) applies to the original project code only. University timetable content, institutional names, designs and trademarks are not licensed by this repository.


### Last known good timetable (English)

After the first successful sync, the integration saves a locally private snapshot of the timetable in Home Assistant's `.storage` directory. If the university service becomes unreachable or returns a malformed page, the calendar continues showing the last successfully saved events, **which may be outdated**. The `Sync-Status` sensor reports `stale` while the source cannot be verified, and `Letzte erfolgreiche Synchronisierung` reports the timestamp of the last successful fetch. The next successful hourly fetch automatically replaces the saved snapshot. A first-time setup with no previous successful fetch cannot restore events. Removing the integration deletes its local cache, but Home Assistant backups may retain older copies.


**English / v0.2.6 safety rule:** A response that parses to zero timetable events is no longer marked as a successful sync or allowed to overwrite saved events. `event_count` is exposed on the calendar and sync status sensor. A genuinely empty timetable may consequently remain flagged as `stale` until an authoritative empty-state signal can be validated. If v0.2.5 already replaced the snapshot with an empty one, the original events cannot be reconstructed from that snapshot alone.


### Detecting incomplete week responses (planned 0.2.7)

When the source page returns fewer future weeks than a previously successful snapshot, the integration rejects the unusually shortened coverage rather than overwriting existing calendar data. Source diagnostics expose `last_response_week_tables`, `last_response_recognized_weeks`, and `last_response_event_count` alongside the cached `event_count`. The counts do **not** expose HTML or student credentials and should help distinguish a shortened university response from missing table captions. A reduced timetable may also be legitimate, so Home Assistant keeps the older events marked `stale` until a later successful refresh. This feature does not reconstruct missing weeks when the existing cached timetable already has only one week.
