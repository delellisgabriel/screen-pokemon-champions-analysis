"""Watch the capture card, track each match, and log team + result."""
import argparse
import os
import time

import cv2
import yaml

from capture import FrameSource
from db import MatchDB
from matcher import SpeciesMatcher
from ocr import crop, read_text
from states import StateDetector


class MatchTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.active = False
        self.my_team = []
        self.opp_team = []
        self.opp_seen = set()

    @staticmethod
    def _add(lst, name, cap=6):
        if name not in lst and len(lst) < cap:
            lst.append(name)


def read_names(frame, regions, matcher, debug=False):
    found = []
    for region in regions:
        for text, _conf in read_text(crop(frame, region)):
            hit = matcher.match(text)
            if debug:
                print(f"    OCR {text!r} -> {hit}")
            if hit:
                species, is_mega = hit
                found.append(f"Mega {species}" if is_mega else species)
                break
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--source", help="camera index or video file (overrides config)")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    source = args.source if args.source is not None else cfg["capture"]["source"]
    if isinstance(source, str) and source.isdigit():
        source = int(source)

    src = FrameSource(source, cfg["capture"]["width"], cfg["capture"]["height"])
    matcher = SpeciesMatcher(cfg["species"]["file"], cfg["species"]["min_score"])
    detector = StateDetector(cfg["states"])
    db = MatchDB(cfg["db"])
    os.makedirs(cfg["screenshots_dir"], exist_ok=True)
    interval = cfg["capture"]["sample_interval"]
    names = cfg["name_regions"]

    tracker = MatchTracker()
    last_state, streak = None, 0
    print("Watching... Ctrl+C to stop.")

    try:
        while True:
            t0 = time.time()
            frame = src.grab()
            if frame is None:
                print("No more frames.")
                break

            state = detector.detect(frame)
            streak = streak + 1 if state == last_state else 1
            last_state = state
            if args.debug:
                print(f"[{time.strftime('%H:%M:%S')}] state={state} streak={streak}")

            if streak >= cfg["debounce"]:
                if state == "team_preview":
                    tracker.active = True
                    for n in read_names(frame, names["team_preview"]["mine"], matcher, args.debug):
                        tracker._add(tracker.my_team, n)
                    for n in read_names(frame, names["team_preview"]["opponent"], matcher, args.debug):
                        tracker._add(tracker.opp_team, n)
                        tracker.opp_seen.add(n)
                elif state == "battle":
                    tracker.active = True
                    for n in read_names(frame, names["battle"]["opponent_active"], matcher, args.debug):
                        tracker.opp_seen.add(n)
                elif state in ("win", "loss") and tracker.active:
                    shot = os.path.join(cfg["screenshots_dir"], f"{time.strftime('%Y%m%d-%H%M%S')}-{state}.png")
                    cv2.imwrite(shot, frame)
                    db.add(state, tracker.my_team, tracker.opp_team, tracker.opp_seen, shot)
                    print(f"Logged {state.upper()}: mine={tracker.my_team} "
                          f"opp_preview={tracker.opp_team} opp_seen={sorted(tracker.opp_seen)}")
                    tracker.reset()

            src.skip_seconds(interval)
            time.sleep(max(0.0, interval - (time.time() - t0)) if not src.is_file else 0)
    except KeyboardInterrupt:
        pass
    finally:
        src.release()


if __name__ == "__main__":
    main()
