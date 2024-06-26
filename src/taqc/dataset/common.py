from random import randint
import re
from typing import Literal, NamedTuple
from expression import Nothing, Option, Some, effect, option


class Size(NamedTuple):
    width: int
    height: int

    @property
    def area(self):
        return self.width * self.height


class ShotInfo(NamedTuple):
    side: Literal[0, 1]
    fabricType: str

    _filenamePattern = re.compile(r"^.*_c(\d)(?:_Ткань)?_(.*)\.jpg$")

    @staticmethod
    @effect.option["ShotInfo"]()
    def fromFilename(filename: str):
        m = yield from option.of_optional(ShotInfo._filenamePattern.match(filename))
        return ShotInfo(int(m.group(1)), m.group(2))  # type: ignore


class Point(NamedTuple):
    x: int
    y: int

    def __sub__(self, rhs: "Point") -> "Point":
        return Point(self.x - rhs.x, self.y - rhs.y)

    def __add__(self, rhs: "Point") -> "Point":
        return Point(self.x + rhs.x, self.y + rhs.y)


def convert_coords(coords, img_size):
    _, x_center, y_center, w_norm, h_norm = map(float, coords)
    w_abs = w_norm * img_size[0]
    h_abs = h_norm * img_size[1]
    x_abs = (x_center * img_size[0]) - (w_abs / 2)
    y_abs = (y_center * img_size[1]) - (h_abs / 2)
    return int(x_abs), int(y_abs), int(w_abs), int(h_abs)


CropBox = tuple[int, int, int, int]


def clamp(x: float, minimum: float = 0, maximum: float = 1) -> float:
    if x < minimum:
        return minimum
    elif x > maximum:
        return maximum
    else:
        return x


def getCropBox(shot: ShotInfo) -> Option[CropBox]:
    match shot:
        case (0, "подкладочная_таффета_белый"):
            return Some((783, 221, 2303, 1197))
        case (1, "подкладочная_таффета_белый"):
            return Some((0, 372, 1260, 1294))
        case (0, "трикотаж_жаккард_TRELAX_tencel"):
            return Some((307, 244, 2303, 1197))
        case (1, "трикотаж_жаккард_TRELAX_tencel"):
            return Some((0, 372, 1862, 1294))
        case (0, "Костюмка_Лиза"):
            return Some((644, 244, 2303, 1197))
        case (1, "Костюмка_Лиза"):
            return Some((0, 396, 1045, 1293))
        case (0, "чулок_рибана"):
            return Some((504, 296, 2303, 1250))
        case (1, "чулок_рибана"):
            return Some((0, 388, 1465, 1293))
        case (0, "автовелюр_серый"):
            return Some((675, 271, 2303, 1230))
        case (1, "автовелюр_серый"):
            return Some((0, 398, 1336, 1293))
        case _:
            return Nothing


def rndWinPos(imageSize: int, objPos: int, objSize: int, winSize: int) -> Option[int]:
    start = max(0, (objPos + objSize) - winSize)
    end = min(imageSize - winSize, objPos)
    return Some(randint(start, end)) if start < end else Nothing
