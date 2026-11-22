"""Frame source: a capture card (or OBS virtual camera) or a recorded video file."""
import cv2


class FrameSource:
    def __init__(self, source=0, width=1920, height=1080):
        self.is_file = isinstance(source, str)
        if self.is_file:
            self.cap = cv2.VideoCapture(source)
        else:
            self.cap = cv2.VideoCapture(int(source), cv2.CAP_AVFOUNDATION)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open source {source!r}. On macOS, allow camera access "
                "for your terminal in System Settings > Privacy & Security > Camera, "
                "and try other indexes (0, 1, 2...) since the built-in webcam is usually 0."
            )

    def grab(self):
        """Return the latest BGR frame, or None at end of file / on failure."""
        if not self.is_file:
            # drop buffered frames so we analyse "now", not a stale frame
            for _ in range(2):
                self.cap.grab()
        ok, frame = self.cap.read()
        return frame if ok else None

    def skip_seconds(self, seconds):
        """For video files: jump ahead so sampling matches wall-clock spacing."""
        if self.is_file:
            fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos + fps * seconds)

    def release(self):
        self.cap.release()
