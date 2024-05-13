from taqc.dataset import Rect, Point, Size


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


def test_db():
    rect = Rect(Point(1, 1), Point(2, 2))
    assert rect.toPostgresBox(Size(10, 10)).replace(" ", "") == "(0.1,0.1),(0.2,0.2)"

def test_db_clamp():
    rect = Rect(Point(1, 1), Point(5, 5))
    assert rect.toPostgresBox(Size(4, 4)).replace(" ", "") == "(0.25,0.25),(1,1)"


def test_distance():
    rect1 = Rect(Point(1, 1), Point(4, 4))
    rect2 = Rect(Point(5, 3), Point(7, 4))

    assert rect1.distance(rect2) == 1
