import numpy as np

from cv_pipeline import primitives


def test_detect_circles_on_synthetic_image() -> None:
    image = np.zeros((200, 200), dtype=np.uint8)
    cv2 = __import__("cv2")
    cv2.circle(image, (100, 100), 40, 255, -1)

    circles = primitives.detect_circles(image)

    assert circles
    assert circles[0].radius > 30


def test_detect_rectangles_on_synthetic_image() -> None:
    image = np.zeros((200, 200), dtype=np.uint8)
    cv2 = __import__("cv2")
    cv2.rectangle(image, (50, 50), (150, 150), 255, -1)

    rectangles = primitives.detect_rectangles(image)

    assert rectangles
    assert rectangles[0].width >= 90


def test_detect_lines_on_synthetic_image() -> None:
    image = np.zeros((200, 200), dtype=np.uint8)
    cv2 = __import__("cv2")
    cv2.line(image, (10, 10), (190, 10), 255, 2)

    lines = primitives.detect_lines(image)

    assert lines
    assert abs(lines[0].start[1] - 10) <= 2
    assert abs(lines[0].end[1] - 10) <= 2
