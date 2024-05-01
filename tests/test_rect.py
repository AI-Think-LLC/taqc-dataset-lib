import pytest
from taqc.dataset import Rect, Point


def test_union():
    rect1 = Rect(Point(1, 1), Point(4, 4))
    rect2 = Rect(Point(2, 2), Point(4, 3))

    assert (rect1 | rect2) == Rect(Point(1, 1), Point(4, 4))


def test_add():
    rect = Rect(Point(1, 1), Point(4, 4))
    origin = Point(3, 3)
    assert (rect + origin) == Rect(Point(4, 4), Point(7, 7))


def test_sub():
    rect = Rect(Point(3, 3), Point(4, 4))
    origin = Point(3, 3)
    assert (rect - origin) == Rect(Point(0, 0), Point(1, 1))
