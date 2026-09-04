# ⚽ Fußball-Mathe-Trainer

Ein browserbasierter Mathe-Trainer mit Fußball-Sammelkarten.  
Für richtig gelöste Aufgaben können Spielerkarten gesammelt und in einem Album nach Wettbewerben und Vereinen angesehen werden.

## Funktionen

- Rechenarten: Mal, Plus, Minus, Geteilt, Division mit Rest und Mix
- Wählbare Trainingsdauer: 5, 7, 10 oder 15 Minuten
- Nach jeweils 10 richtigen Aufgaben gibt es eine Spielerkarte
- Sammelalbum mit Bundesliga, Champions League, Europa League und Legenden
- Kartenwerte aus EA SPORTS FC 27
- Cartoon-Spielerbilder über TheSportsDB
- Automatische Aktualisierung der Spielerdaten über GitHub Actions
- Für iPad und andere Browser geeignet
- PWA-Unterstützung über Manifest und Service Worker

## Zwei mögliche Versionen der App

### 1. Standard-Version

Die normale `index.html` zeigt alle Spieler aus `players.json`.

Wenn für einen Spieler ein Cartoon vorhanden ist, wird dieser bevorzugt angezeigt. Fehlt ein Cartoon, kann die App auf ein normales TheSportsDB-Spielerbild zurückgreifen. Wenn auch dort kein Bild vorhanden ist, werden die Initialen angezeigt.

### 2. Cartoon-only-Version

Die Datei `index-cartoon-only.html` ist die alternative Variante.

Hier werden ausschließlich Spieler verwendet, für die in `players.json` bereits ein Cartoon hinterlegt ist. Spieler ohne Cartoon erscheinen weder im Sammelalbum noch als neue Belohnung.

Wichtig: Die vollständige `players.json` wird trotzdem nicht gekürzt. Dadurch kann der automatische Updater weiterhin alle Spieler prüfen. Sobald später ein Cartoon gefunden wird, erscheint dieser Spieler automatisch auch in der Cartoon-only-Version.

Für den Einsatz auf GitHub Pages einfach die gewünschte Variante in `index.html` umbenennen.

## Wichtige Dateien

- `index.html` – eigentliche Mathe-App
- `players.json` – Spielerliste, Kartenwerte, Wettbewerbe und Cartoon-URLs
- `update_players.py` – automatischer Spieler-/Cartoon-Updater
- `competitions.json` – Vereine und Wettbewerbs-Konfiguration für den Updater
- `.github/workflows/update-players.yml` – GitHub-Action für die automatische Aktualisierung
- `service-worker.js` – Offline-/Cache-Funktion der App
- `manifest.webmanifest` – PWA-Einstellungen

## Automatischer wöchentlicher Updater

Der Updater läuft über GitHub Actions einmal pro Woche.

Er prüft unter anderem:

1. ob sich Spielerwerte bei EA SPORTS FC 27 geändert haben,
2. ob neue bzw. aktualisierte Spieler in den konfigurierten Mannschaften vorhanden sind,
3. ob für Spieler ein Cartoon-Bild gefunden werden kann,
4. ob vorhandene Daten in `players.json` aktualisiert werden müssen.

Die erzeugte `players.json` wird anschließend automatisch in das Repository zurückgeschrieben.

Der Updater kann außerdem jederzeit manuell gestartet werden:

**GitHub → Actions → „FC27 Spieler und Cartoons aktualisieren V5“ → Run workflow**

## Wichtig bei der Cartoon-only-Version

Für die Cartoon-only-Version darf `players.json` **nicht** manuell auf die Spieler mit Cartoon reduziert werden.

Die App filtert die Spieler erst beim Laden im Browser. In `players.json` müssen weiterhin auch Spieler ohne Cartoon stehen, damit der wöchentliche Updater sie erneut prüfen kann.

Beispiel:

- Heute hat ein Spieler keinen Cartoon → er wird in der Cartoon-only-App nicht angezeigt.
- Der Spieler bleibt trotzdem in `players.json`.
- Beim nächsten automatischen Lauf wird erneut nach einem Cartoon gesucht.
- Wird später ein Cartoon gefunden, trägt der Updater die URL in `players.json` ein.
- Danach erscheint die Karte automatisch in der Cartoon-only-App.

## Neue Spieler hinzufügen

Manuelle Spieler können in `players.json` ergänzt werden. Für dauerhaft manuell gepflegte Einträge sollte das bestehende Format des Projekts beibehalten werden, insbesondere `manual: true`.

Der Updater versucht anschließend, passende EA-/TheSportsDB-Daten zu ergänzen, soweit die aktuelle Updater-Logik dafür einen Treffer findet.

Vor manuellen Änderungen an `players.json` empfiehlt sich eine Sicherungskopie.

## Kartenwerte

Die Kartenwerte orientieren sich an den EA SPORTS FC 27 Ratings.

Verwendet werden unter anderem:

- Gesamtwertung
- Tempo
- Schuss
- Passen
- Dribbling
- Defensive
- Physis

Die Daten dienen in diesem Projekt als Werte für die Sammelkarten. Es werden keine originalen EA-Kartengrafiken verwendet.

## Bilder und Quellenhinweis

Cartoon- und gegebenenfalls Ersatzbilder stammen von TheSportsDB.

In der App ist deshalb ein Quellen-/Rechtehinweis eingebaut:

> Spieler-Cartoonbilder und Ersatzbilder: TheSportsDB  
> © Bild-/Artwork-Rechte bei den jeweiligen Rechteinhabern. TheSportsDB wird als Bildquelle genannt.

Die Nennung der Quelle bedeutet nicht automatisch, dass jedes dort verfügbare Bild frei von Rechten Dritter ist.

## GitHub Pages

Für die Veröffentlichung sollte die gewünschte App-Version als `index.html` im Repository liegen.

Nach einer Änderung:

1. Datei in GitHub hochladen bzw. ersetzen.
2. Änderung committen.
3. Kurz warten, bis GitHub Pages neu bereitgestellt wurde.
4. App im Browser neu laden.

Auf dem iPad kann es wegen des Service Workers vorkommen, dass zunächst noch eine ältere Version angezeigt wird. In diesem Fall die Seite neu laden bzw. die Web-App vollständig schließen und erneut öffnen.

## Service Worker und `players.json`

Der Service Worker ist so ausgelegt, dass `players.json` möglichst aktuell geladen wird. Dadurch können neue Werte und Cartoon-URLs aus dem wöchentlichen Update in der App erscheinen, ohne dass jedes Mal die `index.html` geändert werden muss.

## Sammelfortschritt

Der Sammelfortschritt wird im Browser über `localStorage` gespeichert.

Das bedeutet:

- Ein Update von `players.json` löscht den bisherigen Sammelfortschritt normalerweise nicht.
- Derselbe Spieler behält seine Karten-ID, soweit der Updater bestehende IDs erhalten kann.
- Ein Spieler kann gleichzeitig in mehreren Wettbewerben erscheinen, bleibt aber dieselbe gesammelte Karte.

## Hinweise zum Updater

Der aktuelle Updater verwendet direkte EA-Teamseiten, damit er nicht von Suchmaschinen wie DuckDuckGo oder Bing abhängig ist.

Einige Mannschaften können nicht automatisch verarbeitet werden, wenn keine passende EA-Teamseite hinterlegt bzw. verfügbar ist. Der Workflow ist so gebaut, dass ein einzelner fehlgeschlagener Verein nicht die komplette Aktualisierung stoppen soll.

### Hinweis zu TheSportsDB

Die derzeitige Cartoon-Erkennung verwendet neben API-Abfragen auch TheSportsDB-Webseiten zur Ermittlung von Cartoon-Artwork. Die Nutzungsbedingungen von TheSportsDB sollten deshalb bei einer öffentlichen oder weitergegebenen Version des Projekts berücksichtigt und regelmäßig geprüft werden.

## Empfohlene Sicherung

Vor größeren Änderungen am Projekt am besten diese Dateien sichern:

- `index.html`
- `players.json`
- `update_players.py`
- `competitions.json`
- `.github/workflows/update-players.yml`
- `service-worker.js`

So kann jederzeit auf eine funktionierende Version zurückgegangen werden.

## Projektstruktur

```text
/
├── index.html
├── players.json
├── competitions.json
├── update_players.py
├── service-worker.js
├── manifest.webmanifest
├── bg.jpeg
└── .github/
    └── workflows/
        └── update-players.yml
```

## Kurz gesagt

Die `index.html` steuert die Darstellung und das Mathe-Spiel.  
Die `players.json` enthält die Spielerkarten.  
`update_players.py` aktualisiert die Daten.  
GitHub Actions startet diesen Updater automatisch jede Woche.

Bei der Cartoon-only-Version bleiben trotzdem **alle Spieler in `players.json`**, damit fehlende Cartoons bei zukünftigen Läufen weiterhin gefunden werden können.
