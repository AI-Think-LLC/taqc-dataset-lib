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
    @effect.option["ShotInfo"]()  # type: ignore
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
FabricCropBoxes = tuple[CropBox, CropBox]


def clamp(x: float, minimum: float = 0, maximum: float = 1) -> float:
    if x < minimum:
        return minimum
    elif x > maximum:
        return maximum
    else:
        return x


knownCropBoxes = {
    "подкладочная_таффета_белый": ((783, 221, 2303, 1197), (0, 372, 1260, 1294)),
    "трикотаж_жаккард_TRELAX_tencel": ((307, 244, 2303, 1197), (0, 372, 1862, 1294)),
    "Костюмка_Лиза": ((644, 244, 2303, 1197), (0, 396, 1045, 1293)),
    "чулок_рибана": ((504, 296, 2303, 1250), (0, 388, 1465, 1293)),
    "автовелюр_серый": ((675, 271, 2303, 1230), (0, 398, 1336, 1293)),
    "Не_выбрано": ((351, 0, 2304, 1296), (0, 0, 1984, 1296)),
    "Ткань_жаккард_TRELAX_Atlas": ((138, 258, 2304, 973), (0, 417, 2023, 1151)),
    "Ткань_трикотаж_жаккард_Премиум_Соты_розовый": (
        (100, 223, 2304, 1296),
        (0, 351, 1728, 1271),
    ),
    "Ткань_трикотаж_вискоза_бежевый": ((348, 247, 2304, 1296), (0, 368, 1477, 1286)),
}


def getCropBox(
    shot: ShotInfo, additionalBoxes: dict[str, FabricCropBoxes] = {}
) -> Option[CropBox]:
    return option.of_obj(
        (knownCropBoxes | additionalBoxes).get(shot.fabricType, None)
    ).map(lambda x: x[shot.side])


def rndWinPos(imageSize: int, objPos: int, objSize: int, winSize: int) -> Option[int]:
    start = max(0, (objPos + objSize) - winSize)
    end = min(imageSize - winSize, objPos)
    return Some(randint(start, end)) if start < end else Nothing
