# ⚽ Fußball-Mathe-Trainer

## Finale Version: Cartoon Only · Hologramm + Glitzer

Ein browserbasierter Mathe-Trainer für Kinder, bei dem richtig gelöste
Aufgaben mit sammelbaren Fußball-Spielerkarten belohnt werden.

Diese Version ist die **endgültige Cartoon-only-Version**. In der App
werden ausschließlich Spieler angezeigt, für die ein Cartoon-Bild
vorhanden ist. Die Legenden-Karten besitzen einen besonderen **lila
Hologramm- und Glitzereffekt**.

## ✨ Funktionen

-   Matheaufgaben spielerisch üben
-   Sammelbare Fußball-Spielerkarten als Belohnung
-   Karte nach jeweils 10 richtigen Antworten
-   Ausgegraute, noch nicht gesammelte Karten im Album
-   Bundesliga, Champions League, Europa League und Legenden
-   Spielerwerte auf Basis von EA SPORTS FC 27
-   Cartoon-Spielerbilder von TheSportsDB
-   Automatische Aktualisierung über GitHub Actions
-   Für iPad, Smartphone und Desktop geeignet
-   PWA-Nutzung über GitHub Pages
-   Lokaler Sammelfortschritt im Browser

## 🎨 Kartendesign

**Gold:** goldfarbener, plastischer Hintergrund.

**Silber:** metallisch-silberner Hintergrund.

**Bronze:** dunkler Bronze-/Kupfer-Hintergrund.

**Legenden:** lila Premium-Hintergrund mit einem weichen, wandernden
Hologramm-Lichtschein und dezenten Glitzerreflexen. Dieser Effekt ist
ausschließlich den Legenden vorbehalten.

## 🖼️ Cartoon Only

Die finale App zeigt **nur Spieler mit vorhandenem Cartoon** an. Die
`players.json` wird dabei ausdrücklich **nicht** gekürzt.

``` js
const allPlayers = await (await fetch('players.json')).json();

players = allPlayers.filter(
  p => typeof p.cartoon === 'string' && p.cartoon.trim() !== ''
);
```

Die vollständige Spielerliste bleibt im Hintergrund erhalten. Hat ein
Spieler heute noch keinen Cartoon, kann der Updater ihn weiterhin
prüfen. Wird später ein Cartoon gefunden, erscheint der Spieler
automatisch in der App.

## 🔄 Automatische Aktualisierung

Wichtige Dateien:

``` text
update_players.py
.github/workflows/update-players.yml
competitions.json
players.json
```

Der GitHub-Workflow prüft regelmäßig unter anderem:

-   EA SPORTS FC 27 Spielerwerte
-   Spieler und Vereinszuordnungen
-   Wettbewerbsdaten
-   TheSportsDB-Daten
-   neu verfügbare Cartoon-Bilder

Der Workflow kann außerdem manuell gestartet werden:

**GitHub → Actions → FC27 Spieler und Cartoons aktualisieren V5 → Run
workflow**

Die vollständige aktuelle `players.json` sollte niemals durch eine alte
Starter-Version ersetzt werden.

## ⚽ Kartenwerte

Verwendet werden Gesamtbewertung, Tempo, Schuss, Passen, Dribbling,
Defensive und Physis.

Die App verwendet **keine originalen EA-Spielerkarten oder
EA-Kartengrafiken**. Sie besitzt ein eigenes Kartendesign und verwendet
Spielerwerte als Daten.

## 🏆 Album-Kategorien

``` text
bundesliga
champions
europa
Rest der Welt
```

Ein Spieler kann mehreren Kategorien angehören. Er behält dabei dieselbe
interne ID, sodass eine gesammelte Karte nicht mehrfach gespeichert
werden muss.

## ⭐ Legenden

Manuell gepflegte Legenden können beispielsweise so in `players.json`
hinterlegt werden:

``` json
{"name":"Spielername","club":"Verein","competitions":["legenden"],"manual":true}
```

Der Updater versucht anschließend, passende Werte und weitere Daten zu
ergänzen.

## 📁 Projektstruktur

``` text
/
├── index.html
├── players.json
├── competitions.json
├── update_players.py
├── service-worker.js
├── manifest.webmanifest
├── README.md
└── .github/
    └── workflows/
        └── update-players.yml
```

Die finale Datei `index-cartoon-only-hologramm-glitzer.html` wird im
veröffentlichten Repository als **`index.html`** verwendet.

## 🌐 GitHub Pages und iPad

Die Dateien werden in das GitHub-Repository hochgeladen und GitHub Pages
wird unter **Settings → Pages** aktiviert. Auf dem iPad kann die Seite
anschließend in Safari geöffnet und über **„Zum Home-Bildschirm"** wie
eine App installiert werden.

## 💾 Sammelfortschritt

Der Sammelfortschritt wird lokal im Browser gespeichert. Ein
Benutzerkonto oder Server für Spielstände ist nicht notwendig.

Beim Löschen der Browser- oder Websitedaten kann der Fortschritt
verloren gehen.

## 🧩 Service Worker

Der Service Worker übernimmt die PWA- und Cache-Funktion. Für
`players.json` sollte die vorhandene Network-first-Logik erhalten
bleiben, damit möglichst die aktuelle Spielerliste geladen wird.

Nach größeren Änderungen an der App kann die Cache-Version erhöht
werden, damit Geräte die neue Version zuverlässig laden.

## 🖼️ Bildquelle

Spieler-Cartoonbilder stammen von **TheSportsDB**.

Die App enthält den sichtbaren Hinweis:

> Spieler-Cartoonbilder: TheSportsDB\
> © Bild-/Artwork-Rechte bei den jeweiligen Rechteinhabern. TheSportsDB
> wird als Bildquelle genannt.

Die Cartoon-only-Version verwendet **keine normalen Spielerfotos als
Ersatz**, wenn kein Cartoon vorhanden ist.

### Hinweis zu TheSportsDB

Die derzeitige automatische Cartoon-Erkennung verwendet neben
API-Abfragen auch TheSportsDB-Webseiten zur Ermittlung von
Cartoon-Artwork. Die jeweils aktuellen Nutzungsbedingungen von
TheSportsDB sollten deshalb insbesondere bei einer öffentlichen
Veröffentlichung oder Weitergabe des Projekts geprüft und berücksichtigt
werden.

## 🛠️ Wichtig bei Änderungen

**`players.json` nicht auf die Cartoon-Spieler reduzieren.**

Die Cartoon-only-Auswahl erfolgt ausschließlich in `index.html`. Nur
dadurch kann der Updater weiterhin Spieler ohne Cartoon prüfen und sie
später automatisch aufnehmen.

Vor größeren Änderungen empfiehlt sich ein Backup von:

``` text
index.html
players.json
competitions.json
update_players.py
service-worker.js
.github/workflows/update-players.yml
```

## ✅ Endgültige Version

**Cartoon Only · Hologramm + Glitzer**

Diese Version kombiniert ausschließlich Cartoon-Spielerkarten,
automatisch aktualisierte Spielerdaten, vier Album-Kategorien, die
gewählten Gold-/Silber-/Bronze-Designs sowie besondere lila
Legenden-Karten mit kombiniertem Hologramm- und Glitzereffekt.

Die vollständige Spielerdatenbank bleibt im Hintergrund erhalten, sodass
Spieler mit neu verfügbaren Cartoons bei späteren Updates automatisch in
der App erscheinen können.
