"""Detection + tracking + counting pipeline, shared by the live server and the video evaluator.

Two ways to count (set with COUNT_MODE):

  track  Count each tracked object once, the first time it is confirmed.
         Right for a fixed camera. A moving camera recounts items it pans back to,
         because the tracker forgets objects that leave the frame for more than ~30 frames.

  line   Count an object only when its center crosses a horizontal line
         (LINE_POSITION, as a fraction of frame height) in LINE_DIRECTION.
         Right for a walking survey: walk forward, litter moves down the frame,
         and each item crosses the line once. Panning sideways does not cross it.

Both modes also report "in view": how many tracked objects are visible in the current frame.
"""
import threading
from dataclasses import dataclass, field

from detection.yolo_model import load_model
from tracking.tracking import TrackerManager

COUNT_MODES = ("track", "line")
LINE_DIRECTIONS = ("down", "up", "any")


@dataclass
class CountEvent:
    track_id: str
    class_id: int
    class_name: str
    confidence: float
    bbox_ltrb: tuple
    frame_index: int


@dataclass
class CounterState:
    """Thread-safe counters read by the API and written by the detection loop."""
    total: int = 0
    since_last_alert: int = 0
    in_view: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, n: int = 1):
        with self._lock:
            self.total += n
            self.since_last_alert += n

    def set_in_view(self, n: int):
        with self._lock:
            self.in_view = n

    def reset_alert_window(self):
        with self._lock:
            self.since_last_alert = 0

    def snapshot(self):
        with self._lock:
            return {"total": self.total, "since_last_alert": self.since_last_alert, "in_view": self.in_view}


class TrashCounter:
    """Runs YOLO on a frame, tracks objects, and counts them by the chosen mode."""

    def __init__(self, model_path: str, conf_threshold: float = 0.25, count_mode: str = "track",
                 line_position: float = 0.8, line_direction: str = "down", model=None):
        if count_mode not in COUNT_MODES:
            raise ValueError(f"COUNT_MODE must be one of {COUNT_MODES}, got {count_mode!r}")
        if line_direction not in LINE_DIRECTIONS:
            raise ValueError(f"LINE_DIRECTION must be one of {LINE_DIRECTIONS}, got {line_direction!r}")
        if not 0.0 < line_position < 1.0:
            raise ValueError(f"LINE_POSITION must be between 0 and 1, got {line_position}")
        self.model = model if model is not None else load_model(model_path)
        self.names = getattr(self.model, "names", {0: "trash"})
        self.conf_threshold = conf_threshold
        self.count_mode = count_mode
        self.line_position = line_position
        self.line_direction = line_direction
        self.tracker = TrackerManager()
        self.counted_ids = set()
        self.last_center_y = {}   # track_id -> center y in the previous frame it was seen
        self.frame_index = 0
        self.in_view = 0

    def line_y(self, frame_height: int) -> float:
        return self.line_position * frame_height

    def _crossed(self, prev_y: float, y: float, line: float) -> bool:
        down = prev_y < line <= y
        up = prev_y > line >= y
        if self.line_direction == "down":
            return down
        if self.line_direction == "up":
            return up
        return down or up

    def update_from_boxes(self, boxes, frame):
        """Track and count given detector boxes. Split out from process() so it can be tested without a model."""
        tracks = self.tracker.update(boxes, frame, self.conf_threshold)
        visible = [t for t in tracks if t.time_since_update == 0]
        self.in_view = len(visible)
        line = self.line_y(frame.shape[0])

        events = []
        for track in visible:
            tid = track.track_id
            l, t, r, b = track.to_ltrb()
            cy = (t + b) / 2
            prev_y = self.last_center_y.get(tid)
            self.last_center_y[tid] = cy
            if tid in self.counted_ids:
                continue
            if self.count_mode == "line" and (prev_y is None or not self._crossed(prev_y, cy, line)):
                continue
            self.counted_ids.add(tid)
            class_id = int(track.get_det_class()) if track.get_det_class() is not None else -1
            conf = track.get_det_conf()
            events.append(CountEvent(
                track_id=str(tid),
                class_id=class_id,
                class_name=self.names.get(class_id, "unknown"),
                confidence=round(float(conf), 3) if conf is not None else -1.0,
                bbox_ltrb=(round(float(l), 1), round(float(t), 1), round(float(r), 1), round(float(b), 1)),
                frame_index=self.frame_index,
            ))

        # forget tracks the tracker has dropped, so the dict does not grow forever
        live_ids = {t.track_id for t in tracks}
        for tid in list(self.last_center_y):
            if tid not in live_ids:
                del self.last_center_y[tid]

        self.frame_index += 1
        return visible, events

    def process(self, frame):
        """Returns (visible_tracks, new_count_events) for one frame."""
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        boxes = results[0].boxes if results else None
        return self.update_from_boxes(boxes, frame)
