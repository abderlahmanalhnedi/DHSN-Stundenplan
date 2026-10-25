# 🎓 DHSN Stundenplan for Home Assistant

**Unofficial community integration for Duale Hochschule Sachsen (DHSN) / Inoffizielle Community-Integration für die Duale Hochschule Sachsen (DHSN)**

[![Open repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=abderlahmanalhnedi&repository=DHSN-Stundenplan&category=integration)
[![Add integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dhsn_stundenplan)

[![Validate](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/actions/workflows/validate.yml/badge.svg)](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/actions/workflows/validate.yml)
[![GitHub Issues](https://img.shields.io/badge/Report%20a%20bug-GitHub-blue?logo=github)](https://github.com/abderlahmanalhnedi/DHSN-Stundenplan/issues/new?template=bug_report.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

**Quick links / Direktlinks:** [HACS installation](#installation-über-hacs) · [English setup](#install-with-hacs) · [Privacy / Datenschutz](PRIVACY.md) · [Legal notice / Rechtliches](NOTICE.md)

> **Button usage / Hinweise:** **HACS** opens the custom repository in your own Home Assistant; download it and restart Home Assistant before clicking **Add integration**. / **HACS** öffnet das benutzerdefinierte Repository in deiner Home-Assistant-Instanz. Erst herunterladen und Home Assistant neu starten, dann **Integration hinzufügen** wählen.

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
- **Schreibgeschützt:** keine Änderungen am Hochschul-Stundenplan.
- Keine Zugangsdaten, Cookies, Tokens, Tracking oder zentral gespeicherten Stundenpläne.

### Installation über HACS

**Schnellstart:** [**Repository in HACS öffnen**](https://my.home-assistant.io/redirect/hacs_repository/?owner=abderlahmanalhnedi&repository=DHSN-Stundenplan&category=integration) → Herunterladen → Home Assistant neu starten → [**Integration hinzufügen**](https://my.home-assistant.io/redirect/config_flow_start/?domain=dhsn_stundenplan) → Seminargruppe eingeben.

**Hinweis:** Falls schon eine ältere Version von `dhsn_stundenplan` manuell installiert wurde, zuerst die aktuelle Konfiguration sichern und nicht zwei Kopien derselben Integration parallel installieren. Die GitHub-/HACS-Version wurde noch nicht vollständig in einer frischen Home-Assistant-Testinstallation geprüft.

1. In Home Assistant **HACS** öffnen.
2. Das Menü **⋮ → Benutzerdefinierte Repositories / Custom repositories** öffnen.
3. **`https://github.com/abderlahmanalhnedi/DHSN-Stundenplan`** eingeben; Kategorie **Integration** wählen und hinzufügen.
4. Nach **DHSN Stundenplan** suchen und **Herunterladen / Download** anklicken.
5. **Home Assistant neu starten.**
6. **Einstellungen → Geräte & Dienste → Integration hinzufügen → DHSN Stundenplan** wählen.
7. Eigene **Seminargruppe** eingeben und bestätigen.

Fertig! Der Kalender erscheint automatisch als Entität, etwa `calendar.stundenplan_3spxx_1` (die tatsächliche Entitäts-ID kann abweichen). Öffne **Kalender** und aktiviere ihn.

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

**Quick start:** [**Open in HACS**](https://my.home-assistant.io/redirect/hacs_repository/?owner=abderlahmanalhnedi&repository=DHSN-Stundenplan&category=integration) → Download → Restart Home Assistant → [**Add integration**](https://my.home-assistant.io/redirect/config_flow_start/?domain=dhsn_stundenplan) → Enter seminar group.

**Important:** If an older `dhsn_stundenplan` copy was installed manually, back up your current configuration first and do not install duplicate copies of the same integration. Clean-install testing of the published HACS version is still outstanding.

1. Open **HACS** in Home Assistant.
2. Open **⋮ → Custom repositories**.
3. Enter **`https://github.com/abderlahmanalhnedi/DHSN-Stundenplan`**, select **Integration**, and add it.
4. Find **DHSN Stundenplan** in HACS and click **Download**.
5. **Restart Home Assistant.**
6. Go to **Settings → Devices & services → Add integration → DHSN Stundenplan**.
7. Enter your **seminar group** and submit.

Done! A calendar entity is created automatically (e.g. `calendar.stundenplan_3spxx_1`; your actual entity ID may differ). Enable it in the **Calendar** dashboard.

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

## Development / Entwicklung
Source: `custom_components/dhsn_stundenplan/` · Synthetic offline tests: `tests/`. HACS and hassfest validation run using GitHub Actions. This is an experimental community project; please test carefully before relying on it.

## License / Lizenz
[MIT](LICENSE) applies to the original project code only. University timetable content, institutional names, designs and trademarks are not licensed by this repository.
