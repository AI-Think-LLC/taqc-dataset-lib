from taqc.dataset import ShotInfo


def test_shotinfo():
    assert (
        ShotInfo.fromFilename("f6c50725-127_c0_Ткань_чулок_рибана.jpg").value.side == 0
    )
