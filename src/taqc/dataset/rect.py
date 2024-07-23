from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Iterable,
    NamedTuple,
    Protocol,
    Sequence,
)

from expression import Nothing, Option, Some, effect
from expression.collections import Block

from .common import CropBox, Point, Size, clamp, convert_coords, rndWinPos


class TFTensor(Iterable[float], Protocol):
    def item(self) -> float: ...

    def tolist(self) -> list[float]: ...

    def __getitem__(self, any) -> "TFTensor": ...


class Rect(NamedTuple):
    lt: Point
    rb: Point

    @property
    def rt(self) -> Point:
        return Point(self.rb.x, self.lt.y)

    @property
    def lb(self) -> Point:
        return Point(self.lt.x, self.rb.y)

    @property
    def size(self) -> Size:
        return Size(self.rb.x - self.lt.x, self.rb.y - self.lt.y)

    @property
    def center(self) -> tuple[float, float]:
        return (self.lt.x + self.rb.x) / 2, (self.lt.y + self.rb.y) / 2

    def toTuple(self):
        return *self.lt, *self.rb

    def contain(self, point: Point):
        return (self.lt.x <= point.x <= self.rb.x) and (
            self.lt.y <= point.y <= self.rb.y
        )

    def overlaps(self, rhs: "Rect"):
        return self.distance(rhs) <= 0

    def adjustToBoundaries(self, size) -> Option["Rect"]:
        MIN_SIZE = 2

        if not self.overlaps(Rect.fromSize(Point(0, 0), size)):
            return Nothing

        newRect = Rect(
            Point(
                max(0, self.lt.x),
                max(0, self.lt.y),
            ),
            Point(min(self.rb.x, size.width), min(self.rb.y, size.height)),
        )
        newSize = newRect.size
        if newSize.width <= MIN_SIZE or newSize.height <= MIN_SIZE:
            return Nothing

        return Some(newRect)

    def toCocoBounds(self) -> tuple[int, int, int, int]:
        return self.lt.x, self.lt.y, self.size.width, self.size.height

    def toPostgresBox(self, image_size: Size):
        width, height = image_size
        return (
            f"({clamp(self.lt.x / width)}, {clamp(self.lt.y / height)}),"
            + f"({clamp(self.rb.x / width)}, {clamp(self.rb.y / height)})"
        )

    def distance(self, other: "Rect") -> int:
        x1, y1 = self.center
        w1, h1 = self.size
        x2, y2 = other.center
        w2, h2 = other.size

        return int(
            max(
                abs(x1 - x2) - (w1 + w2) / 2,
                abs(y1 - y2) - (h1 + h2) / 2,
            )
        )

    def __or__(self, other: "Rect") -> "Rect":
        return Rect(
            Point(min(self.lt.x, other.lt.x), min(self.lt.y, other.lt.y)),
            Point(max(self.rb.x, other.rb.x), max(self.rb.y, other.rb.y)),
        )

    def __add__(self, point: Point) -> "Rect":
        return Rect(lt=self.lt + point, rb=self.rb + point)

    def __sub__(self, point: Point) -> "Rect":
        return Rect(lt=self.lt - point, rb=self.rb - point)

    @staticmethod
    def parseRelative(string: str, imageSize: tuple[int, int]) -> Option["Rect"]:
        parts = string.split(" ")
        match parts:
            case [_, _, _, _, _]:
                x, y, w, h = convert_coords(parts, imageSize)
                return Some(Rect(lt=Point(x, y), rb=Point(x + w, y + h)))
            case _:
                return Nothing

    @staticmethod
    def fromSize(lt: Point, size: Size) -> "Rect":
        return Rect(lt, Point(lt.x + size.width, lt.y + size.height))

    @staticmethod
    def invariant(p1: Point, p2: Point):
        return Rect(
            Point(min(p1.x, p2.x), min(p1.y, p2.y)),
            Point(max(p1.x, p2.x), max(p1.y, p2.y)),
        )

    @staticmethod
    def fromCoco(bounds: Sequence[int]):
        w: int = bounds[2]
        h: int = bounds[3]
        x: int = bounds[0] - w // 2
        y: int = bounds[1] - h // 2

        return Rect.invariant(Point(x, y), Point(x + w, y + h))

    @staticmethod
    def fromTfTensor(tfTensor: TFTensor) -> "Rect":
        coords = tuple(int(x) for x in tfTensor[:4])
        return Rect(
            Point(*coords[:2]),
            Point(*coords[2:]),
        )


@dataclass(frozen=True)
class Object:
    box: Rect
    category: int

    def updateRect(self, updater: Callable[[Rect], Rect]) -> "Object":
        return Object(updater(self.box), self.category)

    def merge(self, other: "Object", tolerance=2) -> Option["Object"]:
        if self.category != other.category or self.box.distance(other.box) > tolerance:
            return Nothing

        return Some(Object(self.box | other.box, self.category))

    @staticmethod
    @effect.option()
    def parse(string: str, imageSize: tuple[int, int]):
        category = yield from Block(string.split(" ")).try_head()
        rect = yield from Rect.parseRelative(string, imageSize)

        return Object(rect, int(category))

    def toJson(
        self,
        image_size: Size,
        categories: Sequence[str] = ("defect", "hole", "misc", "stripe"),
    ):
        return {
            "category": categories[self.category],
            "box": self.box.toPostgresBox(image_size),
        }


@effect.option[CropBox]()  # type: ignore
def rndCropIncludingRect(imageSize: Size, rect: Rect, winSize: Size):
    x = yield from rndWinPos(imageSize.width, rect.lt.x, rect.size.width, winSize.width)
    y = yield from rndWinPos(
        imageSize.height, rect.lt.y, rect.size.height, winSize.height
    )
    return x, y, x + winSize.width, y + winSize.height


def objects_from_ann(ann: Any):
    return tuple(
        Object(category=category, box=Rect.fromSize(
            Point(*box[:2]), Size(*box[2:])))
        for box, category in zip(ann["objects"]["bbox"], ann["objects"]["category"])
    )
