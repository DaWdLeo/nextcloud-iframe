# Mein erstes iFrame-Projekt

Kleines HTML-Projekt für GitHub Pages und Homarr, komplett vom Smartphone aus nutzbar.

## Inhalt

- `index.html`: Hauptseite mit einem iFrame, das `galerie.html` einbettet.
- `galerie.html`: Vier öffentliche Testbilder mit automatischem Bildwechsel alle 5 Sekunden, Wischanimation, Touchgesten sowie Vor/Zurück/Pause.

## GitHub Pages einrichten

Im Repository **Settings → Pages** öffnen. Unter **Build and deployment** die Quelle **Deploy from a branch** auswählen. Branch **main**, Ordner **/(root)**, anschließend **Save**. Die Veröffentlichung kann einige Minuten dauern.

- Hauptseite: https://dawdleo.github.io/nextcloud-iframe/
- Galerie: https://dawdleo.github.io/nextcloud-iframe/galerie.html

Die Galerie-URL kann als **Embed URL** im Homarr-iFrame verwendet werden.

## Änderungen

In `galerie.html` kann der Wert `const INTERVAL_MS=5000;` beispielsweise auf `2000` geändert werden, um alle zwei Sekunden zu wechseln.

**Datenschutz:** Die Demo verwendet ausschließlich öffentliche Beispielbilder. Private Fotos und Nextcloud-Zugangsdaten gehören nicht in dieses öffentliche Repository. Die private Nextcloud-Anbindung erfolgt später über einen geschützten Homeserver-Dienst.

**Einbettung:** Das Anzeigen in Homarr hängt zusätzlich von den Browser- und Sicherheitsrichtlinien der Umgebung ab.