from pathlib import Path

from avalon.mp3 import create_mp3


def test_create_mp3(tmpdir):

    create_mp3(output_mp3_path=tmpdir)
    assert len(list(Path(tmpdir).glob("*.mp3"))) == 8
