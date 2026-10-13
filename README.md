# Workspace

Modulare, statische HTML-Web-App für GitHub Pages und Homarr. Ohne Framework, npm, Build-Schritt oder Serverbetrieb; pflegbar im Smartphone-Browser über GitHub.

## Seiten

- `index.html`: zentrale Startseite und Galerie-Vorschau.
- `galerie.html`: unveränderte Testgalerie mit Touchgesten, Diashow und Steuerung.
- `links.html`: persönliche Kurzlinks, Speicherung in localStorage.
- `notizen.html`: einfache lokale Notizen, Speicherung in localStorage.
- `fokus.html`: Fokus-Timer (25 Minuten).
- `assets/style.css`: gemeinsames responsives Layout (die bisherige Galerie besitzt ihr eigenes Styling).

## GitHub Pages

- [Startseite](https://dawdleo.github.io/nextcloud-iframe/)
- [Galerie](https://dawdleo.github.io/nextcloud-iframe/galerie.html)
- [Kurzlinks](https://dawdleo.github.io/nextcloud-iframe/links.html)
- [Notizen](https://dawdleo.github.io/nextcloud-iframe/notizen.html)
- [Fokus-Timer](https://dawdleo.github.io/nextcloud-iframe/fokus.html)

## Nutzung in Homarr

Ein beliebiges Modul als iFrame einbetten und dessen URL verwenden, z. B. `https://dawdleo.github.io/nextcloud-iframe/fokus.html?embed=1`. Das optionale `?embed=1` blendet Kopfbereich und Navigation der drei neuen Module aus. Einbettung hängt von den Sicherheitseinstellungen des Browsers und Homarr ab.

## Pflege am Smartphone

Repository im GitHub-Webbrowser öffnen, die gewünschte Datei auswählen, über Edit bearbeiten und Änderungen mit Commit speichern. Für ein weiteres unabhängiges Modul eine neue `modulname.html` anlegen und Navigation bzw. Startseiten-Kachel ergänzen. Relative Links (z. B. `./modulname.html`) verhindern Pfadprobleme bei GitHub Pages.

## Datenschutz / Grenzen

**Dieses Repository und GitHub Pages sind öffentlich.** Keine Passwörter, API-Tokens, privaten Fotos oder personenbezogenen Daten einchecken. `localStorage` hält Kurzlinks und Notizen jeweils nur lokal im verwendeten Browser. Sie sind nicht zwischen Geräten synchronisiert und können beim Löschen von Browserdaten verloren gehen. Nur unkritische Inhalte eingeben. Der Timer kann bei ausgesetztem Smartphone-Browser erst beim Wiederaufwachen sichtbar aktualisiert werden; keine verlässliche Hintergrundbenachrichtigung. Private Nextcloud-Inhalte später nur über einen eigens abgesicherten Zugriffsweg anbinden. Lokale HTTP-LAN-Adressen können aus HTTPS-Seiten an Browserregeln scheitern.

## Bestand

Der bisherige Galerie-Prototyp wurde beibehalten: vier öffentliche Unsplash-Bilder, 5-Sekunden-Bildwechsel, Wischgesten sowie Pause/Weiter/Zurück.
