"""Unit tests for the Python-generated transparent favicon ICO."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from art import favicon


def _frames(data: bytes) -> list[tuple[int, bytes]]:
    reserved, kind, count = struct.unpack_from("<HHH", data, 0)
    assert reserved == 0
    assert kind == 1
    assert count >= 1
    frames: list[tuple[int, bytes]] = []
    for index in range(count):
        width, height, _colors, _reserved, planes, bpp, nbytes, offset = struct.unpack_from(
            "<BBBBHHII", data, favicon._DIR + 16 * index
        )
        assert planes == 1
        assert bpp == 32
        dib_w, dib_h = struct.unpack_from("<ii", data, offset + 4)
        bitcount = struct.unpack_from("<H", data, offset + 14)[0]
        assert width == height == dib_w
        assert dib_h == height * 2
        assert bitcount == 32
        xor = data[offset + favicon._HEADER : offset + favicon._HEADER + width * height * 4]
        assert len(xor) == nbytes - favicon._HEADER - len(favicon._and_mask(width))
        frames.append((width, xor))
    return frames


def test_ico_is_deterministic() -> None:
    assert favicon.ico_bytes() == favicon.ico_bytes()


def test_every_pixel_is_fully_transparent() -> None:
    frames = _frames(favicon.ico_bytes())
    assert [size for size, _xor in frames] == list(favicon.SIZES)
    for _size, xor in frames:
        assert xor
        assert xor[3::4] == bytes(len(xor) // 4)


def test_empty_sizes_are_rejected() -> None:
    with pytest.raises(ValueError, match="at least one size"):
        favicon.ico_bytes(())


def test_write_roundtrip(tmp_path: Path) -> None:
    path = favicon.write(tmp_path / "favicon.ico")
    assert path.read_bytes() == favicon.ico_bytes()


def test_committed_favicon_matches_the_generator() -> None:
    assert favicon.FAVICON_PATH.is_file()
    assert favicon.FAVICON_PATH.read_bytes() == favicon.ico_bytes()


def test_main_writes_the_default_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "favicon.ico"
    monkeypatch.setattr(favicon, "FAVICON_PATH", target)
    path = favicon.main()
    assert path == target
    assert path.read_bytes() == favicon.ico_bytes()
    assert "wrote" in capsys.readouterr().out
