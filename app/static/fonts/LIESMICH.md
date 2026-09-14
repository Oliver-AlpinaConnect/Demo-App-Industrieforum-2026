# Schriften

Hier liegen die Schriftdateien. Die App ruft keinen externen Font-Server auf (Hausregel).

Erwartet werden:

- `BarlowCondensed-SemiBold.woff2` (600)
- `BarlowCondensed-Bold.woff2` (700)
- `Inter-Regular.woff2` (400)
- `Inter-SemiBold.woff2` (600)

Fehlen die Dateien, greift der Fallback `system-ui, sans-serif`. Das Layout bleibt gleich,
nur die Schrift sieht anders aus. Die Dateien sind nicht im Repository, weil sie unter
eigener Lizenz stehen; der Betrieb legt sie beim Aufsetzen ab (siehe `docs/betrieb.md`).
