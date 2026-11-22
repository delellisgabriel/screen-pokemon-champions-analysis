import json
import sqlite3
import time


class MatchDB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                result TEXT NOT NULL,
                my_team TEXT NOT NULL,
                opp_team TEXT NOT NULL,
                opp_seen TEXT NOT NULL,
                screenshot TEXT
            )"""
        )
        self.conn.commit()

    def add(self, result, my_team, opp_team, opp_seen, screenshot=None):
        self.conn.execute(
            "INSERT INTO matches (ts, result, my_team, opp_team, opp_seen, screenshot) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                time.strftime("%Y-%m-%d %H:%M:%S"),
                result,
                json.dumps(my_team),
                json.dumps(opp_team),
                json.dumps(sorted(opp_seen)),
                screenshot,
            ),
        )
        self.conn.commit()
