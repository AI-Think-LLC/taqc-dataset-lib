from typing import Iterable
from taqc.dataset import Rect, Point, Sample
from PIL import Image
from expression.collections import Block

from taqc.dataset.rect import Object

EMPTY_IMAGE = Image.new("RGB", (0, 0))


def createSampleFromRects(*rects: Rect) -> Sample:
    return Sample(EMPTY_IMAGE, Block(rects).map(lambda rect: Object(rect, 0)))


class TestDedupe:
    def test_overlapping(self):
        rect1 = Rect(Point(0, 0), Point(5, 5))
        rect2 = Rect(Point(1, 1), Point(6, 6))

        sample = createSampleFromRects(rect1, rect2).dedupe()

        assert Block([Object(Rect(Point(0, 0), Point(6, 6)), 0)]) == sample.objects

    def test_intact(self):
        rect1 = Rect(Point(0, 0), Point(2, 2))
        rect2 = Rect(Point(5, 5), Point(6, 6))

        sample = createSampleFromRects(rect1, rect2)

        assert sample == sample.dedupe()

    def test_three_overlap(self):
        sample = createSampleFromRects(
            Rect(Point(0, 0), Point(3, 3)),
            Rect(Point(2, 2), Point(5, 5)),
            Rect(Point(4, 4), Point(6, 8)),
        ).dedupe()

        assert sample == createSampleFromRects(Rect(Point(0, 0), Point(6, 8)))


def test_count_false():
    trueObjects = Block(
        (
            Rect(Point(14, 6), Point(25, 17)),
            Rect(Point(45, 12), Point(61, 26)),
            Rect(Point(19, 57), Point(28, 67)),
        )
    ).map(lambda rect: Object(rect, 0))

    predict = createSampleFromRects(
        Rect(Point(9, 9), Point(20, 20)),
        Rect(Point(41, 9), Point(64, 29)),
        Rect(Point(51, 40), Point(66, 53)),
        Rect(Point(15, 31), Point(26, 40)),
    )

    assert predict.count_false(trueObjects) == (1, 2)
