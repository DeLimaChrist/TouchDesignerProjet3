"""
Hand Tracking Generative Visual
===============================
Move your fingers in front of your webcam — no touching needed.

Controls:
    1 = Ripple Rings
    2 = Flow Field
    3 = Sacred Geometry
    4 = Particle Burst
    5 = Warp Web
    S = Save screenshot
    Q or ESC = Quit
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import cv2
import mediapipe as mp
import numpy as np


# =========================
# Config
# =========================
WIDTH = 1280
HEIGHT = 720
WEBCAM_INDEX = 0
TRAIL_DECAY = 0.88  # 0 = no trails, 1 = infinite trails
SHOW_SKELETON = True
SCREENSHOT_DIR = Path("screenshots")


Point = Tuple[int, int]
Color = Tuple[int, int, int]


@dataclass
class HandData:
    landmarks: List[Point]
    thumb_tip: Point
    index_tip: Point
    middle_tip: Point
    ring_tip: Point
    pinky_tip: Point
    palm: Point
    pinch_distance: float
    spread: float


class Particle:
    def __init__(self, x: int, y: int, color: Color) -> None:
        self.x = float(x)
        self.y = float(y)
        angle = np.random.uniform(0, math.tau)
        speed = np.random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = np.random.randint(25, 70)
        self.color = color
        self.radius = np.random.randint(2, 6)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= 1

    def draw(self, frame: np.ndarray) -> None:
        if self.life <= 0:
            return
        alpha = max(0, min(1, self.life / 70))
        radius = max(1, int(self.radius * alpha))
        color = tuple(int(c * alpha) for c in self.color)
        cv2.circle(frame, (int(self.x), int(self.y)), radius, color, -1)


particles: List[Particle] = []


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def hue_color(value: float) -> Color:
    """Create a bright BGR color from a 0-1 value."""
    hue = int((value % 1.0) * 179)
    hsv = np.uint8([[[hue, 255, 255]]])
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
    return int(bgr[0]), int(bgr[1]), int(bgr[2])


def distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def extract_hand_data(results) -> List[HandData]:
    hands: List[HandData] = []
    if not results.multi_hand_landmarks:
        return hands

    for hand_landmarks in results.multi_hand_landmarks:
        points: List[Point] = []
        for lm in hand_landmarks.landmark:
            x = int(lm.x * WIDTH)
            y = int(lm.y * HEIGHT)
            points.append((x, y))

        thumb_tip = points[4]
        index_tip = points[8]
        middle_tip = points[12]
        ring_tip = points[16]
        pinky_tip = points[20]
        palm = points[0]

        pinch_distance = distance(thumb_tip, index_tip)
        spread = distance(index_tip, pinky_tip)

        hands.append(
            HandData(
                landmarks=points,
                thumb_tip=thumb_tip,
                index_tip=index_tip,
                middle_tip=middle_tip,
                ring_tip=ring_tip,
                pinky_tip=pinky_tip,
                palm=palm,
                pinch_distance=pinch_distance,
                spread=spread,
            )
        )
    return hands


def draw_ripple_rings(canvas: np.ndarray, hand: HandData, frame_count: int) -> None:
    x, y = hand.index_tip
    color = hue_color(x / WIDTH)
    base = int(max(20, min(180, hand.spread)))
    spacing = max(14, int(hand.pinch_distance / 3))

    for i in range(8):
        radius = (frame_count * 4 + i * spacing) % (base + 180)
        thickness = 2 + (i % 3)
        cv2.circle(canvas, (x, y), int(radius), color, thickness)


def draw_flow_field(canvas: np.ndarray, hand: HandData, frame_count: int) -> None:
    cx, cy = hand.palm
    color = hue_color((cx + frame_count * 2) / WIDTH)
    intensity = max(20, min(120, hand.spread))

    for i in range(80):
        angle = i * 0.33 + frame_count * 0.04
        radius = (i * 6 + frame_count * 2) % int(intensity + 160)
        x1 = int(cx + math.cos(angle) * radius)
        y1 = int(cy + math.sin(angle) * radius)
        x2 = int(cx + math.cos(angle + 0.8) * (radius + 18))
        y2 = int(cy + math.sin(angle + 0.8) * (radius + 18))
        cv2.line(canvas, (x1, y1), (x2, y2), color, 1)


def draw_sacred_geometry(canvas: np.ndarray, hand: HandData, frame_count: int) -> None:
    cx, cy = hand.index_tip
    color = hue_color((cy + frame_count) / HEIGHT)
    sides = 6
    radius = int(max(40, min(180, hand.spread)))
    rotation = frame_count * 0.03 + hand.pinch_distance * 0.01

    points = []
    for i in range(sides):
        angle = rotation + i * math.tau / sides
        points.append((int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius)))

    for i in range(len(points)):
        cv2.line(canvas, points[i], points[(i + 1) % len(points)], color, 2)
        cv2.line(canvas, (cx, cy), points[i], color, 1)

    cv2.circle(canvas, (cx, cy), radius // 2, color, 1)
    cv2.circle(canvas, (cx, cy), radius, color, 2)


def draw_particle_burst(canvas: np.ndarray, hand: HandData) -> None:
    fingertips = [hand.thumb_tip, hand.index_tip, hand.middle_tip, hand.ring_tip, hand.pinky_tip]
    color = hue_color(hand.palm[0] / WIDTH)

    if len(particles) < 500:
        for tip in fingertips:
            for _ in range(2):
                particles.append(Particle(tip[0], tip[1], color))

    for particle in particles[:]:
        particle.update()
        particle.draw(canvas)
        if particle.life <= 0:
            particles.remove(particle)


def draw_warp_web(canvas: np.ndarray, hand: HandData, frame_count: int) -> None:
    color = hue_color((hand.palm[0] + frame_count * 3) / WIDTH)
    landmarks = hand.landmarks

    connections = mp_hands.HAND_CONNECTIONS
    for start, end in connections:
        cv2.line(canvas, landmarks[start], landmarks[end], color, 2)

    for i, point in enumerate(landmarks):
        radius = 3 + int((math.sin(frame_count * 0.1 + i) + 1) * 3)
        cv2.circle(canvas, point, radius, color, -1)

    for i in range(0, len(landmarks), 3):
        for j in range(i + 3, len(landmarks), 5):
            if distance(landmarks[i], landmarks[j]) < 180:
                cv2.line(canvas, landmarks[i], landmarks[j], color, 1)


def draw_ui(frame: np.ndarray, mode: int, hands_count: int) -> None:
    labels = {
        1: "Ripple Rings",
        2: "Flow Field",
        3: "Sacred Geometry",
        4: "Particle Burst",
        5: "Warp Web",
    }
    text = f"Mode {mode}: {labels[mode]} | Hands: {hands_count} | 1-5 switch | S screenshot | Q quit"
    cv2.rectangle(frame, (0, 0), (WIDTH, 46), (0, 0, 0), -1)
    cv2.putText(frame, text, (18, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)


def save_screenshot(frame: np.ndarray) -> None:
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    filename = SCREENSHOT_DIR / f"hand_visual_{int(time.time())}.png"
    cv2.imwrite(str(filename), frame)
    print(f"Saved screenshot: {filename}")


def main() -> None:
    cap = cv2.VideoCapture(WEBCAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permission or try WEBCAM_INDEX = 1.")

    mode = 1
    frame_count = 0
    trail = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.60,
        min_tracking_confidence=0.60,
    ) as hands_detector:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Could not read webcam frame.")
                break

            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands_detector.process(rgb)
            hand_data = extract_hand_data(results)

            trail = (trail * TRAIL_DECAY).astype(np.uint8)
            canvas = trail.copy()

            for hand in hand_data:
                if mode == 1:
                    draw_ripple_rings(canvas, hand, frame_count)
                elif mode == 2:
                    draw_flow_field(canvas, hand, frame_count)
                elif mode == 3:
                    draw_sacred_geometry(canvas, hand, frame_count)
                elif mode == 4:
                    draw_particle_burst(canvas, hand)
                elif mode == 5:
                    draw_warp_web(canvas, hand, frame_count)

            trail = canvas.copy()
            output = cv2.addWeighted(frame, 0.35, canvas, 0.95, 0)

            if SHOW_SKELETON and results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(output, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            draw_ui(output, mode, len(hand_data))
            cv2.imshow("Hand Tracking Generative Visual", output)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in [ord(str(i)) for i in range(1, 6)]:
                mode = int(chr(key))
            if key == ord("s"):
                save_screenshot(output)

            frame_count += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
