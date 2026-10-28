# Projekt: reformat-exercises

Ziel: In allen .xlsx-Dateien unter `data\Fragenabgabe\` (beliebig tief verschachtelt) wird die Spalte
`Loesungsweg_Text (mit {Variable})` in ein einheitliches Schreibschema (Schema 1) überführt.
Danach werden die Aufgabentexte angepasst, damit im Lösungsweg genannte Variablennamen im Aufgabentext erkennbar sind.

Drei Claude-Sessions arbeiten parallel und kommunizieren ausschließlich über Dateien:
- INSPECTOR: korrigiert die Lösungswege (Output: `data\Fragenabgabe_v1_formatiert\`)
- REVIEWER: prüft die Arbeit des Inspectors unabhängig und gibt Dateien frei
- AUDITOR: prüft die Logik der freigegebenen Dateien, ergänzt Variablennamen "(X)" in der Spalte `Aufgabenbeschreibung` (Output: `data\Fragenabgabe_v2_audit\`)

Jede Session kennt die anderen beiden und weiß, dass sie parallel laufen.

## Arbeitsregeln für alle Sessions
- Arbeite autonom, keine Rückfragen an den Nutzer. Annahmen kommen in den Abschlussreport.
- Sprache: Berichte und Nachrichten auf Deutsch, Code und Dateinamen englisch.
- Windows/PowerShell. Pfade mit Backslash. Python mit openpyxl bevorzugt. Dateien immer mit UTF-8 schreiben.
- `data\Fragenabgabe\` (Original) und alle Dateien, die nicht deiner Rolle gehören, sind READ-ONLY. Niemals überschreiben.
- Ignoriere temporäre Excel-Dateien (`~$*.xlsx`).
- Nicht raten: Bei Unsicherheit Zelle unverändert lassen und als Problem mit Kategorie melden.
- Jede Session schreibt nur in ihren eigenen Kommunikationsordner und liest die der anderen.
- Fehlende Ordner selbst anlegen.

## Ordnerstruktur
| Zweck | Pfad (relativ zum Root) |
|---|---|
| Original (RO) | `data\Fragenabgabe\` |
| Output Inspector | `data\Fragenabgabe_v1_formatiert\` (gleiche Unterordner und Dateinamen) |
| Output Auditor | `data\Fragenabgabe_v2_audit\` (gleiche Unterordner und Dateinamen) |
| Kommunikation Inspector | `modules\communication\inspector\` |
| Kommunikation Reviewer | `modules\communication\reviewer\` |
| Kommunikation Auditor | `modules\communication\auditor\` |
| Eigene Skripte | `modules\tools\` (jede Session nur eigene Dateien: `inspector_tool.py`, `reviewer_check.py`, `auditor_tool.py`) |

`file_id` = relativer Pfad der Excel-Datei ab `data\Fragenabgabe\` (z. B. `Kapitel1\Aufgaben\Datei.xlsx`).

## Zielspalte und Schemata
Header der Zielspalte: `Loesungsweg_Text (mit {Variable})` (tolerant matchen: Whitespace, Groß-/Kleinschreibung). Alle Sheets prüfen.
Fehlende Spalte oder mehrere passende Spalten sind ein Problem der Datei.

**Schema 1 (korrekt):** Jede Formel/Gleichung mit {Platzhaltern} steht zuerst ohne geschweifte Klammern, danach mit geschweiften Klammern, verbunden mit " = ".

```
Rentenbarwertfaktor: RBF(i, n) = ((1 + i)^n − 1) / (i · (1 + i)^n) = ((1 + {i})^{n} − 1) / ({i} · (1 + {i})^{n}).
Kapitalwerte: K_0(A) = −I0A € + CFA € · RBF(i, n) = −{I0A} € + {CFA} € · RBF(i, n); K_0(B) = −I0B € + CFB € · RBF(i, n) = −{I0B} € + {CFB} € · RBF(i, n).
Annuitäten: A(A) = K_0(A) / RBF(i, n); A(B) = K_0(B) / RBF(i, n).
Beide Annuitäten sind positiv, die Investitionen sind also prinzipiell vorteilhaft. Investition A hat die höhere Annuität und ist daher vorzuziehen.
```

**Schema 2 (falsch):** Direkt die Formel mit {}-Klammern, ohne vorangestellte klammerfreie Variante:

```
Rentenbarwertfaktor: RBF(i, n) = ((1 + {i})^{n} − 1) / ({i} · (1 + {i})^{n}).
Kapitalwerte: K_0(A) = −{I0A} € + {CFA} € · RBF(i, n); K_0(B) = −{I0B} € + {CFB} € · RBF(i, n).
```

### Transformationsregeln (Schema 2 → Schema 1)
1. Nur der Ausdruck mit {Platzhaltern} bekommt davor seine klammerfreie Kopie (alle `{X}` → `X`, auch `^{n}` → `^n`), verbunden mit " = ". Alles andere bleibt zeichengleich (Operatoren, Leerzeichen, Einheiten, Unicode wie −, ·, €).
2. Ausdrucksgrenzen: Teil einer Gleichungskette zwischen "="-Zeichen bzw. Satz-/Listengrenzen (`;` oder `.`). Ein vorangehender Teil ohne Platzhalter (z. B. `RBF(i, n) =`) bleibt stehen; die klammerfreie Kopie kommt direkt vor den Ausdruck mit Platzhaltern.
   - `RBF(i, n) = ((1 + {i})^{n} − 1) / ...` → `RBF(i, n) = ((1 + i)^n − 1) / ... = ((1 + {i})^{n} − 1) / ...`
   - `0 = −{A} + {E1}/(1+i) + {E2}/(1+i)^2.` → `0 = −A + E1/(1+i) + E2/(1+i)^2 = −{A} + {E1}/(1+i) + {E2}/(1+i)^2.`
   - `{A}·x^2 − {E1}·x − {E2} = 0.` → `A·x^2 − E1·x − E2 = {A}·x^2 − {E1}·x − {E2} = 0.`
3. Idempotenz: Bereits korrekte Zellen bleiben unverändert und werden nie ein zweites Mal korrigiert. Zellen ohne Platzhalter bleiben unverändert. Gemischte Zellen werden nur an den Schema-2-Stellen korrigiert.
4. Unsichere Fälle (mehrdeutige Grenzen, Klammern in Fließtext, verschachtelt, leere Zelle, Rich Text, Formelzelle) nicht raten, sondern unverändert lassen und als `problem` mit Kategorie melden. Kategorien als Slug: `mixed_schema`, `braces_in_prose`, `ambiguous_expression`, `no_header`, `multiple_target_columns`, `rich_text`, `empty_cell`, `other:<kurz>`.
5. Außerhalb der Zielspalte darf sich nichts ändern (Werte, Sheets, Formatierung, Spaltenbreiten, Validierungen). Nach dem Speichern per Diff prüfen.

### Aufgabe des Auditors (Aufgabenbeschreibung)
Im Lösungsweg stehen jetzt klammerfreie Namen (A, E1, E2 ...), die im Aufgabentext nur als `{E1} €` vorkommen. Im Aufgabentext wird daher direkt hinter den Platzhalter samt direkt folgender Einheit ` (X)` eingefügt:
`{E1} €` → `{E1} € (E1)`, `{i} %` → `{i} % (i)`, `{n} Jahre` → `{n} Jahre (n)`, ohne Einheit `{n}` → `{n} (n)`.
Nur das erste Vorkommen annotieren, bereits vorhandene `(X)` nicht verdoppeln. Hilfsvariablen des Lösungswegs (x, i_IRR, RBF, K_0(A) ...) werden nicht annotiert.
Platzhalter im Lösungsweg, die im Aufgabentext fehlen, werden nur gemeldet, nicht geändert.

## Kommunikationsprotokoll
Nachrichten sind JSON-Dateien im Ordner des Absenders: `<NNNN>_<absender>_to_<empfänger>_<typ>.json` (NNNN fortlaufend pro Absender, vierstellig).
Felder: `seq, from, to, type, file_id, round, verdict, summary, details` (nicht benötigte Felder weglassen).

| Typ | Absender → Empfänger | Bedeutung |
|---|---|---|
| `manifest` | inspector → reviewer, auditor | Liste aller Dateien |
| `submission` | inspector → reviewer (cc auditor) | Datei (Runde N) eingereicht |
| `review` | reviewer → inspector (cc auditor) | `verdict`: `approved` / `changes_requested` / `approved_with_unresolved` |
| `audit_finding` | auditor → inspector (cc reviewer) | Formatfehler in v1 gefunden |
| `audit_done` | auditor → inspector, reviewer | Datei im Audit abgeschlossen |

Jede Session pflegt `state.json` in ihrem Ordner (aktuelle Datei, Runde, offen/erledigt, Zeitstempel).

Flag-Dateien: `inspector\ALL_SUBMITTED.flag`, `reviewer\ALL_REVIEWED.flag`, `<rolle>\DONE.flag`.
Freigabe-Logik: Der Auditor bearbeitet eine Datei erst nach `review` mit `approved` oder `approved_with_unresolved`. Nach einem `audit_finding` muss der Reviewer die Datei erneut freigeben.

Regeln zur Zusammenarbeit:
- Maximal 3 Runden pro Datei. Danach `unresolved` und weiter zur nächsten Datei.
- Der Inspector darf dem Reviewer sachlich widersprechen (und umgekehrt). Belegte Argumente zählen.
- Nicht blockieren: Während auf Feedback gewartet wird, an anderen Dateien weiterarbeiten.
- Polling: `Start-Sleep -Seconds 20` (Auditor: 30), danach Ordner der anderen erneut lesen. Kein einzelnes Sleep über 60 Sekunden.
- Bleibt eine erwartete Antwort länger als 10 Minuten aus: Vermerk in `state.json`, weiterarbeiten, später erneut nachfragen.
- Lies bei jedem Poll nur NEUE Nachrichten (merke dir die höchste verarbeitete `seq` je Absender in `state.json`).

## Abschlussberichte (Deutsch)
- Inspector: `modules\communication\inspector\FINAL_REPORT.md` (Zahlen, Probleme gruppiert nach Kategorie mit Datei/Sheet/Zeile, Beispiele, Empfehlung)
- Reviewer: `modules\communication\reviewer\REVIEW_SIGNOFF.md`
- Auditor: `modules\communication\auditor\AUDIT_REPORT.md`