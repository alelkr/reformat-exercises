# Reformat Exercise sheets for rendering

cd C:\Users\smaikrau\reformat-exercises
claude --agent inspector "Starte jetzt deine Arbeit als INSPECTOR gemäß CLAUDE.md und deiner Agent-Definition. Reviewer und Auditor starten parallel in eigenen Sessions. Arbeite autonom bis zum Abschlussreport und DONE.flag."  

cd C:\Users\smaikrau\reformat-exercises
claude --agent reviewer "Starte jetzt deine Arbeit als REVIEWER gemäß CLAUDE.md und deiner Agent-Definition. Inspector und Auditor laufen parallel in eigenen Sessions. Warte auf das Manifest des Inspectors und arbeite autonom bis zum REVIEW_SIGNOFF.md und DONE.flag."

cd C:\Users\smaikrau\reformat-exercises
claude --agent auditor "Starte jetzt deine Arbeit als AUDITOR gemäß CLAUDE.md und deiner Agent-Definition. Inspector und Reviewer laufen parallel in eigenen Sessions. Warte auf Freigaben des Reviewers und arbeite autonom bis zum AUDIT_REPORT.md und DONE.flag."