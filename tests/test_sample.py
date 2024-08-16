from PIL import Image
from expression.collections import Block

from taqc.dataset import Rect, Point, Sample
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

    def test_real(self):
        sample = createSampleFromRects(
            Rect.invariant(Point(x=2633, y=1146), Point(x=2405, y=913)),
            Rect.invariant(Point(x=2632, y=1149), Point(x=2406, y=915)),
            Rect.invariant(Point(x=2631, y=1143), Point(x=2407, y=914)),
        )

        assert sample.dedupe().objects == Block(
            [Object(Rect(Point(2405, 913), Point(2633, 1149)), 0)]
        )


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


def test_from_internal():
    json = [{"box": [0, 0, 2, 2], "category": 0}, {"box": [1, 1, 3, 3], "category": 1}]
    sample = Sample.fromInternalJson(json)
    assert sample.objects[0] == Object(Rect(Point(0, 0), Point(2, 2)), 0)
    assert sample.objects[1] == Object(Rect(Point(1, 1), Point(3, 3)), 1)
