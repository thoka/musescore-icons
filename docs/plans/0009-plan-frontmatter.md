---
Title: "Plan frontmatter: metadata in files, table generated"
Status: done
Written: 2026-09-16
---

# Plan frontmatter: Metadaten in den Plan-Dateien, Tabelle generiert

## Einstieg

* **Stand**: alle Schritte erledigt. Frontmatter (`Title`/`Status`/
  `Written`, Werte mit Doppelpunkt in Anführungszeichen) in
  0001–0006 und 0009; `pyyaml` in `requirements-dev.txt`;
  `tools/pending.py --write-index` generiert die Tabelle zwischen
  `<!-- table:begin -->` / `<!-- table:end -->`; Konventionstexte in
  `docs/plans/README.md` und AGENTS.md angepasst. 198 Tests grün.
* **Nächster Schritt**: keiner im Code — der Merge nach `alpha` ist vom
  Benutzer verlangt; danach `/clear`.
* **Lesen**: `tools/pending.py` (`read_frontmatter`, `plans_index`,
  `index_table`, `replace_table`), `tests/test_pending.py`. Nicht nötig:
  die Inhalte der Pläne 0001–0006.
* **Laufen lassen**: `.venv/bin/python -m pytest` — 198 grün;
  `python3 tools/pending.py --write-index` — idempotent, keine Änderung.
* **Offen**: nichts. Für 0007/0008 gilt: ihr Frontmatter kommt, wenn
  dort der nächste Schritt anpackt.

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

* **Frontmatter, flach**: jede Plan-Datei trägt ganz oben, vor dem
  Titel, `Title`, `Status: open|done|abandoned` und
  `Written: JJJJ-MM-TT` als YAML-Frontmatter. Der `Title` ist englisch
  (die Konvention hält die Tabelle englisch, die H1s sind es nicht) und
  wird nur von der Tabelle gelesen; die Nummer steckt im Dateinamen.
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

* [x] `pyyaml` in `requirements-dev.txt` und im `.venv` installiert.
* [x] Frontmatter (`Title`/`Status`/`Written`, letztere wie bislang in
  der Tabelle) in 0001–0006; die Ad-hoc-Zeile in 0005 fällt weg; die
  Prosa-Statuszeilen in 0001 und 0003 bleiben als Geschichte stehen.
* [x] pytest grün.

### Schritt 2: Generator und Konventionen

Modell: GLM — baut auf Schritt 1 auf, gleiche Prüfbasis.

* [x] `tools/pending.py`: `plans_index()` liest das Frontmatter aus
  `docs/plans/*.md` statt der Tabelle; `--write-index` ersetzt den
  markierten Block in `docs/plans/README.md`.
* [x] `tests/test_pending.py`: Frontmatter-Parser, Tabellengenerierung
  als reine Textfunktion, fehlendes Frontmatter → `unknown`.
* [x] Konventionstexte: `docs/plans/README.md` (Tabelle generiert,
  Regenerate-Kommando) und AGENTS.md (*Plans*: Status im Frontmatter,
  `Einstieg` unter dem Frontmatter; *Generated content*: neuer Bullet).
* [x] Tabelle regeneriert — die von Hand gesetzte 0009-Zeile aus dem
  Plan-Commit wird ersetzt, nicht verdoppelt.
* [x] Status auf `done`, noch einmal regenerieren, Einstieg
  umgeschrieben, committet.
