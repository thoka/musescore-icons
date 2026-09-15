# MuseScore 4.7.4 — Action-Codes

*Aus dem Quelltext von [MuseScore v4.7.4](https://github.com/musescore/MuseScore/tree/v4.7.4)
extrahiert — dieselben Register, die der Shortcuts-Editor anbietet. Titel und
Beschreibungen sind die (englischen) UI-Texte; die deutsche Oberfläche zeigt
Übersetzungen. „Aktiv wo" ist der Shortcut-Kontext (`scCtx`): wo eine zugewiesene
Taste greift. „Vorbelegung" kommt aus der eingebetteten
`src/app/configs/data/shortcuts.xml`. 548 Aktionen.
Neu erzeugen: `tools/extract_actions.py`.*

Siehe auch: `docs/musescore-fernsteuerung.md` (wie diese Codes als Tasten
zugewiesen werden).

### App-Fenster & Menüs (34)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `about-musescore` | About MuseScore Studio… |  | immer |  |
| `about-musicxml` | About MusicXML… |  | immer |  |
| `about-qt` | About Qt… |  | immer |  |
| `accessibility-statement` | Accessibility statement |  | immer |  |
| `action://cancel` |  |  | immer | Esc |
| `action://copy` | Copy | Copy | immer | Ctrl+C |
| `action://cut` | Cut | Cut | immer | Ctrl+X |
| `action://delete` | Delete | Delete | immer | Del Backspace |
| `action://paste` | Paste | Paste | immer | Ctrl+V |
| `action://redo` | Redo |  | immer |  |
| `action://undo` | Undo |  | immer |  |
| `ask-help` | Ask for help |  | immer |  |
| `dock-restore-default-layout` | Restore the default layout | Restore the default layout | immer |  |
| `fullscreen` | Full screen | Full screen | immer | F11 |
| `inspector` | Properties | Show/hide properties | immer | F8 |
| `online-handbook` | Online handbook | Open online handbook | immer |  |
| `preference-dialog` | Preferences… | Preferences | immer |  |
| `quit` | Quit |  | immer | Ctrl+Q |
| `restart` | Restart |  | immer |  |
| `revert-factory` | Revert to factory settings | Revert to factory settings | immer |  |
| `toggle-braille-panel` | Braille | Show/hide braille panel | immer | Alt+F11 |
| `toggle-instruments` | Layout | Show/hide layout panel | immer | F7 |
| `toggle-mixer` | Mixer | Show/hide mixer | immer | F10 |
| `toggle-navigator` | Navigator | Show/hide navigator | immer |  |
| `toggle-noteinput` | Note input | Show/hide note input toolbar | immer |  |
| `toggle-palettes` | Palettes | Show/hide palettes | immer | F9 |
| `toggle-percussion-panel` | Percussion | Show/hide percussion panel | Partitur offen | O |
| `toggle-piano-keyboard` | Piano keyboard | Show/hide piano keyboard | immer | P |
| `toggle-scorecmp-tool` | Score comparison tool |  | Partitur offen |  |
| `toggle-selection-filter` | Selection filter | Show/hide selection filter | Partitur offen |  |
| `toggle-statusbar` | Status bar | Show/hide status bar | Partitur offen |  |
| `toggle-timeline` | Timeline | Show/hide timeline | immer | F12 |
| `toggle-transport` | Playback controls | Show/hide playback controls | Partitur offen |  |
| `toggle-undo-history-panel` | History | Show/hide undo history | Partitur offen |  |

### Notation (424)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `acciaccatura` | Acciaccatura | Add grace note: acciaccatura | Partitur offen | / Num+/ |
| `action://notation/cancel` |  |  | deaktiviert |  |
| `action://notation/copy` | Copy | Copy | deaktiviert |  |
| `action://notation/cut` | Cut | Cut | deaktiviert |  |
| `action://notation/delete` | Delete | Delete | deaktiviert |  |
| `action://notation/paste` | Paste | Paste | deaktiviert |  |
| `action://notation/redo` | Redo |  | deaktiviert |  |
| `action://notation/undo` | Undo |  | deaktiviert |  |
| `add-8va` | Ottava 8va alta | Add ottava 8va alta | Partitur offen |  |
| `add-8vb` | Ottava 8va bassa | Add ottava 8va bassa | Partitur offen |  |
| `add-braces` | Add braces to element |  | Partitur offen |  |
| `add-brackets` | Add brackets to accidental |  | Partitur offen |  |
| `add-down-bow` | Toggle down bow | Add bowing: down bow | Partitur offen |  |
| `add-dynamic` | Dynamic | Add dynamic | Partitur offen | Ctrl+D |
| `add-fretboard-diagram` | Add fretboard diagram | Add fretboard diagram | Partitur fokussiert |  |
| `add-hairpin` | Crescendo | Add hairpin: crescendo | Partitur offen | Shift+, |
| `add-hairpin-reverse` | Diminuendo | Add hairpin: diminuendo | Partitur offen | Shift+. |
| `add-haydn` | Toggle Haydn ornament | Add ornament: Haydn ornament | Partitur offen |  |
| `add-image` | Image |  | Partitur fokussiert |  |
| `add-lyric-verse` | Add lyrics verse |  | Partitur offen | Return Enter |
| `add-marcato` | Marcato | Add articulation: marcato | Partitur offen | Shift+O |
| `add-melisma` | Add extension line | Lyrics: enter extension line | notation-text-editing | Shift+- |
| `add-mordent` | Toggle mordent | Add ornament: mordent | Partitur offen |  |
| `add-noteline` | Note-anchored line | Add note-anchored line | Partitur offen |  |
| `add-parentheses` | Add parentheses to element |  | Partitur offen | Shift+9 |
| `add-prall-mordent` | Toggle prall mordent | Add ornament: prall mordent | Partitur offen |  |
| `add-sforzato` | Accent | Add articulation: accent | Partitur offen | Shift+V |
| `add-shake` | Toggle shake | Add ornament: shake | Partitur offen |  |
| `add-shake-muffat` | Toggle shake (Muffat) | Add ornament: shake (Muffat) | Partitur offen |  |
| `add-short-trill` | Toggle short trill | Add ornament: short trill | Partitur offen |  |
| `add-slur` | Slur | Add slur | Partitur offen | S |
| `add-staccato` | Staccato | Add articulation: staccato | Partitur offen | Shift+S |
| `add-tenuto` | Tenuto | Add articulation: tenuto | Partitur offen | Shift+N |
| `add-tremblement` | Toggle tremblement | Add ornament: tremblement | Partitur offen |  |
| `add-tremblement-couperin` | Toggle tremblement appuyé (Couperin) | Add ornament: tremblement appuyé (Couperin) | Partitur offen |  |
| `add-trill` | Toggle trill | Add ornament: trill | Partitur offen |  |
| `add-turn` | Toggle turn | Add ornament: turn | Partitur offen |  |
| `add-turn-inverted` | Toggle inverted turn | Add ornament: inverted turn | Partitur offen |  |
| `add-turn-inverted-up` | Toggle vertical inverted turn | Add ornament: vertical inverted turn | Partitur offen |  |
| `add-turn-slash` | Toggle turn with slash | Add ornament: turn with slash | Partitur offen |  |
| `add-turn-up` | Toggle vertical turn | Add ornament: vertical turn | Partitur offen |  |
| `add-up-bow` | Toggle up bow | Add bowing: up bow | Partitur offen |  |
| `advance-1` | Advance cursor: whole note (chord symbols/figured bass) |  | Partitur offen | Ctrl+7 |
| `advance-16` | Advance cursor: 16th note (chord symbols/figured bass) |  | Partitur offen | Ctrl+3 |
| `advance-2` | Advance cursor: half note (chord symbols/figured bass) |  | Partitur offen | Ctrl+6 |
| `advance-32` | Advance cursor: 32nd note (chord symbols/figured bass) |  | Partitur offen | Ctrl+2 |
| `advance-4` | Advance cursor: quarter note (chord symbols/figured bass) |  | Partitur offen | Ctrl+5 |
| `advance-64` | Advance cursor: 64th note (chord symbols/figured bass) |  | Partitur offen | Ctrl+1 |
| `advance-8` | Advance cursor: eighth note (chord symbols/figured bass) |  | Partitur offen | Ctrl+4 |
| `advance-breve` | Advance cursor: breve (chord symbols/figured bass) |  | Partitur offen | Ctrl+8 |
| `advance-longa` | Advance cursor: longa (chord symbols/figured bass) |  | Partitur offen | Ctrl+9 |
| `append-fretframe` | Fretboard diagram legend | Insert fretboard diagram legend at end of score | Partitur offen |  |
| `append-hbox` | Horizontal frame | Insert horizontal frame at end of score | Partitur offen |  |
| `append-measure` | Insert one measure at end of score | Insert one measure at end of score | Partitur offen | Ctrl+B |
| `append-measures` | Insert at end of score… | Insert measures at end of score | Partitur offen | Alt+Shift+B |
| `append-textframe` | Text frame | Insert text frame at end of score | Partitur offen |  |
| `append-vbox` | Vertical frame | Insert vertical frame at end of score | Partitur offen |  |
| `apply-system-lock` | Add/remove system lock |  | Partitur fokussiert | Alt+Return Alt+Enter |
| `appoggiatura` | Appoggiatura | Add grace note: appoggiatura | Partitur offen |  |
| `autoplace-enabled` | Toggle automatic placement for entire score |  | Partitur offen |  |
| `beam-auto` | Auto beam |  | Partitur offen |  |
| `beam-break-inner-16th` | Break inner beams (16th) |  | Partitur offen |  |
| `beam-break-inner-8th` | Break inner beams (8th) | Break inner beams (eighth) | Partitur offen |  |
| `beam-break-left` | Break beam left |  | Partitur offen |  |
| `beam-feathered-accelerate` | Feathered beam, accelerate | Add feathered beam: accelerate | Partitur offen |  |
| `beam-feathered-decelerate` | Feathered beam, decelerate | Add feathered beam: decelerate | Partitur offen |  |
| `beam-join` | Join beams |  | Partitur offen |  |
| `beam-none` | No beam |  | Partitur offen |  |
| `bottom-chord` | Bottom note in chord | Select bottom note in chord | Partitur fokussiert | Ctrl+Alt+Down |
| `check-for-score-corruptions` | Check for score corruptions |  | Partitur offen |  |
| `chord-a` |  |  | Partitur offen | Shift+A |
| `chord-b` |  |  | Partitur offen | Shift+B Shift+H |
| `chord-c` |  |  | Partitur offen | Shift+C |
| `chord-d` |  |  | Partitur offen | Shift+D |
| `chord-e` |  |  | Partitur offen | Shift+E |
| `chord-f` |  |  | Partitur offen | Shift+F |
| `chord-g` |  |  | Partitur offen | Shift+G |
| `chord-text` | Chord symbol | Add text: chord symbol | Partitur offen | Ctrl+K |
| `chord-tie` | Add tied note to chord |  | Partitur offen | Alt++ |
| `clef-bass` | Add bass clef | Add clef: bass | Partitur offen |  |
| `clef-violin` | Add treble clef | Add clef: treble | Partitur offen |  |
| `color-element-shapes` | Color element shapes |  | Partitur offen |  |
| `color-segment-shapes` | Color segment shapes |  | Partitur offen |  |
| `composer-text` | Composer | Add text: composer | Partitur offen |  |
| `concert-pitch` | Concert pitch | Toggle concert pitch | Partitur offen |  |
| `copy-lyrics-to-clipboard` | Copy lyrics to clipboard | Copy lyrics | Partitur offen |  |
| `cross-staff-beaming` | Cross-staff beaming |  | Partitur offen |  |
| `dec-duration-dotted` | Halve selected duration (dotted) | Halve selected duration (includes dotted values) | Partitur offen | Shift+Q |
| `del-empty-measures` | Remove empty trailing measures | Remove empty trailing measures | Partitur offen |  |
| `dip` | Dip |  | Partitur offen |  |
| `dive` | Dive |  | Partitur offen |  |
| `double-duration` | Double duration | Double selected duration | Partitur offen | W |
| `down-chord` | Down note in chord | Select note/rest below | notation-list-selection | Alt+Down |
| `duplet` | Duplet | Enter tuplet: duplet | Partitur fokussiert | Ctrl+2 |
| `edit-element` | Edit element |  | Partitur offen | F2 Alt+Shift+E |
| `edit-strings` |  |  | Partitur offen |  |
| `edit-style` | Style… | Format style | Partitur offen |  |
| `empty-trailing-measure` | Go to first empty trailing measure |  | Partitur offen |  |
| `enh-both` | Change enharmonic spelling (concert and transposed pitch) | Change enharmonic spelling (concert and transposed pitch) | Partitur offen | J |
| `enh-current` | Change enharmonic spelling (current pitch mode only) | Change enharmonic spelling (current pitch mode only) | Partitur offen | Ctrl+J |
| `explode` | Explode | Explode | Partitur offen |  |
| `expression-text` | Expression text | Add text: expression text | Partitur offen | Ctrl+E |
| `extend-to-next-note` | Extend to next note |  | Partitur offen | Alt+W |
| `figured-bass` | Figured bass | Add text: figured bass | Partitur offen | Ctrl+G |
| `find` | Find / Go to | Find / Go to | Partitur offen |  |
| `fingering-text` | Fingering | Add text: fingering | Partitur offen |  |
| `first-element` | First element | Go to first element in score | Partitur fokussiert | Ctrl+Home |
| `flat` | Toggle flat | Toggle accidental: flat | Partitur offen | - Num+- |
| `flat-post` | Add flat | Add accidental: flat | Partitur offen |  |
| `flat2` | Toggle double-flat | Toggle accidental: double-flat | Partitur offen |  |
| `flat2-post` | Add double-flat | Add accidental: double-flat | Partitur offen |  |
| `flip` | Flip direction |  | Partitur offen | X |
| `flip-horizontally` | Flip horizontally |  | Partitur offen | Alt+X |
| `frame-text` | Text | Add frame text | Partitur offen |  |
| `fret-0` |  |  | notation-note-input-staff-tab | 0 A |
| `fret-1` |  |  | notation-note-input-staff-tab | 1 B |
| `fret-10` |  |  | notation-note-input-staff-tab |  |
| `fret-11` |  |  | notation-note-input-staff-tab |  |
| `fret-12` |  |  | notation-note-input-staff-tab |  |
| `fret-13` |  |  | notation-note-input-staff-tab |  |
| `fret-14` |  |  | notation-note-input-staff-tab |  |
| `fret-2` |  |  | notation-note-input-staff-tab | 2 C |
| `fret-3` |  |  | notation-note-input-staff-tab | 3 D |
| `fret-4` |  |  | notation-note-input-staff-tab | 4 E |
| `fret-5` |  |  | notation-note-input-staff-tab | 5 F |
| `fret-6` |  |  | notation-note-input-staff-tab | 6 G |
| `fret-7` |  |  | notation-note-input-staff-tab | 7 H |
| `fret-8` |  |  | notation-note-input-staff-tab | 8 J |
| `fret-9` |  |  | notation-note-input-staff-tab | 9 K |
| `full-measure-rest` | Full measure rest | Insert full measure rest | Partitur offen | Ctrl+Shift+Del Ctrl+Shift+Backspace |
| `get-location` | Accessibility: Get location | Accessibility: get location | Partitur offen | Shift+L |
| `grace-note-bend` | Grace note bend |  | Partitur offen | Ctrl+Alt+B |
| `grace16` | Grace: 16th | Add grace note: 16th | Partitur offen |  |
| `grace16after` | Grace: 16th after | Add grace note: 16th after | Partitur offen |  |
| `grace32` | Grace: 32nd | Add grace note: 32nd | Partitur offen |  |
| `grace32after` | Grace: 32nd after | Add grace note: 32nd after | Partitur offen |  |
| `grace4` | Grace: quarter | Add grace note: quarter | Partitur offen |  |
| `grace8after` | Grace: 8th after | Add grace note: eighth after | Partitur offen |  |
| `half-duration` | Halve duration | Halve selected duration | Partitur offen | Q |
| `hammer-on-pull-off` | Hammer-on/pull-off | Add hammer-on/pull-off | Partitur offen | Alt+H |
| `help` | Context sensitive help |  | Partitur offen | F1 |
| `implode` | Implode | Implode | Partitur offen |  |
| `inc-duration-dotted` | Double selected duration (dotted) | Double selected duration (includes dotted values) | Partitur offen | Shift+W |
| `insert-a` |  |  | Partitur offen | Ctrl+Shift+A |
| `insert-b` |  |  | Partitur offen | Ctrl+Shift+B Ctrl+Shift+H |
| `insert-c` |  |  | Partitur offen | Ctrl+Shift+C |
| `insert-d` |  |  | Partitur offen | Ctrl+Shift+D |
| `insert-e` |  |  | Partitur offen | Ctrl+Shift+E |
| `insert-f` |  |  | Partitur offen | Ctrl+Shift+F |
| `insert-fretframe` | Insert fretboard diagram legend | Insert fretboard diagram legend | Partitur offen |  |
| `insert-g` |  |  | Partitur offen | Ctrl+Shift+G |
| `insert-hbox` | Insert horizontal frame | Insert horizontal frame | Partitur offen |  |
| `insert-measure` | Insert one measure before selection | Insert one measure before selection | Partitur offen | Ins |
| `insert-measures` | Insert before selection… | Insert measures before selection | Partitur offen | Ctrl+Ins |
| `insert-measures-after-selection` | Insert after selection… | Insert measures after selection | Partitur offen |  |
| `insert-measures-at-start-of-score` | Insert at start of score… | Insert measures at start of score | Partitur offen |  |
| `insert-staff-type-change` | Staff type change | Insert staff type change | Partitur offen |  |
| `insert-textframe` | Insert text frame | Insert text frame | Partitur offen |  |
| `insert-vbox` | Insert vertical frame | Insert vertical frame | Partitur offen |  |
| `instrument-change-text` | Instrument change | Add text: instrument change | Partitur offen |  |
| `interval-10` | Tenth below | Enter interval: tenth below | Partitur offen | Alt+Shift+0 |
| `interval-2` | Second below | Enter interval: second below | Partitur offen | Alt+Shift+2 |
| `interval-3` | Third below | Enter interval: third below | Partitur offen | Alt+Shift+3 |
| `interval-4` | Fourth below | Enter interval: fourth below | Partitur offen | Alt+Shift+4 |
| `interval-5` | Fifth below | Enter interval: fifth below | Partitur offen | Alt+Shift+5 |
| `interval-6` | Sixth below | Enter interval: sixth below | Partitur offen | Alt+Shift+6 |
| `interval-7` | Seventh below | Enter interval: seventh below | Partitur offen | Alt+Shift+7 |
| `interval-8` | Octave below | Enter interval: octave below | Partitur offen | Alt+Shift+8 |
| `interval-9` | Ninth below | Enter interval: ninth below | Partitur offen | Alt+Shift+9 |
| `interval1` | Unison | Enter interval: unison | Partitur offen | Alt+1 |
| `interval10` | Tenth above | Enter interval: tenth above | Partitur offen | Alt+0 |
| `interval2` | Second above | Enter interval: second above | Partitur offen | Alt+2 |
| `interval3` | Third above | Enter interval: third above | Partitur offen | Alt+3 |
| `interval4` | Fourth above | Enter interval: fourth above | Partitur offen | Alt+4 |
| `interval5` | Fifth above | Enter interval: fifth above | Partitur offen | Alt+5 |
| `interval6` | Sixth above | Enter interval: sixth above | Partitur offen | Alt+6 |
| `interval7` | Seventh above | Enter interval: seventh above | Partitur offen | Alt+7 |
| `interval8` | Octave above | Enter interval: octave above | Partitur offen | Alt+8 |
| `interval9` | Ninth above | Enter interval: ninth above | Partitur offen | Alt+9 |
| `join-measures` | Join selected measures | Join selected measures | Partitur offen |  |
| `last-element` | Last element | Go to last element in score | Partitur fokussiert | Ctrl+End |
| `load-style` | Load style… | Load style | Partitur offen |  |
| `lv` | Laissez vibrer | Add laissez vibrer | Partitur offen |  |
| `lyrics` | Lyrics | Add text: lyrics | Partitur offen | Ctrl+L |
| `make-into-system` | Create system from selection |  | Partitur fokussiert | Alt+S |
| `mark-corrupted-measures` | Mark corrupted measures |  | Partitur offen |  |
| `mark-empty-staff-visibility-overrides` | Mark empty staff visibility overrides |  | Partitur offen |  |
| `measure-properties` | Measure properties… | Measure properties | Partitur offen |  |
| `measures-per-system` | Measures per system… | Measures per system | Partitur offen |  |
| `mirror-note` | Mirror notehead |  | Partitur offen | Shift+X |
| `move-down` | Move to staff below | Move selected note/rest to staff below | Partitur fokussiert | Ctrl+Shift+Down |
| `move-left` | Move chord/rest left |  | Partitur fokussiert | Shift+Left |
| `move-measure-to-next-system` | Move measure to next system |  | Partitur fokussiert | Alt+Down |
| `move-measure-to-prev-system` | Move measure to previous system |  | Partitur fokussiert | Alt+Up |
| `move-right` | Move chord/rest right |  | Partitur fokussiert | Shift+Right |
| `move-up` | Move to staff above | Move selected note/rest to staff above | Partitur fokussiert | Ctrl+Shift+Up |
| `nashville-number-text` | Nashville number | Add text: Nashville number | Partitur offen |  |
| `nat` | Toggle natural | Toggle accidental: natural | Partitur offen | = |
| `nat-post` | Add natural | Add accidental: natural | Partitur offen |  |
| `next-beat-TEXT` | Advance cursor: next beat (chord symbols) |  | Partitur offen | ; |
| `next-element` | Next element | Select next element in score | Partitur fokussiert | Alt+Right |
| `next-frame` | Next frame | Go to next frame | Partitur fokussiert |  |
| `next-lyric-verse` | Next lyric verse | Move text/go to next lyric verse | notation-text-editing | Down |
| `next-segment-element` | Accessibility: Next segment element | Select next in-staff element | Partitur offen | Ctrl+Alt+Shift+Right |
| `next-syllable` | Next syllable | Lyrics: enter hyphen | notation-text-editing | - Num+- |
| `next-system` | Next system | Go to next system | Partitur fokussiert |  |
| `next-text-element` | Next text element | Go to next text element | notation-text-editing | Right |
| `next-track` | Next staff or voice | Go to next staff or voice | Partitur fokussiert |  |
| `next-word` | Next word | Go to next word | notation-text-editing | Space |
| `nonuplet` | Nonuplet | Enter tuplet: nonuplet | Partitur fokussiert | Ctrl+9 |
| `notation-context-menu` |  |  | Partitur fokussiert | Shift+F10 Ctrl+Shift+F10 |
| `notation-move-left` | Previous chord / Shift text left | Select previous chord / move text left | Partitur fokussiert | Left |
| `notation-move-left-quickly` | Previous measure / Shift text left quickly | Go to previous measure / move text left quickly | Partitur fokussiert | Ctrl+Left |
| `notation-move-right` | Next chord / Shift text right | Select next chord / move text right | Partitur fokussiert | Right |
| `notation-move-right-quickly` | Next measure / Shift text right quickly | Go to next measure / move text right quickly | Partitur fokussiert | Ctrl+Right |
| `notation-paste-double` | Paste double duration | Paste double duration | Partitur fokussiert | Ctrl+Shift+W |
| `notation-paste-half` | Paste half duration | Paste half duration | Partitur fokussiert | Ctrl+Shift+Q |
| `notation-paste-special` | Paste special |  | Partitur offen |  |
| `notation-popup-menu` |  |  | Partitur fokussiert |  |
| `notation-select-all` | Select all | Select all | Partitur offen | Ctrl+A |
| `notation-select-section` | Select section | Select section | Partitur offen |  |
| `notation-swap` | Swap with clipboard | Copy/paste: swap with clipboard | Partitur fokussiert | Ctrl+Shift+X |
| `note-a` |  |  | Partitur offen | A |
| `note-b` |  |  | Partitur offen | B H |
| `note-breve` | Double whole note | Set duration: double whole note | notation-not-note-input-staff-tab | 8 Num+8 |
| `note-c` |  |  | Partitur offen | C |
| `note-d` |  |  | Partitur offen | D |
| `note-e` |  |  | Partitur offen | E |
| `note-f` |  |  | Partitur offen | F |
| `note-g` |  |  | Partitur offen | G |
| `note-input` | Note input | Toggle note input mode | Partitur offen |  |
| `note-input-by-duration` | Input by duration | Toggle note input mode: input by duration | Partitur offen | M |
| `note-input-by-note-name` | Input by note name | Toggle note input mode: input by note name | Partitur offen | N |
| `note-input-realtime-auto` | Real-time (metronome) | Toggle note input mode: real-time (metronome) | Partitur offen |  |
| `note-input-realtime-manual` | Real-time (foot pedal) | Toggle note input mode: real-time (foot pedal) | Partitur offen |  |
| `note-input-repitch` | Re-pitch existing notes | Toggle note input mode: re-pitch existing notes | Partitur offen | Ctrl+Shift+I |
| `note-input-rhythm` | Rhythm only (not pitch) | Toggle note input mode: rhythm only (not pitch) | Partitur offen |  |
| `note-input-timewise` | Insert | Toggle note input mode: insert (increases measure duration) | Partitur offen |  |
| `note-longa` | Longa | Set duration: longa | notation-not-note-input-staff-tab | 9 Num+9 |
| `octuplet` | Octuplet | Enter tuplet: octuplet | Partitur fokussiert | Ctrl+8 |
| `pad-dot` | Augmentation dot | Toggle duration dot | Partitur offen | . Num+. Num+, |
| `pad-dot2` | Double augmentation dot | Toggle duration dot: double | Partitur offen |  |
| `pad-dot3` | Triple augmentation dot | Toggle duration dot: triple | Partitur offen |  |
| `pad-dot4` | Quadruple augmentation dot | Toggle duration dot: quadruple | Partitur offen |  |
| `pad-note-1` | Whole note | Set duration: whole note | notation-not-note-input-staff-tab | 7 Num+7 |
| `pad-note-1-TAB` | Whole note | Set duration: whole note | Partitur offen | Shift+7 Num+7 |
| `pad-note-1024` | 1024th note | Set duration: 1024th note | notation-not-note-input-staff-tab |  |
| `pad-note-1024-TAB` | 1024th note | Set duration: 1024th note | Partitur offen |  |
| `pad-note-128` | 128th note | Set duration: 128th note | notation-not-note-input-staff-tab |  |
| `pad-note-128-TAB` | 128th note | Set duration: 128th note | Partitur offen | Shift+0 Num+0 |
| `pad-note-16` | 16th note | Set duration: 16th note | notation-not-note-input-staff-tab | 3 Num+3 |
| `pad-note-16-TAB` | 16th note | Set duration: 16th note | Partitur offen | Shift+3 Num+3 |
| `pad-note-2` | Half note | Set duration: half note | notation-not-note-input-staff-tab | 6 Num+6 |
| `pad-note-2-TAB` | Half note | Set duration: half note | Partitur offen | Shift+6 Num+6 |
| `pad-note-256` | 256th note | Set duration: 256th note | notation-not-note-input-staff-tab |  |
| `pad-note-256-TAB` | 256th note | Set duration: 256th note | Partitur offen |  |
| `pad-note-32` | 32nd note | Set duration: 32nd note | notation-not-note-input-staff-tab | 2 Num+2 |
| `pad-note-32-TAB` | 32nd note | Set duration: 32nd note | Partitur offen | Shift+2 Num+2 |
| `pad-note-4` | Quarter note | Set duration: quarter note | notation-not-note-input-staff-tab | 5 Num+5 |
| `pad-note-4-TAB` | Quarter note | Set duration: quarter note | Partitur offen | Shift+5 Num+5 |
| `pad-note-512` | 512th note | Set duration: 512th note | notation-not-note-input-staff-tab |  |
| `pad-note-512-TAB` | 512th note | Set duration: 512th note | Partitur offen |  |
| `pad-note-64` | 64th note | Set duration: 64th note | notation-not-note-input-staff-tab | 1 Num+1 |
| `pad-note-64-TAB` | 64th note | Set duration: 64th note | Partitur offen | Shift+1 Num+1 |
| `pad-note-8` | Eighth note | Set duration: eighth note | notation-not-note-input-staff-tab | 4 Num+4 |
| `pad-note-8-TAB` | Eighth note | Set duration: eighth note | Partitur offen | Shift+4 Num+4 |
| `pad-rest` | Rest | Toggle rest | Partitur offen |  |
| `page-break` | Add/remove page break |  | Partitur offen | Ctrl+Return Ctrl+Enter |
| `page-end` | Page: Bottom of last | Jump to bottom of last page | Partitur offen | End |
| `page-next` | Page: Next | Jump to next page | Partitur offen | Ctrl+PgDown |
| `page-prev` | Page: Previous | Jump to previous page | Partitur offen | Ctrl+PgUp |
| `page-settings` | Page settings… | Page settings | Partitur offen |  |
| `page-top` | Page: Top of first | Jump to top of first page | Partitur offen | Home |
| `part-text` | Part name | Add text: part name | Partitur offen |  |
| `parts` | Parts | Manage parts | Partitur offen |  |
| `pitch-down` | Down | Move pitch/selection down | notation-not-note-input-staff-tab | Down |
| `pitch-down-diatonic` | Diatonic pitch down | Move pitch down diatonically | Partitur offen | Alt+Shift+Down |
| `pitch-down-diatonic-alterations` | Diatonic pitch down (keep degree alterations) | Move pitch down diatonically (keep degree alterations) | Partitur offen |  |
| `pitch-down-octave` | Down octave | Move pitch down an octave | Partitur fokussiert | Ctrl+Down |
| `pitch-spell` | Optimize enharmonic spelling | Optimize enharmonic spelling | Partitur offen |  |
| `pitch-spell-flats` | Respell pitches with flats | Respell pitches with flats | Partitur offen |  |
| `pitch-spell-sharps` | Respell pitches with sharps | Respell pitches with sharps | Partitur offen |  |
| `pitch-up` | Up | Move pitch/selection up | notation-not-note-input-staff-tab | Up |
| `pitch-up-diatonic` | Diatonic pitch up | Move pitch up diatonically | Partitur offen | Alt+Shift+Up |
| `pitch-up-diatonic-alterations` | Diatonic pitch up (keep degree alterations) | Move pitch up diatonically (keep degree alterations) | Partitur offen |  |
| `pitch-up-octave` | Up octave | Move pitch up an octave | Partitur fokussiert | Ctrl+Up |
| `poet-text` | Lyricist | Add text: lyricist | Partitur offen |  |
| `pre-bend` | Pre-bend |  | Partitur offen |  |
| `pre-dive` | Pre-dive |  | Partitur offen |  |
| `prev-beat-TEXT` | Advance cursor: previous beat (chord symbols) |  | Partitur offen | Shift+; |
| `prev-element` | Previous element | Select previous element in score | Partitur fokussiert | Alt+Left |
| `prev-frame` | Previous frame | Go to previous frame | Partitur fokussiert |  |
| `prev-lyric-verse` | Previous lyric verse | Move text/go to previous lyric verse | notation-text-editing | Up |
| `prev-segment-element` | Accessibility: Previous segment element | Select previous in-staff element | Partitur offen | Ctrl+Alt+Shift+Left |
| `prev-system` | Previous system | Go to previous system | Partitur fokussiert |  |
| `prev-text-element` | Previous text element | Go to previous text element | notation-text-editing | Shift+Space Left Backspace |
| `prev-track` | Previous staff or voice | Go to previous staff or voice | Partitur fokussiert |  |
| `put-note` | Put note |  | Partitur offen |  |
| `quadruplet` | Quadruplet | Enter tuplet: quadruplet | Partitur fokussiert | Ctrl+4 |
| `quintuplet` | Quintuplet | Enter tuplet: quintuplet | Partitur fokussiert | Ctrl+5 |
| `realize-chord-symbols` | Realize chord symbols | Realize chord symbols | Partitur offen |  |
| `realtime-advance` | Real-time advance |  | Partitur offen | Enter |
| `rehearsalmark-text` | Rehearsal mark | Add text: rehearsal mark | Partitur offen | Ctrl+M |
| `remove-note` | Remove note |  | Partitur offen |  |
| `repeat-sel` | Repeat selection |  | Partitur offen | R |
| `resequence-rehearsal-marks` | Resequence rehearsal marks | Resequence rehearsal marks | Partitur offen |  |
| `reset` | Reset shapes and positions | Reset shapes and positions | Partitur offen | Ctrl+R |
| `reset-beammode` | Reset beams | Reset beams to default grouping | Partitur offen |  |
| `reset-groupings` | Regroup rhythms | Regroup rhythms | Partitur offen |  |
| `reset-stretch` | Reset layout stretch | Reset layout stretch | Partitur offen |  |
| `reset-style` | Reset style | Reset all style values to default | Partitur offen |  |
| `reset-text-style-overrides` | Reset text style overrides | Reset all text style overrides to default | Partitur offen |  |
| `reset-to-default-layout` | Reset entire score to default layout | Reset entire score to default layout | Partitur offen |  |
| `rest` | Rest | Enter rest | notation-not-note-input-staff-tab | 0 Num+0 |
| `rest-TAB` | Rest | Enter rest | notation-note-input-staff-tab | ; |
| `roman-numeral-text` | Roman numeral analysis | Add text: Roman numeral analysis | Partitur offen |  |
| `save-style` | Save style… | Save style | Partitur offen |  |
| `scoop` | Scoop |  | Partitur offen |  |
| `scr-next` | Screen: Next | Jump to next screen | Partitur offen | PgDown |
| `scr-prev` | Screen: Previous | Jump to previous screen | Partitur offen | PgUp |
| `section-break` | Add/remove section break |  | Partitur offen |  |
| `select-begin-line` | Select to beginning of line |  | Partitur offen | Shift+Home |
| `select-begin-score` | Select to beginning of score |  | Partitur offen | Ctrl+Shift+Home |
| `select-dialog` | More… | Select similar elements with more options | Partitur offen |  |
| `select-end-line` | Select to end of line |  | Partitur offen | Shift+End |
| `select-end-score` | Select to end of score |  | Partitur offen | Ctrl+Shift+End |
| `select-next-chord` | Add next chord to selection | Add to selection: next note/rest | Partitur offen | Shift+Right |
| `select-next-measure` | Select to end of measure |  | Partitur offen | Ctrl+Shift+Right |
| `select-prev-chord` | Add previous chord to selection | Add to selection: previous note/rest | Partitur offen | Shift+Left |
| `select-prev-measure` | Select to beginning of measure |  | Partitur offen | Ctrl+Shift+Left |
| `select-similar` | Similar | Select similar elements | Partitur offen |  |
| `select-similar-range` | Similar in this range | Select similar elements in the selected range | Partitur offen |  |
| `select-similar-staff` | Similar on this staff | Select similar elements on the same staff | Partitur offen |  |
| `select-staff-above` | Add staff above to selection | Add to selection: staff above | Partitur offen | Shift+Up |
| `select-staff-below` | Add staff below to selection | Add to selection: staff below | Partitur offen | Shift+Down |
| `septuplet` | Septuplet | Enter tuplet: septuplet | Partitur fokussiert | Ctrl+7 |
| `set-visible` | Set visible | Make selected element(s) visible | Partitur offen |  |
| `sextuplet` | Sextuplet | Enter tuplet: sextuplet | Partitur fokussiert | Ctrl+6 |
| `sharp` | Toggle sharp | Toggle accidental: sharp | Partitur offen | + Num++ |
| `sharp-post` | Add sharp | Add accidental: sharp | Partitur offen |  |
| `sharp2` | Toggle double-sharp | Toggle accidental: double-sharp | Partitur offen |  |
| `sharp2-post` | Add double-sharp | Add accidental: double-sharp | Partitur offen |  |
| `show-element-bounding-rects` | Show element bounding rectangles | Show/hide element bounding rectangles | Partitur offen |  |
| `show-element-masks` | Show element masks | Show/hide element masks | Partitur offen |  |
| `show-frames` | Show frames | Show/hide frames | Partitur offen |  |
| `show-gap-rests` | Show gap rests |  | Partitur offen |  |
| `show-invisible` | Show invisible | Show/hide invisible elements | Partitur offen |  |
| `show-irregular` | Mark irregular measures | Mark irregular measures | Partitur offen |  |
| `show-line-attach-points` | Show line-attach points | Show/hide line-attach points | Partitur offen |  |
| `show-pageborders` | Show page margins | Show/hide page margins | Partitur offen |  |
| `show-segment-shapes` | Show segment shapes | Show/hide segment shapes | Partitur offen |  |
| `show-skylines` | Show skylines | Show/hide skylines | Partitur offen |  |
| `show-soundflags` | Show sound flags | Show/hide sound flags | Partitur offen |  |
| `show-system-bounding-rects` | Show system bounding rectangles | Show/hide system bounding rectangles | Partitur offen |  |
| `show-unprintable` | Show formatting | Show/hide formatting | Partitur offen |  |
| `slash-fill` | Fill with slashes | Fill with slashes | Partitur offen |  |
| `slash-rhythm` | Toggle rhythmic slash notation | Toggle rhythmic slash notation | Partitur offen |  |
| `slight-bend` | Slight bend |  | Partitur offen |  |
| `split-measure` | Split measure before selected note/rest | Split measure before selected note/rest | Partitur offen |  |
| `staff-properties` | Staff/Part properties… | Staff/Part properties | Partitur offen |  |
| `staff-text` | Staff text | Add text: staff text | Partitur offen | Ctrl+T |
| `staff-text-properties` | Staff text properties… | Staff text properties | Partitur offen |  |
| `standard-bend` | Standard bend |  | Partitur offen | Alt+B |
| `sticking-text` | Sticking | Add text: sticking | Partitur offen |  |
| `stretch+` | Increase layout stretch | Increase layout stretch | Partitur offen | } |
| `stretch-` | Decrease layout stretch | Decrease layout stretch | Partitur offen | { |
| `string-above` | String above (TAB) | Go to string above (TAB) | notation-note-input-staff-tab | Up |
| `string-below` | String below (TAB) | Go to string below (TAB) | notation-note-input-staff-tab | Down |
| `subtitle-text` | Subtitle | Add text: subtitle | Partitur offen |  |
| `system-break` | Add/remove system break |  | Partitur fokussiert | Return Enter |
| `system-text` | System text | Add text: system text | Partitur offen | Ctrl+Shift+T |
| `system-text-properties` | System text properties… | System text properties | Partitur offen |  |
| `tempo` | Tempo marking | Add text: tempo marking | Partitur offen | Alt+Shift+T |
| `text-b` | Bold face | Format text: bold | notation-text-editing | Ctrl+B |
| `text-i` | Italic | Format text: italic | notation-text-editing | Ctrl+I |
| `text-s` | Strikethrough | Format text: strikethrough | notation-text-editing |  |
| `text-sub` | Subscript | Format text: subscript | notation-text-editing |  |
| `text-sup` | Superscript | Format text: superscript | notation-text-editing |  |
| `text-u` | Underline | Format text: underline | notation-text-editing | Ctrl+U |
| `tie` | Tie | Add tied note | Partitur offen | T |
| `time-delete` | Remove selected range | Delete selected measures | Partitur offen | Ctrl+Del Ctrl+Backspace |
| `title-text` | Title | Add text: title | Partitur offen |  |
| `toggle-autoplace` | Toggle automatic placement for selected elements |  | Partitur offen |  |
| `toggle-hide-empty` | Toggle empty staves | Show/hide empty staves | Partitur offen |  |
| `toggle-insert-mode` | Insert/overwrite | Toggle note input mode: insert/overwrite | Partitur offen | Ctrl+I |
| `toggle-mmrest` | Toggle multimeasure rests |  | Partitur offen | Ctrl+Shift+M |
| `toggle-score-lock` | Lock/unlock all systems |  | Partitur offen | Ctrl+Alt+L |
| `toggle-snap-to-next` | Snap to next | Snap to next | Partitur offen |  |
| `toggle-snap-to-previous` | Snap to previous | Snap to previous | Partitur offen |  |
| `toggle-system-lock` | Lock/unlock selected system(s) |  | Partitur offen | Alt+L |
| `toggle-visible` | Toggle visibility of elements |  | Partitur offen | V |
| `top-chord` | Top note in chord | Select top note in chord | Partitur fokussiert | Ctrl+Alt+Up |
| `top-staff` | Go to top staff |  | Partitur fokussiert |  |
| `transpose` | Transpose… | Transpose | Partitur offen |  |
| `transpose-down` | Transpose down | Transpose down a semitone | Partitur offen |  |
| `transpose-up` | Transpose up | Transpose up a semitone | Partitur offen |  |
| `triplet` | Triplet | Enter tuplet: triplet | Partitur fokussiert | Ctrl+3 |
| `tuplet` | Tuplet |  | Partitur offen |  |
| `tuplet-dialog` | Other… | Enter tuplet: other | Partitur fokussiert |  |
| `unroll-repeats` | Unroll repeats | Unroll repeats | Partitur offen |  |
| `unset-visible` | Set invisible | Make selected element(s) invisible | Partitur offen |  |
| `up-chord` | Up note in chord | Select note/rest above | notation-list-selection | Alt+Up |
| `view-mode-continuous` | Continuous view (horizontal) | Display continuous view (horizontal) | Partitur offen |  |
| `view-mode-float` | Floating |  | Partitur offen |  |
| `view-mode-page` | Page view | Display page view | Partitur offen |  |
| `view-mode-single` | Continuous view (vertical) | Display continuous view (vertical) | Partitur offen |  |
| `voice-1` | Voice 1 | Use voice 1 | Partitur offen | Ctrl+Alt+1 |
| `voice-2` | Voice 2 | Use voice 2 | Partitur offen | Ctrl+Alt+2 |
| `voice-3` | Voice 3 | Use voice 3 | Partitur offen | Ctrl+Alt+3 |
| `voice-4` | Voice 4 | Use voice 4 | Partitur offen | Ctrl+Alt+4 |
| `voice-assignment-all-in-instrument` | All voices on instrument | Use all voices on instrument | Partitur offen | Ctrl+Alt+0 |
| `voice-assignment-all-in-staff` | All voices on staff | Use all voices on staff | Partitur offen | Ctrl+Alt+- |
| `voice-x12` | Exchange voice 1-2 | Exchange voice 1-2 | Partitur offen |  |
| `voice-x13` | Exchange voice 1-3 |  | Partitur offen |  |
| `voice-x14` | Exchange voice 1-4 | Exchange voice 1-4 | Partitur offen |  |
| `voice-x23` | Exchange voice 2-3 | Exchange voice 2-3 | Partitur offen |  |
| `voice-x24` | Exchange voice 2-4 |  | Partitur offen |  |
| `voice-x34` | Exchange voice 3-4 | Exchange voice 3-4 | Partitur offen |  |
| `zoom-page-width` | Zoom to page width |  | Partitur offen |  |
| `zoom-two-pages` | Zoom to two pages |  | Partitur offen |  |
| `zoom-whole-page` | Zoom to whole page |  | Partitur offen |  |
| `zoom100` | Zoom to 100% |  | Partitur offen | Ctrl+0 |
| `zoomin` | Zoom in |  | Partitur offen | Ctrl++ Ctrl+= |
| `zoomout` | Zoom out |  | Partitur offen | Ctrl+- Ctrl+Shift+- |

### Paletten (5)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `apply-current-palette-element` | Apply current palette element |  | Partitur offen |  |
| `customize-kit` | Customize kit… | Customize kit | Partitur offen |  |
| `palette-search` | Palette search | Search palettes | immer | Ctrl+F9 |
| `show-keys` | Insert special characters… | Insert special characters | notation-text-editing | Shift+F2 |
| `time-signature-properties` | Time signature properties… | Time signature properties | Partitur offen |  |

### Wiedergabe & Mixer (21)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `clear-online-sounds-cache` | Clear online sounds cache for this score |  | immer |  |
| `countin` | Enable count-in when playing |  | immer |  |
| `loop` | Loop playback | Toggle ‘Loop playback’ | Partitur fokussiert |  |
| `loop-in` | Set loop marker left |  | Partitur fokussiert |  |
| `loop-out` | Set loop marker right |  | Partitur fokussiert |  |
| `metronome` | Metronome | Toggle metronome playback | Partitur fokussiert |  |
| `midi-input-sounding-pitch` | Sounding pitch | Input sounding pitch | immer |  |
| `midi-input-written-pitch` | Written pitch | Input written pitch | immer |  |
| `midi-on` | Enable MIDI input | Toggle MIDI input | immer |  |
| `pan` | Pan score automatically | Pan score automatically during playback | immer |  |
| `pause` | Pause | Pause playback | Partitur fokussiert |  |
| `pause-and-select` | Pause and select | Pause and select playback position | Partitur offen | Ctrl+Space |
| `play` | Play |  | Partitur fokussiert | Space |
| `play-chord-symbols` | Play chord symbols |  | Partitur fokussiert |  |
| `play-from-selection` | Play from selection |  | Partitur offen | Shift+Space |
| `playback-reload-cache` | Reload playback cache |  | immer |  |
| `playback-setup` | Playback setup | Open playback setup dialog | Partitur fokussiert |  |
| `repeat` | Play repeats |  | Partitur fokussiert |  |
| `rewind` | Rewind |  | Partitur fokussiert |  |
| `stop` | Stop | Stop playback | Partitur offen |  |
| `toggle-hear-playback-when-editing` | Hear playback when editing | Toggle hear playback when editing | immer |  |

### Projekt & Dateien (16)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `clear-recent` | Clear list of recent files | Clear list of recent files | immer |  |
| `file-close` | Close | Close | immer |  |
| `file-export` | Export… | Export | immer |  |
| `file-import-audio-to-score` | Import Audio to Score… | Import Audio to Score | immer |  |
| `file-import-pdf` | Import PDF… | Import PDF | immer |  |
| `file-new` | New… | New | immer | Ctrl+N |
| `file-open` | Open… | Open | immer |  |
| `file-publish` | Publish to MuseScore.com… | Publish to MuseScore.com | immer |  |
| `file-save` | Save | Save | immer |  |
| `file-save-a-copy` | Save a copy… | Save a copy | immer |  |
| `file-save-as` | Save as… | Save as | immer | Ctrl+Shift+S |
| `file-save-selection` | Save selection… | Save selection | immer |  |
| `file-save-to-cloud` | Save to cloud… | Save to cloud | immer |  |
| `file-share-audio` | Share on Audio.com… | Share on Audio.com | immer |  |
| `print` | Print… | Print | immer | Ctrl+P |
| `project-properties` | Project properties… | Project properties | immer |  |

### Instrumente (2)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `change-instrument` | Select instrument… | Select instrument | Partitur offen |  |
| `instruments` | Add/remove instruments… | Add/remove instruments | immer | I |

### Audio (3)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `action://audio/dev/use-drivermode` |  |  | deaktiviert |  |
| `action://audio/dev/use-workermode` |  |  | deaktiviert |  |
| `action://audio/dev/use-workerrpcmode` |  |  | deaktiviert |  |

### Extensions (2)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `extensions-show-apidump` | Show API dump |  | deaktiviert |  |
| `manage-plugins` | Manage plugins… | Manage plugins… | immer |  |

### Multiwindow (1)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `multiwindows-dev-show-info` | Multiinstances |  | immer | Ctrl+F3 |

### MuseSampler (2)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `musesampler-check` | Check MuseSampler |  | immer |  |
| `musesampler-reload` | Reload MuseSampler |  | immer |  |

### Tastaturnavigation (17)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `nav-dev-show-controls` |  |  | immer | Ctrl+F1 |
| `nav-down` |  |  |  | Down |
| `nav-escape` |  |  | deaktiviert |  |
| `nav-first-control` |  |  |  | Home |
| `nav-last-control` |  |  |  | End |
| `nav-left` |  |  |  | Left |
| `nav-next-panel` |  |  | immer | Tab |
| `nav-next-section` |  |  | immer | F6 ` |
| `nav-next-tab` |  |  | immer | Ctrl+Tab |
| `nav-nextrow-control` |  |  |  | PgDown |
| `nav-prev-panel` |  |  | immer | Shift+Tab |
| `nav-prev-section` |  |  | immer | Shift+F6 Shift+` |
| `nav-prev-tab` |  |  | immer | Ctrl+Shift+Tab |
| `nav-prevrow-control` |  |  |  | PgUp |
| `nav-right` |  |  |  | Right |
| `nav-trigger-control` |  |  |  | Return Enter Space |
| `nav-up` |  |  |  | Up |

### Update (1)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `check-update` | Check for update |  | immer |  |

### VST (2)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `vst-use-newview` | Use new view |  | deaktiviert |  |
| `vst-use-oldview` | Use old view |  | deaktiviert |  |

### Workspaces (3)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `configure-workspaces` | Edit workspaces… | Edit workspaces | immer |  |
| `create-workspace` | Create new workspace |  | immer |  |
| `select-workspace` | Select workspace |  | immer |  |

### Diagnose (Dev) (14)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `action://diagnostic/actions/query` |  |  | deaktiviert |  |
| `action://diagnostic/actions/query_params1` |  |  | deaktiviert |  |
| `action://diagnostic/actions/query_params2` |  |  | deaktiviert |  |
| `diagnostic-accessible-tree-dump` | Dump accessibility tree to console | Dump accessibility tree to console | deaktiviert |  |
| `diagnostic-save-diagnostic-files` | Save diagnostic files |  | deaktiviert |  |
| `diagnostic-show-accessible-tree` | Show accessibility tree… | Show accessibility tree | deaktiviert | Ctrl+F2 |
| `diagnostic-show-actions` | Show actions list | Show actions list | deaktiviert |  |
| `diagnostic-show-engraving-elements` | Show engraving elements | Show engraving elements | deaktiviert |  |
| `diagnostic-show-engraving-style` | Show engraving style options list | Show engraving style options list | deaktiviert |  |
| `diagnostic-show-engraving-undostack` | Show engraving undo stack | Show engraving undo stack | deaktiviert |  |
| `diagnostic-show-graphicsinfo` | Show graphics info… | Show graphics info | deaktiviert |  |
| `diagnostic-show-navigation-tree` | Show navigation tree… | Show navigation tree | deaktiviert |  |
| `diagnostic-show-paths` | Show paths… | Show paths | deaktiviert |  |
| `diagnostic-show-profiler` | Show profiler… | Show profiler | deaktiviert |  |

### Autobot (Dev) (1)

| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |
|---|---|---|---|---|
| `autobot-show-scripts` | Show scripts… | Show scripts | deaktiviert |  |
