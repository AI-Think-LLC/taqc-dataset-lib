from taqc.dataset import ShotInfo
from taqc.dataset.common import getCropBox


def test_shotinfo():
    assert (
        ShotInfo.fromFilename("f6c50725-127_c0_Ткань_чулок_рибана.jpg").value.side == 0
    )


def test_cropbox():
    ShotInfo.fromFilename("dd257ce0-1032_c1_Не_выбрано.jpg").bind(getCropBox).value == (
        0,
        0,
        1984,
        1296,
    )


def test_cropbox_additional():
    assert ShotInfo.fromFilename("dd257ce0-1032_c1_abcdef.jpg").bind(
        lambda x: getCropBox(x, {"abcdef": ((0, 0, 0, 0), (1, 1, 1, 1))})
    ).value == (1, 1, 1, 1)
