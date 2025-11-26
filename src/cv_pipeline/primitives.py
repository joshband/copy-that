"""Primitive shape detection helpers using OpenCV."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray


@dataclass(slots=True)
class Circle:
    center: tuple[int, int]
    radius: int


@dataclass(slots=True)
class Rectangle:
    x: int
    y: int
    width: int
    height: int


@dataclass(slots=True)
class Line:
    start: tuple[int, int]
    end: tuple[int, int]


def detect_circles(gray: NDArray[np.uint8]) -> list[Circle]:
    blurred = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=0,
    )
    results: list[Circle] = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for x, y, r in circles:
            results.append(Circle(center=(int(x), int(y)), radius=int(r)))
    return results


def detect_rectangles(gray: NDArray[np.uint8]) -> list[Rectangle]:
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rectangles: list[Rectangle] = []
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > 100:
            x, y, w, h = cv2.boundingRect(approx)
            rectangles.append(Rectangle(x=x, y=y, width=w, height=h))
    return rectangles


def detect_lines(gray: NDArray[np.uint8]) -> list[Line]:
    edges = cv2.Canny(gray, 50, 150)
    segments = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)
    lines: list[Line] = []
    if segments is not None:
        for x1, y1, x2, y2 in segments[:, 0]:
            lines.append(Line(start=(int(x1), int(y1)), end=(int(x2), int(y2))))
    return lines
