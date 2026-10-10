# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Archive readers (ADR 0013). Archives are built here from project-made bytes: no artwork."""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest
from tm import archives
from tm.archives import ArchiveError, expand

FILES = {"LOGO.ANS": b"\x1b[1;36mlogo\x1b[0m\r\n", "SUB/FILE_ID.DIZ": b"test pack\r\n"}


def make_zip(path: Path, files: dict[str, bytes] = FILES) -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("SUB/", b"")
        for name, data in files.items():
            archive.writestr(name, data)
    return path


def refuse(
    name: str,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception | None = None,
) -> None:
    """Make Python's reader fail on one member, as it does on PKZIP 1.x methods."""
    read = zipfile.ZipFile.read

    def fake(self: zipfile.ZipFile, member: str | zipfile.ZipInfo, pwd: bytes | None = None):
        if getattr(member, "filename", member) == name:
            raise error or NotImplementedError("That compression method is not supported")
        return read(self, member, pwd)

    monkeypatch.setattr(zipfile.ZipFile, "read", fake)


def test_zip_members_in_archive_order(tmp_path: Path) -> None:
    result = expand(make_zip(tmp_path / "p.zip"), "zip")
    assert (result.members, result.unreadable) == (list(FILES.items()), [])


def test_infozip_reads_what_python_cannot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    refuse("LOGO.ANS", monkeypatch)
    result = expand(make_zip(tmp_path / "p.zip"), "zip")
    assert (result.members, result.unreadable) == (list(FILES.items()), [])


def test_a_member_recorded_before_the_archive_goes_to_infozip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # textfiles' ascii/jasper/jasper06.zip: its first member's offset is -1
    refuse("LOGO.ANS", monkeypatch, ValueError("negative seek value -1"))
    result = expand(make_zip(tmp_path / "p.zip"), "zip")
    assert (result.members, result.unreadable) == (list(FILES.items()), [])


def test_a_member_whose_crc_does_not_match_is_unreadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    refuse("LOGO.ANS", monkeypatch)
    monkeypatch.setattr(archives.zlib, "crc32", lambda _data: 0)
    result = expand(make_zip(tmp_path / "p.zip"), "zip")
    assert result.unreadable == ["LOGO.ANS"]
    assert [name for name, _ in result.members] == ["SUB/FILE_ID.DIZ"]


def test_an_oversize_member_is_unreadable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(archives, "MAX_MEMBER_BYTES", 12)
    result = expand(make_zip(tmp_path / "p.zip"), "zip")
    assert (result.unreadable, [n for n, _ in result.members]) == (
        ["LOGO.ANS"],
        ["SUB/FILE_ID.DIZ"],
    )


def test_a_damaged_zip_is_a_classified_error(tmp_path: Path) -> None:
    damaged = tmp_path / "p.zip"
    damaged.write_bytes(b"PK\x03\x04 damaged")
    with pytest.raises(ArchiveError, match="bad_archive"):
        expand(damaged, "zip")


def without_central_directory(archive: Path) -> Path:
    """Cut the archive where its central directory starts, as a truncated download does."""
    data = archive.read_bytes()
    archive.write_bytes(data[: data.index(b"PK\x01\x02")])
    return archive


def test_a_zip_without_central_directory_is_read_by_its_local_headers(tmp_path: Path) -> None:
    result = expand(without_central_directory(make_zip(tmp_path / "p.zip")), "zip")
    assert (result.members, result.unreadable) == (list(FILES.items()), [])


def test_a_recovered_member_whose_crc_does_not_match_is_unreadable(tmp_path: Path) -> None:
    archive = tmp_path / "p.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_STORED) as stored:
        for name, data in FILES.items():
            stored.writestr(name, data)
    data = without_central_directory(archive).read_bytes()
    archive.write_bytes(data.replace(b"logo", b"LOGO"))
    result = expand(archive, "zip")
    assert result.unreadable == ["LOGO.ANS"]
    assert [name for name, _ in result.members] == ["SUB/FILE_ID.DIZ"]


def test_sevenzip_reads_in_listing_order(tmp_path: Path) -> None:
    # 7-Zip detects the format from the bytes: a ZIP exercises the same path as RAR or LHA.
    result = expand(make_zip(tmp_path / "p.lzh"), "lzh")
    assert (result.members, result.unreadable) == (list(FILES.items()), [])


def test_a_damaged_rar_is_a_classified_error(tmp_path: Path) -> None:
    damaged = tmp_path / "p.rar"
    damaged.write_bytes(b"Rar!\x1a\x07\x00 damaged")
    with pytest.raises(ArchiveError, match="bad_archive"):
        expand(damaged, "rar")


@pytest.mark.skipif(
    shutil.which("arj") is None,
    reason="arj is not installed: no Windows build exists (lead I97); CI runs this test",
)
def test_arj_members_in_name_order(tmp_path: Path) -> None:
    source = tmp_path / "src"
    for name, data in FILES.items():
        (source / name).parent.mkdir(parents=True, exist_ok=True)
        (source / name).write_bytes(data)
    arj = tmp_path / "p.arj"
    subprocess.run(
        ["arj", "a", "-r", "-y", str(arj), "*"], cwd=source, capture_output=True, check=True
    )
    result = expand(arj, "arj")
    assert (result.members, result.unreadable) == (sorted(FILES.items()), [])


def test_a_missing_reader_is_named(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(archives.shutil, "which", lambda _tool: None)
    with pytest.raises(ArchiveError, match="missing_reader: 7zz"):
        expand(make_zip(tmp_path / "p.rar"), "rar")


def test_an_unknown_format_is_unsupported(tmp_path: Path) -> None:
    with pytest.raises(ArchiveError, match="unsupported_archive"):
        expand(tmp_path / "p.ace", "ace")


def test_dos_names_are_read_as_cp437() -> None:
    assert archives._dos_name(b"art-core!/\xa1CE.MOD") == "art-core!/íCE.MOD"  # pyright: ignore[reportPrivateUsage]
    assert archives._dos_name("A∙C∙E.ANS".encode()) == "A∙C∙E.ANS"  # pyright: ignore[reportPrivateUsage]


def test_dos_paths_use_portable_separators() -> None:
    assert archives._dos_name(b"SUB\\FILE_ID.DIZ") == "SUB/FILE_ID.DIZ"  # pyright: ignore[reportPrivateUsage]
