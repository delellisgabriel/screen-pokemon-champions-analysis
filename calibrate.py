"""Grab one frame, draw every configured region on it, and print what OCR reads.

Usage:
    python calibrate.py                     # use the capture card
    python calibrate.py --image shot.png    # use a saved screenshot
    python calibrate.py --source clip.mp4   # first frame of a recording

Open calibration.png, check the boxes sit on the right UI elements, edit
config.yaml, and repeat. Do this once per screen (preview, battle, result).
"""
import argparse

import cv2
import yaml

from capture import FrameSource
from matcher import SpeciesMatcher
from ocr import crop, read_text


def draw(frame, region, label, color):
    h, w = frame.shape[:2]
    x, y, rw, rh = region
    p1, p2 = (int(x * w), int(y * h)), (int((x + rw) * w), int((y + rh) * h))
    cv2.rectangle(frame, p1, p2, color, 2)
    cv2.putText(frame, label, (p1[0], max(p1[1] - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--image")
    ap.add_argument("--source")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))

    if args.image:
        frame = cv2.imread(args.image)
    else:
        source = args.source if args.source is not None else cfg["capture"]["source"]
        if isinstance(source, str) and source.isdigit():
            source = int(source)
        src = FrameSource(source, cfg["capture"]["width"], cfg["capture"]["height"])
        for _ in range(10):  # let the camera warm up
            frame = src.grab()
        src.release()
    if frame is None:
        raise SystemExit("Could not get a frame.")

    matcher = SpeciesMatcher(cfg["species"]["file"], cfg["species"]["min_score"])
    out = frame.copy()

    print("== States ==")
    for s in cfg["states"]:
        text = " ".join(t for t, _ in read_text(crop(frame, s["region"])))
        print(f"{s['name']:14} region={s['region']} OCR={text!r}")
        draw(out, s["region"], s["name"], (0, 200, 255))

    print("\n== Name regions ==")
    for screen, groups in cfg["name_regions"].items():
        for group, regions in groups.items():
            for i, r in enumerate(regions):
                texts = [t for t, _ in read_text(crop(frame, r))]
                hit = matcher.match(texts[0]) if texts else None
                print(f"{screen}/{group}[{i}] OCR={texts} -> {hit}")
                draw(out, r, f"{group[:3]}{i}", (0, 255, 0))

    cv2.imwrite("calibration.png", out)
    print("\nWrote calibration.png")


if __name__ == "__main__":
    main()
