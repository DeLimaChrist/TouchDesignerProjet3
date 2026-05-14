# Hand Tracking Generative Visual

Move your fingers in front of your webcam and create real-time generative visuals. The visuals react to your finger position, pinch gestures, and hand spread.

## What this project does

This Python project uses:

- OpenCV for the webcam and visual effects
- MediaPipe for hand tracking
- NumPy for calculations and image processing

## Requirements

- Python 3.10 or newer
- A working webcam
- Camera permission enabled on your computer

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/DeLimaChrist/Project-TouchDesigner-.git
cd Project-TouchDesigner-
```

### 2. Create a virtual environment

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the project

```bash
python hand_visual.py
```

## Controls

| Key | Action |
| --- | --- |
| `1` | Ripple Rings |
| `2` | Flow Field |
| `3` | Sacred Geometry |
| `4` | Particle Burst |
| `5` | Warp Web |
| `S` | Save screenshot as PNG |
| `Q` or `ESC` | Quit |

## Gesture Reference

- Pinch your index finger and thumb to change the effect density.
- Spread your fingers wide to increase size and intensity.
- Move your hand left or right to shift the color.
- Move your hand up or down to change the visual movement.
- Use two hands for stronger effects in some modes.

## Troubleshooting

### The webcam does not open

Open `hand_visual.py` and change:

```python
WEBCAM_INDEX = 0
```

to:

```python
WEBCAM_INDEX = 1
```

Then run the file again.

### Hand tracking is not working well

Use brighter lighting and place your hand in front of a plain background.

### MediaPipe installation fails

Try upgrading pip first:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## TouchDesigner Note

This repository currently runs as a Python/OpenCV hand-tracking visual project. To make it a true TouchDesigner project, add a `.toe` or `.tox` file created inside TouchDesigner.
