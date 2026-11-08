# Privacy / Datenschutz

## Deutsch

Die inoffizielle Integration für die **Duale Hochschule Sachsen (DHSN)** läuft lokal in **Home Assistant**. Dieses Open-Source-Projekt betreibt **keinen zentralen Proxy, Telemetrieserver oder Datenspeicher** für die Stundenpläne.

**Lokal:** Die angegebene Seminargruppe wird in den Einstellungen von Home Assistant gespeichert. Abgerufene Termine werden dort als Kalenderdaten verarbeitet. Nach dem ersten erfolgreichen Abruf wird zudem **eine letzte gültige Kopie** mit Fächern, Räumen und ggf. Namen von Dozierenden im privaten lokalen Home-Assistant-Speicher (`.storage`) abgelegt. Damit können vorübergehende Ausfälle überbrückt werden. Beim Entfernen des Integrationseintrags wird der Cache gelöscht; bereits existierende Backups müssen ggf. separat entfernt werden. Etwaige Protokolle, Verlaufsspeicherung, Sicherungen und deren Aufbewahrungsdauer hängen von der lokalen Home-Assistant-Konfiguration ab.

**Übertragung:** Der Stundenplanserver wird bei normalem Betrieb etwa stündlich über HTTPS direkt angesprochen. Die Anfrage enthält die Seminargruppe; der fremde Server kann IP-Adresse, Uhrzeit und übliche technische Zugriffsdaten protokollieren. Diese Verarbeitung liegt außerhalb der Kontrolle dieses Projekts. Maßgeblich sind die Datenschutzhinweise des jeweiligen Dienstbetreibers.

**Personenbezogene Inhalte:** Im Stundenplan können Namen von Dozierenden oder weitere personenbezogene Angaben stehen. Bitte keine realen Stundenpläne, HAR-Dateien, Cookies, Tokens oder Kontodaten in öffentliche GitHub-Issues hochladen.

**Stoppen:** Unter Einstellungen → Geräte & Dienste kann die Integration deaktiviert oder entfernt werden. Bestehende Home-Assistant-Backups und Logdaten müssen ggf. getrennt behandelt werden.

## English

This independent, unofficial project intended for **Duale Hochschule Sachsen (DHSN)** runs locally in **Home Assistant**. The project does **not** operate a central proxy, telemetry service or timetable collection backend.

Your seminar-group identifier is stored in local Home Assistant integration settings. Timetable events are processed locally. After the first successful sync, the integration also stores **one last-known-good snapshot** (including course names, rooms and potentially lecturers' names) in Home Assistant's private local `.storage` directory for outage recovery. Removing the integration entry deletes this cache; old backups may need separate removal. Logging and backups depend on your own Home Assistant configuration.

During normal operation, roughly one HTTPS request per hour goes directly to the external timetable server with the group identifier. That operator may record your IP address, time and ordinary HTTP metadata. Its processing is outside the control of this project.

Some timetable data may contain lecturers' names or other personal information. Never post real timetables, HAR captures, cookies, tokens or credentials to public issues.

Disable or remove the integration under Settings → Devices & services to stop future periodic requests. Locally retained backups and logs may need separate deletion.
