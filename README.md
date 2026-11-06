# Mobility exercise content

Public JSON feed of gentle, low-intensity, chair-friendly mobility exercises for older
adults, consumed by a private wellness app. **Not medical advice** — a starting template
to review with a care team before use.

- `exercises.json` — the live monthly set the app fetches.
- `months/` — archived monthly sets.
- `images/` — labeled placeholder illustrations.
- `exercises.schema.json` — the schema each file validates against.
- `validate.py` — `python3 validate.py` checks the files (10 exercises, >= 2 balance moves,
  a seated option + safety cue on every move).

## Swapping next month

```bash
cp months/exercises-2026-03.json months/exercises-2026-04.json
# edit the new file (keep 10 exercises, >= 2 balance, seated option + safety cue each)
python3 validate.py months/exercises-2026-04.json      # must pass
cp months/exercises-2026-04.json exercises.json         # promote to live
git add -A && git commit -m "content: April 2026" && git push
```

The app picks up the new `exercises.json` on the 1st; it keeps the last good set cached and
falls back to a bundled copy if the fetch ever fails.
