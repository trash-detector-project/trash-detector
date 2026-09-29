# Run: python tests/test_counting_modes.py
"""Compares the two counting modes on synthetic clips with a known answer.

No detection model is used: boxes are fed straight to the real tracker, so this tests
the tracking and counting logic only. Real footage will be messier.

Scenarios
  fixed     Fixed camera, 3 items sitting still.                     True count: 3
  walk      Walking forward, 5 items pass from top to bottom.         True count: 5
  walk+pan  Walking forward while sweeping the camera side to side,
            so items leave the frame and come back.                   True count: 5
"""
import os
import random
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import TrashCounter  # noqa: E402

H, W = 480, 640
COLORS = [(0, 0, 255), (0, 200, 0), (255, 0, 0), (0, 200, 255), (200, 0, 200)]


class _Arr:
    def __init__(self, a):
        self.a = np.array(a, dtype=float)

    def cpu(self):
        return self

    def numpy(self):
        return self.a


class FakeBoxes:
    """Mimics the parts of an ultralytics Boxes object the tracker reads."""

    def __init__(self, dets):
        self.xyxy = _Arr([d[0] for d in dets] or np.zeros((0, 4)))
        self.conf = _Arr([d[1] for d in dets])
        self.cls = _Arr([0 for _ in dets])

    def __len__(self):
        return len(self.conf.a)


def make_clip(scenario, seed):
    rng = random.Random(seed)
    frames = []
    if scenario == "fixed":
        items = [(120, 150), (300, 250), (480, 180)]
        n, vy, sweep = 90, 0, 0
    else:
        items = [(100 + i * 100, -60 - i * 110) for i in range(5)]  # start above the frame, staggered
        n, vy = 260, 4
        sweep = 0 if scenario == "walk" else 220
    for f in range(n):
        img = np.full((H, W, 3), 90, np.uint8)
        dets = []
        dx = int(sweep * np.sin(f / 18)) if sweep else 0
        for i, (x0, y0) in enumerate(items):
            x, y, w, h = x0 + dx, y0 + vy * f, 60, 45
            if x < 0 or y < 0 or x + w > W or y + h > H:
                continue  # out of frame
            img[y:y + h, x:x + w] = COLORS[i % len(COLORS)]
            if rng.random() > 0.08:  # detector misses about 8% of frames
                j = lambda: rng.uniform(-3, 3)  # noqa: E731
                dets.append(((x + j(), y + j(), x + w + j(), y + h + j()), rng.uniform(0.5, 0.9)))
        frames.append((img, FakeBoxes(dets)))
    return frames


def count(frames, mode):
    c = TrashCounter("", conf_threshold=0.25, count_mode=mode, line_position=0.8,
                     line_direction="down", model=object())
    max_in_view = 0
    for img, boxes in frames:
        c.update_from_boxes(boxes, img)
        max_in_view = max(max_in_view, c.in_view)
    return len(c.counted_ids), max_in_view


if __name__ == "__main__":
    truth = {"fixed": 3, "walk": 5, "walk+pan": 5}
    print(f"{'scenario':<10} {'true':>4} {'track mode':>11} {'line mode':>10} {'max in view':>12}")
    for scenario in ("fixed", "walk", "walk+pan"):
        track_counts, line_counts, views = [], [], []
        for seed in range(3):
            clip = make_clip(scenario, seed)
            t, v = count(clip, "track")
            l, _ = count(clip, "line")
            track_counts.append(t)
            line_counts.append(l)
            views.append(v)
        print(f"{scenario:<10} {truth[scenario]:>4} {sum(track_counts) / 3:>11.1f} "
              f"{sum(line_counts) / 3:>10.1f} {max(views):>12}")
