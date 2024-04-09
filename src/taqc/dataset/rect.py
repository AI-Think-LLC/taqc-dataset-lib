from typing import NamedTuple
from expression import Nothing, Option, Some
from expression.collections import Seq
from .common import Point, Size, convert_coords


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

    def toTuple(self):
        return (*self.lt, *self.rb)

    def contain(self, point: Point):
        return (self.lt.x <= point.x <= self.rb.x) and (
            self.lt.y <= point.y <= self.rb.y
        )

    def overlaps(self, rhs: "Rect"):
        def containAny(lhs: "Rect", other: "Rect"):
            return any(Seq.of(other.lt, other.rb, other.rt, other.lb).map(lhs.contain))

        return containAny(self, rhs) or containAny(rhs, self)

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
        return (self.lt.x, self.lt.y, self.size.width, self.size.height)

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
