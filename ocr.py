"""Text reading with Apple's Vision framework (via ocrmac). Fast on M-series chips."""
import cv2
from PIL import Image
from ocrmac import ocrmac


def crop(frame, region):
    h, w = frame.shape[:2]
    x, y, rw, rh = region
    x0, y0 = int(x * w), int(y * h)
    x1, y1 = int((x + rw) * w), int((y + rh) * h)
    return frame[max(y0, 0):y1, max(x0, 0):x1]


def read_text(img_bgr, languages=None):
    """Return a list of (text, confidence) for an image crop."""
    if img_bgr is None or img_bgr.size == 0:
        return []
    h, w = img_bgr.shape[:2]
    # Upscale small crops: Vision is noticeably more accurate on larger text.
    if h < 80:
        scale = 80 / h
        img_bgr = cv2.resize(img_bgr, (int(w * scale), 80), interpolation=cv2.INTER_CUBIC)
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    kwargs = {"recognition_level": "accurate"}
    if languages:
        kwargs["language_preference"] = languages
    results = ocrmac.OCR(pil, **kwargs).recognize()
    return [(text, conf) for text, conf, _bbox in results]


def read_joined(frame, region, languages=None):
    """OCR a region of a full frame and return one lowercase string."""
    parts = read_text(crop(frame, region), languages)
    return " ".join(t for t, _ in parts).lower()
