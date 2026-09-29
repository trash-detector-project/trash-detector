# Trash Detector

Point a camera at an area and this program draws a box around each piece of litter it sees, follows each piece from frame to frame, and counts it once. It runs on a normal laptop with a webcam.

> **Status: v0.3, working prototype.** The model finds about 4 in 10 pieces of litter (see [Results so far](#results-so-far)), so treat every count as a minimum. It has not been tested in the field yet, and there is no map yet.

## Contents

- [Run it on a Mac](#run-it-on-a-mac)
- [Run it on Windows](#run-it-on-windows)
- [Running it again later](#running-it-again-later)
- [Try walking-survey mode](#try-walking-survey-mode)
- [If something goes wrong](#if-something-goes-wrong)
- [How it works](#how-it-works) and everything technical after it

---

## Run it on a Mac

Do these in order. Each step says what you should see. The whole thing takes about 15 minutes the first time, mostly waiting for downloads.

### Step 1. Open Terminal

Press **Cmd + Space**, type `Terminal`, and press **Enter**. A window with a text prompt opens. You type every command below into this window and press **Enter** after each one.

### Step 2. Check that Homebrew is installed

```bash
brew --version
```

**You should see:** `Homebrew 4.x.x` or similar.
**If you see `command not found: brew`:** go to [brew.sh](https://brew.sh), copy the install command on that page, paste it into Terminal, and follow what it prints. Then run `brew --version` again.

### Step 3. Install Python 3.12 and Git

```bash
brew install python@3.12 git
```

This takes a few minutes. When your prompt comes back, check it worked:

```bash
python3.12 --version
```

**You should see:** `Python 3.12.x`.
**Why 3.12:** the model files need PyTorch 2.5.1, which does not work on Python 3.13 or newer. Your Mac may already have a newer Python; that is fine, this installs 3.12 next to it.

### Step 4. Download the project to your Desktop

```bash
cd ~/Desktop
git clone https://github.com/trash-detector-project/trash-detector.git
```

**You should see:** a few lines ending in `done.`, and a new `trash-detector` folder on your Desktop.

### Step 5. Go into the project folder

```bash
cd trash-detector
```

**You should see:** your prompt now ends in `trash-detector %`.

### Step 6. Create a private Python environment for the project

```bash
python3.12 -m venv venv
```

**You should see:** nothing. No output means it worked.

### Step 7. Turn the environment on

```bash
source venv/bin/activate
```

**You should see:** `(venv)` at the start of your prompt. From here on, `python` means Python 3.12.

### Step 8. Install what the project needs

```bash
pip install -r requirements.txt
```

This downloads about 1 GB and takes 3 to 5 minutes.
**You should see:** the last lines start with `Successfully installed`. A few yellow warnings are fine. Red lines that say `ERROR` are not; see [If something goes wrong](#if-something-goes-wrong).

### Step 9. Create the settings file

```bash
cp .env.example .env
```

**You should see:** nothing.

### Step 10. Allow Terminal to use the camera

macOS blocks the camera for Terminal until you allow it. Do this once:

1. Open **System Settings** (Apple menu, top left).
2. Click **Privacy & Security**, then **Camera**.
3. Turn on **Terminal**. If Terminal is not listed yet, go on to Step 11; macOS will ask when the program starts, and you can come back here after.
4. Quit Terminal completely with **Cmd + Q** (closing the window is not enough), then reopen it and follow [Running it again later](#running-it-again-later).

### Step 11. Run it

```bash
python main.py
```

**You should see:** a window called **Trash detector** showing your camera. Hold up a bottle, can, or wrapper. A blue box with an ID number appears around it, and the top left shows **In view** (litter visible now) and **Counted** (total so far).

The window can open behind Terminal. If you do not see it, press **Cmd + Tab** and pick the Python icon.

### Step 12. Stop it

Click the camera window and press **Esc**. If that does not work, click Terminal and press **Ctrl + C**.

---

## Run it on Windows

Use **Command Prompt** for these steps, not PowerShell.

### Step 1. Install Git

Download it from [git-scm.com](https://git-scm.com/download/win) and run the installer. The default options are fine.

### Step 2. Install Python 3.12

Go to [python.org/downloads](https://www.python.org/downloads/), scroll to **Python 3.12.x**, and download the Windows installer. Do not use the newest version at the top of the page; it will not work with this project.

On the first installer screen, tick **Add python.exe to PATH**, then click **Install Now**.

### Step 3. Open Command Prompt

Press the **Windows key**, type `cmd`, and press **Enter**.

### Step 4. Download the project to your Desktop

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/trash-detector-project/trash-detector.git
```

**You should see:** a new `trash-detector` folder on your Desktop.

### Step 5. Go into the project folder

```bat
cd trash-detector
```

### Step 6. Create the environment

```bat
py -3.12 -m venv venv
```

**If you see `No suitable Python runtime found`:** Python 3.12 did not install. Redo Step 2.

### Step 7. Turn the environment on

```bat
venv\Scripts\activate
```

**You should see:** `(venv)` at the start of the line.

### Step 8. Install what the project needs

```bat
pip install -r requirements.txt
```

Takes 3 to 5 minutes. **You should see:** `Successfully installed` at the end.

### Step 9. Create the settings file

```bat
copy .env.example .env
```

### Step 10. Run it

```bat
python main.py
```

**You should see:** the **Trash detector** camera window. If Windows blocks the camera, open **Settings**, **Privacy & security**, **Camera**, and turn on **Let desktop apps access your camera**, then run `python main.py` again.

Press **Esc** in the camera window to stop.

The Windows steps have not been tested on a real Windows machine yet. If one fails, please [open an issue](https://github.com/trash-detector-project/trash-detector/issues) with a screenshot.

---

## Running it again later

You only install once. After that, every time you want to run it:

**Mac**

```bash
cd ~/Desktop/trash-detector
source venv/bin/activate
python main.py
```

**Windows**

```bat
cd %USERPROFILE%\Desktop\trash-detector
venv\Scripts\activate
python main.py
```

If you put the project somewhere other than the Desktop, change the first line to that folder.

---

## Try walking-survey mode

By default the program counts every new object it tracks. That works for a camera that stays still. If you walk around with the camera, it recounts litter every time you turn back toward it.

Walking-survey mode fixes that: an orange line appears near the bottom of the window, and an item only counts when it crosses that line as you walk forward.

1. Open the settings file. Mac: `open -e .env`. Windows: `notepad .env`.
2. Find the line `COUNT_MODE=track` and change it to `COUNT_MODE=line`.
3. Save and close the file.
4. Run `python main.py` again.
5. Walk forward slowly with the camera pointed ahead and slightly down. Keep it steady; swinging it side to side can make it miss items.

To go back, change the line to `COUNT_MODE=track`.

---

## If something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `command not found: python` | On a Mac, `python` only works after Step 7 | Run `source venv/bin/activate` first |
| `command not found: python3.12` | Python 3.12 is not installed | Run `brew install python@3.12` and wait for it to finish |
| `No matching distribution found for torch`, or errors installing `torch` | The environment was made with the wrong Python version | Delete the `venv` folder (`rm -rf venv` on Mac, `rmdir /s /q venv` on Windows) and redo Steps 6 to 8 |
| `not authorized to capture video` or `Could not open camera or video source: 0` | The camera is blocked for Terminal | Mac: do Step 10 of the Mac guide, including quitting Terminal with Cmd + Q |
| `can't open file 'main.py': No such file or directory` | Terminal is not inside the project folder. This also happens if the drive holding the project was unplugged | `cd` into the project folder again (see [Running it again later](#running-it-again-later)) |
| A long warning mentioning `weights_only` | PyTorch announcing a future change | Harmless, ignore it |
| No camera window appears | It opened behind other windows, or it is turned off | Press Cmd + Tab (Mac) or Alt + Tab (Windows) and look for Python. Check that `.env` has `SHOW_WINDOW=true` |
| The count keeps going up when you move the camera | The default mode recounts items you turn back to | Use [walking-survey mode](#try-walking-survey-mode) |
| It boxes things that are not trash | The model is not very accurate yet | Known limitation; see [Results so far](#results-so-far) |

Still stuck? [Open an issue](https://github.com/trash-detector-project/trash-detector/issues) with a screenshot of the error.

---

## How it works

```
camera / video file
      │
      ▼
YOLOv10 detector  ──►  DeepSORT tracker  ──►  count each item once
                                                   │
                         detections.jsonl  ◄───────┤
                         FastAPI /trash-count ◄────┤
                         WhatsApp alert (optional) ◄┘
```

Each frame goes through a YOLOv10 detector, a DeepSORT tracker gives every object an ID, and each object is counted once (see [Counting modes](#counting-modes)). A small FastAPI server exposes the counts, and a React page can show them live.

## Results so far

Metrics read from the saved checkpoints. These are **validation-split** numbers from training, so they are optimistic; no held-out test set has been scored yet.

| Model file | Base | Training data | Classes | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|---|
| `models/best_one_class.pt` (default) | YOLOv10n, 50 epochs | TACO (Roboflow export) | 1: trash | 0.56 | 0.42 | 0.41 | 0.25 |
| `models/best_4000_img_train3.pt` | YOLOv10s, 132 epochs | TACO (Roboflow export) | 18 TACO classes | 0.70 | 0.42 | 0.46 | 0.35 |

At the default setting the model finds roughly 4 in 10 labeled items, so counts from this system are **lower bounds**.

## Counting modes

**In view** is how many pieces of litter are visible right now. **Counted** is the running total, and how it is counted depends on `COUNT_MODE` in `.env`:

| Mode | Use it for | How it counts |
|---|---|---|
| `track` (default) | A fixed camera watching one spot | Each tracked object counts once, when the tracker confirms it |
| `line` | A walking survey (street, beach, park path) | An object counts when its center crosses the orange line in `LINE_DIRECTION` |

Why two modes: the tracker forgets an object after about 30 frames out of view. With a moving camera, turning back to litter you already passed gives it a new ID, so `track` mode counts it again. In `line` mode, litter moves down the frame as you walk forward and crosses the line once. Panning sideways moves litter across the frame, not over the line.

`LINE_POSITION` sets the line height as a fraction of the frame (`0.8` is near the bottom). `LINE_DIRECTION` is `down` for walking forward, `up` for walking backward, or `any`.

Synthetic test results (`python tests/test_counting_modes.py`, 3 clips per scenario, boxes fed straight to the tracker):

| Scenario | True count | `track` mode | `line` mode |
|---|---|---|---|
| Fixed camera, 3 items | 3 | 3.0 | 0.0 (nothing crosses the line; use `track` here) |
| Walking forward, 5 items | 5 | 5.0 | 5.0 |
| Walking forward while sweeping the camera side to side | 5 | 11.7 | 4.0 |

`line` mode can miss an item if the camera is pointed away at the moment that item passes the line.

## Settings and API

All settings live in `.env` (copied from `.env.example`):

- `SHOW_WINDOW=true` shows the camera window. Set it to `false` on a device with no screen.
- `CAMERA_SOURCE=0` is the first webcam. Use `1` for a second camera, or a file path or stream URL to run on video.
- `COUNT_MODE`, `LINE_POSITION`, `LINE_DIRECTION`: see [Counting modes](#counting-modes).
- `CONF_THRESHOLD=0.25`: how confident the model must be to draw a box. Higher means fewer false boxes and more missed litter.
- Twilio and S3 settings are optional, for WhatsApp alerts and cloud logs.

While it runs, a local API is available at `http://127.0.0.1:8000`: `GET /trash-count` (returns `in_view` and `total`), `GET /status`, `GET /health`, and WebSocket `/ws/trash-count`. Every counted item is appended to `detections.jsonl` with its time, track ID, class, confidence and box.

Optional web dashboard (needs [Node.js](https://nodejs.org)):

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

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

- Trained only on TACO, which is mostly close-up photos of litter on the ground. Expect lower accuracy from other viewpoints (fixed cameras, water, drones).
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
- Rewrote the setup instructions as step-by-step guides for Mac and Windows, with a troubleshooting table.
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
