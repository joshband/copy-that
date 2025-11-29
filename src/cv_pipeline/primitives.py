"""Primitive shape detection helpers using OpenCV."""

from __future__ import annotations

from collections.abc import Iterable
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


def bounding_boxes_from_contours(
    gray: NDArray[np.uint8],
    *,
    canny_threshold1: int = 50,
    canny_threshold2: int = 150,
    min_area: int = 16,
) -> list[tuple[int, int, int, int]]:
    """
    Extract axis-aligned bounding boxes from contours on a grayscale image.

    Returns a list of (x, y, w, h) tuples.
    """
    edges = cv2.Canny(gray, canny_threshold1, canny_threshold2)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes: list[tuple[int, int, int, int]] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h >= min_area:
            boxes.append((int(x), int(y), int(w), int(h)))
    return boxes


def measure_spacing_gaps(
    bboxes: Iterable[tuple[int, int, int, int]],
    *,
    min_gap: int = 2,
    max_gap: int = 200,
) -> tuple[list[int], list[int]]:
    """
    Compute horizontal and vertical gaps between sorted bounding boxes.

    Returns (x_gaps, y_gaps) in pixels.
    """
    x_gaps: list[int] = []
    y_gaps: list[int] = []
    sorted_x = sorted(bboxes, key=lambda b: b[0])
    sorted_y = sorted(bboxes, key=lambda b: b[1])

    for i in range(len(sorted_x) - 1):
        _, _, w1, _ = sorted_x[i]
        x1 = sorted_x[i][0] + w1
        x2 = sorted_x[i + 1][0]
        gap = x2 - x1
        if min_gap <= gap <= max_gap:
            x_gaps.append(gap)

    for i in range(len(sorted_y) - 1):
        _, _, _, h1 = sorted_y[i]
        y1 = sorted_y[i][1] + h1
        y2 = sorted_y[i + 1][1]
        gap = y2 - y1
        if min_gap <= gap <= max_gap:
            y_gaps.append(gap)

    return x_gaps, y_gaps


def components_to_bboxes(
    gray: NDArray[np.uint8],
    *,
    min_area: int = 64,
    open_iterations: int = 1,
    close_iterations: int = 2,
) -> list[tuple[int, int, int, int]]:
    """Detect connected components with morphology + contours.

    Returns a list of bounding boxes (x, y, w, h) sorted by row/column.
    """

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    mean_intensity = float(np.mean(blurred.astype(np.float32)))
    thresh_type = cv2.THRESH_BINARY_INV if mean_intensity > 127 else cv2.THRESH_BINARY
    _, binary = cv2.threshold(blurred, 0, 255, thresh_type + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=open_iterations)
    processed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=close_iterations)

    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bboxes: list[tuple[int, int, int, int]] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h >= min_area:
            bboxes.append((int(x), int(y), int(w), int(h)))

    return sorted(bboxes, key=lambda box: (box[1], box[0]))


def gaps_from_bboxes(
    bboxes: Iterable[tuple[int, int, int, int]],
    *,
    axis_tolerance: int = 2,
    min_overlap_ratio: float = 0.3,
) -> tuple[list[int], list[int]]:
    """Compute horizontal and vertical gaps between neighboring boxes."""

    boxes = list(bboxes)
    if len(boxes) < 2:
        return [], []

    def _overlap(start1: int, end1: int, start2: int, end2: int) -> int:
        return min(end1, end2) - max(start1, start2)

    def _dedupe(values: list[int]) -> list[int]:
        if not values:
            return []
        values.sort()
        merged = [values[0]]
        for gap in values[1:]:
            if abs(gap - merged[-1]) <= axis_tolerance:
                merged[-1] = int(round((merged[-1] + gap) / 2))
            else:
                merged.append(gap)
        return merged

    horizontal: list[int] = []
    vertical: list[int] = []

    sorted_x = sorted(boxes, key=lambda b: b[0])
    for idx, a in enumerate(sorted_x):
        ax1, ay1, aw, ah = a
        ax2 = ax1 + aw
        ay2 = ay1 + ah
        for b in sorted_x[idx + 1 :]:
            bx1, by1, bw, bh = b
            bx2 = bx1 + bw
            by2 = by1 + bh
            overlap = _overlap(ay1, ay2, by1, by2)
            min_height = min(ah, bh)
            if min_height <= 0:
                continue
            if overlap / min_height < min_overlap_ratio:
                continue
            gap = bx1 - ax2
            if gap > 0:
                horizontal.append(gap)
                break

    sorted_y = sorted(boxes, key=lambda b: b[1])
    for idx, a in enumerate(sorted_y):
        ax1, ay1, aw, ah = a
        ax2 = ax1 + aw
        ay2 = ay1 + ah
        for b in sorted_y[idx + 1 :]:
            bx1, by1, bw, bh = b
            bx2 = bx1 + bw
            by2 = by1 + bh
            overlap = _overlap(ax1, ax2, bx1, bx2)
            min_width = min(aw, bw)
            if min_width <= 0:
                continue
            if overlap / min_width < min_overlap_ratio:
                continue
            gap = by1 - ay2
            if gap > 0:
                vertical.append(gap)
                break

    return _dedupe(horizontal), _dedupe(vertical)
