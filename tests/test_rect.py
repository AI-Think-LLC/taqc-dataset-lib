import pytest
from taqc.dataset import Rect, Point


def test_union():
    rect1 = Rect(Point(1, 1), Point(4, 4))
    rect2 = Rect(Point(2, 2), Point(4, 3))

    assert (rect1 | rect2) == Rect(Point(1, 1), Point(4, 4))
