"""Fuzzy-match OCR text against a species list."""
import re
from rapidfuzz import fuzz, process

FORM_PREFIXES = ("mega ", "mega-", "méga-", "méga ")


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\-'.:é♀♂]", "", text)
    return re.sub(r"\s+", " ", text)


class SpeciesMatcher:
    def __init__(self, path, min_score=85):
        with open(path, encoding="utf-8") as f:
            self.names = [line.strip() for line in f if line.strip()]
        self.norm = [normalize(n) for n in self.names]
        self.min_score = min_score

    def match(self, text):
        """Return (species, is_mega) or None if nothing is close enough."""
        t = normalize(text)
        if not t:
            return None
        is_mega = False
        for p in FORM_PREFIXES:
            if t.startswith(p):
                is_mega, t = True, t[len(p):]
                break
        hit = process.extractOne(t, self.norm, scorer=fuzz.WRatio, score_cutoff=self.min_score)
        if hit is None:
            return None
        return self.names[hit[2]], is_mega
