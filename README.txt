FC27-AUTOMATIK – FUSSBALL-MATHE-TRAINER
=========================================

Was diese Version macht
-----------------------
Das Sammelalbum hat genau vier Kategorien:
1. Bundesliga
2. Champions League
3. Europa League
4. Legenden

Bundesliga und Champions League: pro Verein werden die 11 bestbewerteten
Männer-Spieler aus der offiziellen EA SPORTS FC 27 Ratings-Datenbank übernommen.

Europa League: pro Verein werden die 5 bestbewerteten Männer-Spieler übernommen.

Ein Spieler darf in mehreren Kategorien vorkommen. Er besitzt trotzdem nur EINE
Sammel-ID. Wird die Karte einmal verdient, ist sie in allen Kategorien aufgedeckt.

WICHTIG: ERSTER LAUF
--------------------
Die beigelegte players.json enthält zunächst nur die manuell gepflegten Legenden.
Nach dem ersten Lauf der GitHub Action "FC27 Spieler und Cartoons aktualisieren"
wird players.json automatisch mit den Bundesliga-, Champions-League- und
Europa-League-Spielern aufgebaut.

Die Action versucht:
- offizielle EA-Teamseiten automatisch zu finden,
- die besten Spieler in EA-Rangfolge zu übernehmen,
- OVR/PAC/SHO/PAS/DRI/DEF/PHY zu übernehmen,
- TheSportsDB-IDs und Cartoonbilder zu ergänzen,
- vorhandene Sammel-IDs und vorhandene Cartoon-Links zu behalten,
- players.json mit GENAU EINER ZEILE PRO SPIELER zu schreiben.

Eigene Spieler später hinzufügen
--------------------------------
In players.json einfach vor der schließenden ] eine neue Zeile hinzufügen:

  {"name":"Spielername","club":"Verein","competitions":["legenden"],"manual":true}

oder z.B.:

  {"name":"Spielername","club":"Verein","competitions":["champions"],"manual":true}

Beim nächsten Action-Lauf werden – wenn EA den Spieler findet – FC27-Werte,
EA-ID und weitere Daten ergänzt. Eine id muss nicht eingetragen werden; sie
wird automatisch vergeben. "manual":true ist wichtig, damit der Eintrag beim
automatischen Neuaufbau erhalten bleibt.

Mehrere Kategorien:
  "competitions":["bundesliga","champions"]

Legenden in dieser Startversion
-------------------------------
- Lionel Messi – Inter Miami CF
- Cristiano Ronaldo – Al Nassr
- Thomas Müller – Vancouver Whitecaps FC
- Marco Reus – LA Galaxy
- Neymar Jr – Santos
- Sadio Mané – Al Nassr

Dateien auf GitHub
------------------
index.html                         -> Repository-Hauptverzeichnis
players.json                       -> Repository-Hauptverzeichnis
competitions.json                  -> Repository-Hauptverzeichnis
update_players.py                  -> Repository-Hauptverzeichnis
service-worker.js                  -> Repository-Hauptverzeichnis
.github/workflows/update-players.yml -> genau in diesen Unterordner

Danach:
GitHub -> Actions -> "FC27 Spieler und Cartoons aktualisieren" -> Run workflow.

Hinweis zu den Wettbewerbslisten
--------------------------------
Gewünschte Kicker-Seiten:
https://www.kicker.de/champions-league/teams
https://www.kicker.de/europa-league/teams

Die Kicker-Seiten verwenden Bot-/JavaScript-Schutz. Deshalb wurden die aktuellen
36er-Teilnehmerlisten 2026/27 zusätzlich gegen die offiziellen UEFA-Listen
geprüft und in competitions.json fest hinterlegt.

FC27-Quelle:
https://www.ea.com/games/ea-sports-fc/ratings

EA weist darauf hin, dass bestimmte Details nach dem Datenbank-Update vom
10. September noch geändert werden können. Die wöchentliche Action übernimmt
spätere Änderungen automatisch.

V2-KORREKTUR
------------
Die erste Version suchte EA-Teamseiten über DuckDuckGo/Bing. Das führte in
GitHub Actions zu 403-Fehlern. V2 verwendet KEINE Suchmaschine mehr.

Für unterstützte Vereine steht die direkte offizielle EA-Männerteam-URL in
competitions.json. Nicht sicher zuordenbare Teams werden ausdrücklich
übersprungen. Vorhandene automatische Spieler werden bei einem späteren
temporären EA-Fehler nicht mehr aus players.json gelöscht.

Beispiele der fest hinterlegten Männerteams:
FC Bayern München -> .../fc-bayern-munchen/21
Borussia Dortmund -> .../borussia-dortmund/22
Manchester City -> .../manchester-city/10
Arsenal -> .../arsenal/1
FC Barcelona -> .../fc-barcelona/241
Atlético Madrid -> .../atletico-de-madrid/240
RSC Anderlecht -> .../rsc-anderlecht/229
Beşiktaş -> .../besiktas/327
Celtic -> .../celtic/78


V4-CARTOON-VERBESSERUNG
-----------------------
FC27-Team- und Wertelogik bleibt unverändert.
Für Spieler ohne Cartoon wird die SportsDB-Spieler-/Teamzuordnung erneut geprüft.
Alte UND frisch gemeldete SportsDB-Team-IDs werden als mögliche Cartoon-Quelle
berücksichtigt. Vorhandene Cartoons werden nicht überschrieben.
Der Workflow meldet am Ende die Cartoon-Abdeckung und Beispiele fehlender Cartoons.

Wichtig: Wenn TheSportsDB für einen Spieler selbst keinen Cartoon bereitstellt,
kann der Updater keinen Cartoon erfinden.
