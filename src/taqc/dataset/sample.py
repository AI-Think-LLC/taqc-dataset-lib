from dataclasses import dataclass
import dataclasses
import os
from random import randint
from typing import Container, Iterable
from PIL import Image, ImageDraw
from expression.collections import Block, Seq
from more_itertools import take
from .common import rndCropIncludingRect
from . import Object, Rect, Point, Size


@dataclass
class Sample:
    image: Image.Image
    objects: Block[Object]

    @staticmethod
    def read(
        dataset_path: str, filename: str, image_folder="images", label_folder="labels"
    ) -> "Sample":
        basename, _ = os.path.splitext(filename)
        image = Image.open(f"{dataset_path}/raw/{image_folder}/{filename}")

        return Sample(
            image=image,
            objects=Seq(
                open(f"{dataset_path}/raw/{label_folder}/{basename}.txt").readlines()
            )
            .choose(lambda line: Object.parse(line, image.size))
            .to_list(),
        )

    def displayRects(self):
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)
        for obj in self.objects:
            draw.rectangle([*obj.box.lt, *obj.box.rb], outline="red")
        return image_copy

    def crop(self, cropBox: tuple[int, int, int, int]):
        newOrigin = Point(*cropBox[:2])
        newImage = self.image.copy().crop(cropBox)
        return Sample(
            newImage,
            objects=self.objects.map(
                lambda obj: obj.updateRect(
                    lambda rect: Rect(rect.lt - newOrigin, rect.rb - newOrigin)
                )
            ).choose(
                lambda obj: obj.box.adjustToBoundaries(Size(*newImage.size)).map(
                    lambda box: dataclasses.replace(obj, box=box)
                )
            ),
        )

    def rndEmpty(self, tileSize: Size) -> "Sample":
        def rndTiles():
            for _ in range(10):
                x0 = randint(0, self.image.size[0] - tileSize.width)
                y0 = randint(0, self.image.size[1] - tileSize.height)
                yield Rect(
                    Point(x0, y0), Point(x0 + tileSize.width, y0 + tileSize.height)
                )

        image = next(
            self.image.copy().crop(tile.toTuple())  # type: ignore
            for tile in rndTiles()
            if all(self.objects.map(lambda defect: not defect.box.overlaps(tile)))
        )

        return Sample(image, Block.empty())

    def rndDefects(
        self, tileSize: Size, categories: Container[int] | None = None
    ) -> Block["Sample"]:
        imageSize = Size(*self.image.size)
        return self.objects.filter(
            lambda obj: obj.category in categories if categories is not None else True
        ).choose(
            lambda obj: rndCropIncludingRect(imageSize, obj.box, tileSize).map(
                self.crop
            )
        )

    def toCocoJson(self, filename: str, idsIter: Iterable[int]):
        return {
            "file_name": filename,
            "width": self.image.size[0],
            "height": self.image.size[1],
            "image_id": int(filename[: filename.index(".")]),
            "objects": {
                "bbox": list(self.objects.map(lambda obj: obj.box.toCocoBounds())),
                "area": list(self.objects.map(lambda obj: obj.box.size.area)),
                "category": list(self.objects.map(lambda obj: obj.category)),
                "id": take(len(self.objects), idsIter),
            },
        }
