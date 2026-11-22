"""Quick stats from matches.sqlite: overall record and win rate vs each opponent Pokémon."""
import json
import sqlite3
import sys
from collections import defaultdict

conn = sqlite3.connect(sys.argv[1] if len(sys.argv) > 1 else "matches.sqlite")
rows = conn.execute("SELECT result, opp_seen FROM matches").fetchall()
if not rows:
    sys.exit("No matches logged yet.")

wins = sum(1 for r, _ in rows if r == "win")
print(f"Record: {wins}-{len(rows) - wins} ({wins / len(rows):.0%} win rate over {len(rows)} matches)\n")

vs = defaultdict(lambda: [0, 0])  # species -> [wins, games]
for result, seen in rows:
    for sp in json.loads(seen):
        vs[sp][1] += 1
        vs[sp][0] += result == "win"

print("Win rate vs opponent Pokémon (min 2 games):")
for sp, (w, g) in sorted(vs.items(), key=lambda kv: -kv[1][1]):
    if g >= 2:
        print(f"  {sp:20} {w}/{g}  {w / g:.0%}")
