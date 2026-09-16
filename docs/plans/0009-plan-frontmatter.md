# Plan frontmatter: Metadaten in den Plan-Dateien, Tabelle generiert

---
Status: open
Written: 2026-09-16
---

## Einstieg

* **Stand**: branch `plan/0009-plan-frontmatter`, gerade der Plan-Commit,
  nichts implementiert. `tools/pending.py` liest die von Hand gepflegte
  Tabelle in `docs/plans/README.md`; die Pläne 0001–0006 tragen ihren
  Status nur dort (0005 zusätzlich als Ad-hoc-Zeile). Auf `alpha` sind
  193 Tests grün.
* **Nächster Schritt**: Schritt 1 — Frontmatter in alle Plan-Dateien.
* **Lesen**: `tools/pending.py` (`plans_index`, `ROW`),
  `tests/test_pending.py`, `docs/plans/README.md` (Tabelle und
  Konventionstext), AGENTS.md (*Plans*, *Generated content*). Nicht
  nötig: die Inhalte der Pläne 0001–0006.
* **Laufen lassen**: `.venv/bin/python -m pytest` — grün;
  `python3 tools/pending.py` — Übersicht, aktuell noch aus der Tabelle
  gelesen.
* **Offen**: nichts — die Richtungsentscheidungen stehen unter
  *Entschieden*.

## Kontext

Brief von 2026-09-16: die Index-Tabelle in `docs/plans/README.md` wird
von Hand gepflegt, obwohl AGENTS.md sagt, dass der Fortschritt in der
Plan-Datei selbst abgehakt wird — der Status ist genau dieser eine
Haken und lebt doch woanders. Dazu sind die Plan-Dateien inkonsistent:
0005 trägt `Status: **open** · Written: ...` als Ad-hoc-Zeile, 0001 und
0003 im Fließtext, 0002/0004/0006 gar nicht maschinenlesbar. Lösung:
die Metadaten wandern als Frontmatter in die Plan-Dateien, die Tabelle
wird daraus generiert.

## Entschieden (nicht neu diskutieren)

* **Frontmatter, flach**: jede Plan-Datei trägt direkt unter dem Titel
  `Status: open|done|abandoned` und `Written: JJJJ-MM-TT` als
  YAML-Frontmatter. Nichts Weiteres — der Titel bleibt die H1, die
  Nummer steckt im Dateinamen.
* **PyYAML statt Hand-Parser**: die Agentenregeln sagen seit heute,
  "no dependencies" sei ein Antipattern. `pyyaml` kommt in
  `requirements-dev.txt` (`pending.py` ist ein Entwicklungswerkzeug);
  der Commit nennt die Wahl.
* **Tabelle generiert**: `tools/pending.py --write-index` ersetzt die
  Tabelle in `docs/plans/README.md`, begrenzt durch
  `<!-- table:begin -->` und `<!-- table:end -->`. Der Rest der Datei
  bleibt Handarbeit.
* **Regeln folgen**: AGENTS.md (*Plans*, *Generated content*) und die
  Konvention in `docs/plans/README.md` beschreiben danach: Status in
  die Plan-Datei, Tabelle regenerieren — im selben Commit.
* **0007/0008**: ihre Plan-Dateien leben noch auf ihren Branches und
  bekommen ihr Frontmatter, wenn dort weitergearbeitet wird. Der
  Generator meldet einen Plan ohne Frontmatter als `unknown`, statt zu
  scheitern.
* **0009 kommt als `done` auf `alpha`**: Werkzeugarbeit, von den Tests
  abgedeckt; kein Gerät urteilt hier.

## Schritte

### Schritt 1: Frontmatter in alle Plan-Dateien

Modell: GLM — mechanische Edits mit prüfbarem Endzustand (pytest).

* [ ] `pyyaml` in `requirements-dev.txt` und im `.venv` installiert.
* [ ] Frontmatter (Status/Written wie bislang in der Tabelle) in
  0001–0006; die Ad-hoc-Zeile in 0005 fällt weg; die Prosa-Statuszeilen
  in 0001 und 0003 bleiben als Geschichte stehen.
* [ ] pytest grün.

### Schritt 2: Generator und Konventionen

Modell: GLM — baut auf Schritt 1 auf, gleiche Prüfbasis.

* [ ] `tools/pending.py`: `plans_index()` liest das Frontmatter aus
  `docs/plans/*.md` statt der Tabelle; `--write-index` ersetzt den
  markierten Block in `docs/plans/README.md`.
* [ ] `tests/test_pending.py`: Frontmatter-Parser, Tabellengenerierung
  als reine Textfunktion, fehlendes Frontmatter → `unknown`.
* [ ] Konventionstexte: `docs/plans/README.md` (Tabelle generiert,
  Regenerate-Kommando) und AGENTS.md (*Plans*: Status im Frontmatter,
  `Einstieg` unter dem Frontmatter; *Generated content*: neuer Bullet).
* [ ] Tabelle regeneriert — die von Hand gesetzte 0009-Zeile aus dem
  Plan-Commit wird ersetzt, nicht verdoppelt.
* [ ] Status auf `done`, noch einmal regenerieren, Einstieg
  umgeschrieben, committet.
