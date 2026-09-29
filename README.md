# Trash Detector (YOLOv10 + DeepSORT)

Counts visible litter in a camera feed or recorded video. Each frame goes through a YOLOv10 detector, a DeepSORT tracker gives every object an ID, and each confirmed ID is counted once. A small FastAPI server exposes the count, and a React page shows it live.

> **Status: v0.3, working prototype.** Detection accuracy has only been measured on the TACO validation split (see Results). It has not yet been tested on field data or compared with hand counts, and there is no map yet. See Roadmap.

## How it works

```
camera / video file
      │
      ▼
YOLOv10 detector  ──►  DeepSORT tracker  ──►  count each confirmed track once
                                                   │
                         detections.jsonl  ◄───────┤
                         FastAPI /trash-count ◄────┤
                         WhatsApp alert (optional) ◄┘
```

## Results so far

Metrics read from the saved checkpoints. These are **validation-split** numbers from training, so they are optimistic; no held-out test set has been scored yet.

| Model file | Base | Training data | Classes | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|---|
| `models/best_one_class.pt` (default) | YOLOv10n, 50 epochs | TACO (Roboflow export) | 1: trash | 0.56 | 0.42 | 0.41 | 0.25 |
| `models/best_4000_img_train3.pt` | YOLOv10s, 132 epochs | TACO (Roboflow export) | 18 TACO classes | 0.70 | 0.42 | 0.46 | 0.35 |

What this means: at the default setting the model finds roughly 4 in 10 labeled items. Counts from this system are therefore **lower bounds**.

## Quick start

You need **Git** and **Python 3.10 to 3.12**. Python 3.13 or newer will not work: PyTorch 2.5.1, which the model files need, has no builds for it. The first install downloads about 1 GB and takes 3 to 5 minutes.

**macOS**

```bash
brew install python@3.12
git clone https://github.com/trash-detector-project/trash-detector.git
cd trash-detector
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

The first time, macOS blocks the camera. Allow Terminal in System Settings, Privacy & Security, Camera, then quit Terminal (Cmd+Q), reopen it, `cd` back into the folder, run `source venv/bin/activate`, and run `python main.py` again.

**Windows (PowerShell).** Install Python 3.12 from [python.org](https://www.python.org/downloads/) and tick "Add python.exe to PATH". Then:

```powershell
git clone https://github.com/trash-detector-project/trash-detector.git
cd trash-detector
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

**Linux.** Same as macOS, using your package manager for Python 3.12.

A window opens showing the camera with a box around anything the model thinks is litter, plus two numbers: how many items are in view and how many have been counted. Press Esc to quit. Windows and Linux setups have not been tested yet; please open an issue if something breaks.

The model files were trained with the [THU-MIG YOLOv10 fork](https://github.com/THU-MIG/yolov10), which `requirements.txt` installs.

## Run it live

```bash
python main.py
```

- The video window is on by default (press Esc to quit). Set `SHOW_WINDOW=false` in `.env` on a device with no screen.
- `CAMERA_SOURCE=0` is the first webcam; set it to a file path or stream URL to run on video.
- On macOS, allow the camera for Terminal (System Settings, Privacy & Security, Camera), then quit and reopen Terminal.
- API: `GET /trash-count` (returns `in_view` and `total`), `GET /status`, `GET /health`, WebSocket `/ws/trash-count`.
- Every counted item is appended to `detections.jsonl` (time, track ID, class, confidence, box).

Dashboard:

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

## Counting modes

The window shows two numbers. **In view** is how many pieces of litter are visible right now. **Counted** is the running total, and how it is counted depends on `COUNT_MODE` in `.env`:

| Mode | Use it for | How it counts |
|---|---|---|
| `track` (default) | A fixed camera watching one spot | Each tracked object counts once, when the tracker confirms it |
| `line` | A walking survey (street, beach, park path) | An object counts when its center crosses the orange line in `LINE_DIRECTION` |

Why two modes: the tracker forgets an object after about 30 frames out of view. With a moving camera, panning back to litter you already passed gives it a new ID, so `track` mode counts it again. In `line` mode, walk forward with the camera pointed ahead and down; litter moves down the frame and crosses the line once. Panning sideways moves litter across the frame, not over the line.

`LINE_POSITION` sets the line height as a fraction of the frame (`0.8` is near the bottom). `LINE_DIRECTION` is `down` for walking forward, `up` for walking backward, or `any`.

Synthetic test results (`python tests/test_counting_modes.py`, 3 clips per scenario, boxes fed straight to the tracker):

| Scenario | True count | `track` mode | `line` mode |
|---|---|---|---|
| Fixed camera, 3 items | 3 | 3.0 | 0.0 (nothing crosses the line; use `track` here) |
| Walking forward, 5 items | 5 | 5.0 | 5.0 |
| Walking forward while sweeping the camera side to side | 5 | 11.7 | 4.0 |

`line` mode can miss an item if the camera is pointed away at the moment that item passes the line. Keep the camera steady and pointed ahead while surveying.

## Measure counting accuracy

Record short clips, have two people agree on the number of unique items in each, and put them in `hand_counts.csv`:

```
clip,count
clip01.mp4,7
clip02.mp4,3
```

Then:

```bash
python count_video.py clips/*.mp4 --hand-counts hand_counts.csv
python count_video.py clips/*.mp4 --hand-counts hand_counts.csv --mode line   # walking-survey clips
```

It prints mean absolute error and percent error and writes `results/count_eval.csv`.

## Known limitations

- Trained only on TACO, which is mostly close-up photos of litter on the ground. Expect lower accuracy on other viewpoints (fixed cameras, water, drones).
- The confidence threshold (0.25) is the training default, not yet tuned on a precision-recall curve.
- No location data yet, so no map.
- The pH endpoint accepts readings from a real sensor; no sensor is connected, and the code does not generate pH values.

## Roadmap

1. Pick the deployment setting and write the one-sentence claim.
2. Retrain with splits made before augmentation, plus a held-out test set.
3. Collect and label 300 to 500 images from the real setting; report field accuracy.
4. Measure counting error on 10 to 20 hand-counted clips.
5. Add GPS to each detection and build a normalized heatmap (items per 100 m surveyed).
6. Partner with a cleanup group and measure before/after.

## Changelog

**v0.3**
- Added an "in view" count (litter visible right now) to the window, the API and the dashboard.
- Added `line` counting mode for walking surveys, with `LINE_POSITION` and `LINE_DIRECTION` settings.
- Added `tests/test_counting_modes.py`.
- `/` now returns a short index instead of a 404.
- Added a Quick start with clone and setup steps for macOS, Windows and Linux.
- The video window is now on by default.

**v0.2**
- Fixed: tracker received `x1,y1,x2,y2` boxes where DeepSORT expects `left,top,width,height`.
- Fixed: tentative (unconfirmed) tracks were counted.
- Fixed: total count reset to 0 after every alert.
- Fixed: alert threshold had two different defaults (1 and 5).
- Removed: randomly generated pH values that were logged as sensor readings.
- Removed: unused Canny edge detection.
- Alerts and S3 uploads now run off the video thread; windows are optional; camera loss stops cleanly.
- Added `count_video.py` for count-error evaluation, `detections.jsonl` event log, `.env.example`, pinned requirements.

## License

The YOLOv10 code and the weights derived from it are AGPL-3.0. This repository is distributed under AGPL-3.0 as well; see `LICENSE`.

## Credits

- **Maintained by** Aravind Srinivasan and Naren Ranjith, under the [trash-detector-project](https://github.com/trash-detector-project) organization.
- **Original code** by Sreeraman Sreebalaji, November 2024: [Ramennn1232007/trash_detector_model_YOLO](https://github.com/Ramennn1232007/trash_detector_model_YOLO). This repository continues that project with its full commit history.
- **Dataset:** [TACO](http://tacodataset.org) (Proença and Simões, 2020).
- **Detection model:** [YOLOv10](https://github.com/THU-MIG/yolov10) (THU-MIG). **Tracker:** [deep_sort_realtime](https://github.com/levan92/deep_sort_realtime).
