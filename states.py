"""Decide which screen the game is on by looking for keywords in fixed regions."""
from ocr import read_joined


class StateDetector:
    def __init__(self, state_cfgs, languages=None):
        self.state_cfgs = state_cfgs
        self.languages = languages

    def detect(self, frame):
        # Cache OCR per region so states sharing a region only cost one OCR call.
        cache = {}
        for spec in self.state_cfgs:
            key = tuple(spec["region"])
            if key not in cache:
                cache[key] = read_joined(frame, spec["region"], self.languages)
            text = cache[key]
            if any(k.lower() in text for k in spec["keywords"]):
                return spec["name"]
        return "unknown"
