# Champions Tracker

Watches a capture card feed, reads the on-screen text with Apple Vision OCR,
and logs each match (your team, opponent's team, win/loss) to SQLite.
No vision-language model needed for the normal path, so it runs light on an M1 Pro.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python fetch_species.py en        # or es / fr / de / it, matching your game language
```

Allow camera access for your terminal in System Settings > Privacy & Security > Camera.
If the capture card isn't index 0, try 1, 2... (or use OBS's virtual camera).

## Calibrate (one time)

The region coordinates in `config.yaml` are placeholders. For each screen
(team preview, mid-battle, win, loss):

1. Get the game on that screen (or save a screenshot / record a short clip).
2. `python calibrate.py` (or `--image shot.png` / `--source clip.mp4`)
3. Open `calibration.png`, check the boxes land on the right text, and read the
   printed OCR output. Edit `config.yaml` and repeat until names and keywords read correctly.

Set the state `keywords` to the exact words your game shows, in your game's language.

## Run

```bash
python main.py --debug            # watch the capture card, verbose
python main.py --source clip.mp4  # test against a recorded match
python stats.py                   # record and win rate vs each opponent Pokémon
```

## How it works

1. Samples about 1 frame per second.
2. `states.py` checks keyword text in fixed regions to know the screen:
   win, loss, team_preview, battle.
3. On team preview and in battle, `main.py` OCRs the name regions and
   `matcher.py` fuzzy-matches them against `species.txt`.
4. On a win/loss screen it saves a screenshot and writes the match to `matches.sqlite`.

## Tuning tips

- A state must be seen `debounce` samples in a row before acting, which filters transitions.
- If a name misreads often, tighten the region around the text, or raise `min_score`.
- Always check `screenshots/` against logged results for the first few matches.
- Optional next step: when OCR fails on a region, send that crop to a local VLM
  (e.g. Qwen2.5-VL via MLX) as a fallback.
