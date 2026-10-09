# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Reading pack archives: the files inside, byte for byte, in archive order (ADR 0013).

ZIP is read in Python. Members stored with methods Python lacks (shrink, implode, from PKZIP
1.x) are taken from Info-ZIP `unzip` and checked against the CRC-32 the archive records. A ZIP
Python cannot open (no central directory, often a truncated download) is listed and extracted by
7-Zip from its local headers, each member checked the same way (ADR 0014). RAR,
LHA and LZH are read with the official 7-Zip build, ARJ with `arj`; both check their own CRCs.
A member that cannot be read is named in `unreadable`, never guessed.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
import zlib
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

MAX_MEMBER_BYTES = 256 * 1024 * 1024
TOOL_TIMEOUT_SECONDS = 300
FAILED_7ZZ = re.compile(rb"^ERROR: [^:]+ : (.+?)\r?$", re.MULTILINE)
UNREADABLE = (zipfile.BadZipFile, NotImplementedError, RuntimeError, zlib.error, EOFError)


class ArchiveError(Exception):
    """The archive as a whole cannot be read: `kind` is a classified error."""

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__(f"{kind}: {detail}")
        self.kind = kind


@dataclass
class Expanded:
    members: list[tuple[str, bytes]] = field(default_factory=list[tuple[str, bytes]])
    unreadable: list[str] = field(default_factory=list[str])


def expand(path: Path, archive_format: str) -> Expanded:
    if archive_format == "zip":
        return _zip(path)
    if archive_format in {"rar", "lha", "lzh"}:
        return _sevenzip(path)
    if archive_format == "arj":
        return _arj(path)
    raise ArchiveError("unsupported_archive", archive_format)


def _zip(path: Path) -> Expanded:
    try:
        archive = zipfile.ZipFile(BytesIO(path.read_bytes()))
    except zipfile.BadZipFile as err:
        return _zip_recovered(path, err)
    infos = [info for info in archive.infolist() if not info.is_dir()]
    read: dict[str, bytes] = {}
    for info in infos:
        if info.file_size <= MAX_MEMBER_BYTES:
            with contextlib.suppress(*UNREADABLE):  # left to Info-ZIP below
                read[info.filename] = archive.read(info)
    missing = [info for info in infos if info.filename not in read]
    if missing:
        read.update(_zip_with_infozip(path, missing))
    result = Expanded()
    for info in infos:
        if info.filename in read:
            result.members.append((info.filename, read[info.filename]))
        else:
            result.unreadable.append(info.filename)
    return result


def _zip_with_infozip(path: Path, wanted: list[zipfile.ZipInfo]) -> dict[str, bytes]:
    """Members Python could not read, extracted by Info-ZIP and kept only if their CRC matches.

    A member is found by name, or, when the tool spelt a DOS name differently, by size and CRC.
    """
    found: dict[str, bytes] = {}
    with tempfile.TemporaryDirectory() as tmp:
        _run(["unzip", "-qq", "-o", str(path), "-d", tmp])
        files = _extracted(tmp)
        for info in wanted:
            if info.file_size > MAX_MEMBER_BYTES:
                continue
            named = files.get(info.filename)
            candidates = [named] if named else [p for p in files.values() if _sized(p, info)]
            for candidate in candidates:
                data = candidate.read_bytes()
                if len(data) == info.file_size and zlib.crc32(data) == info.CRC:
                    found[info.filename] = data
                    break
    return found


def _zip_recovered(path: Path, err: zipfile.BadZipFile) -> Expanded:
    """A ZIP without a usable central directory: 7-Zip finds the members by their local headers,
    and each is kept only if its size and CRC-32 match that header (ADR 0014)."""
    listing = _run(["7zz", "l", "-slt", "-ba", "-tzip", str(path)])
    entries = [
        fields
        for fields in map(_fields, listing.stdout.replace(b"\r\n", b"\n").split(b"\n\n"))
        if b"Path" in fields
        and fields.get(b"Folder") != b"+"
        and not fields.get(b"Attributes", b"").startswith(b"D")
    ]
    if not entries:
        raise ArchiveError("bad_archive", str(err)) from err
    result = Expanded()
    with tempfile.TemporaryDirectory() as tmp:
        _run(["7zz", "x", "-y", "-tzip", f"-o{tmp}", str(path)])
        files = _extracted(tmp)
        for entry in entries:
            name = _dos_name(entry[b"Path"])
            data = files[name].read_bytes() if name in files else b""
            if name in files and _matches(data, entry):
                result.members.append((name, data))
            else:
                result.unreadable.append(name)
    return result


def _fields(block: bytes) -> dict[bytes, bytes]:
    """One entry of a `7zz l -slt` listing, as its `Key = value` lines."""
    pairs = (line.split(b" = ", 1) for line in block.splitlines() if b" = " in line)
    return {key: value.strip() for key, value in pairs}


def _matches(data: bytes, entry: dict[bytes, bytes]) -> bool:
    return (
        len(data) <= MAX_MEMBER_BYTES
        and str(len(data)).encode() == entry.get(b"Size")
        and f"{zlib.crc32(data):08X}".encode() == entry.get(b"CRC")
    )


def _sized(path: Path, info: zipfile.ZipInfo) -> bool:
    return path.stat().st_size == info.file_size


def _sevenzip(path: Path) -> Expanded:
    listing = _run(["7zz", "l", "-slt", "-ba", str(path)])
    names = [
        _dos_name(block.split(b"\n", 1)[0].removeprefix(b"Path = "))
        for block in listing.stdout.replace(b"\r\n", b"\n").split(b"\n\n")
        if block.startswith(b"Path = ") and b"\nAttributes = D" not in block
    ]
    with tempfile.TemporaryDirectory() as tmp:
        run = _run(["7zz", "x", "-y", f"-o{tmp}", str(path)])
        failed = {_dos_name(name) for name in FAILED_7ZZ.findall(run.stdout + run.stderr)}
        if not names and run.returncode != 0:
            raise ArchiveError("bad_archive", run.stderr.decode(errors="replace").strip()[:200])
        return _collect(_extracted(tmp), names, failed)


def _arj(path: Path) -> Expanded:
    with tempfile.TemporaryDirectory() as tmp:
        run = _run(["arj", "x", "-y", str(path), f"{tmp}/"])
        if run.returncode != 0:
            raise ArchiveError("bad_archive", run.stdout.decode(errors="replace").strip()[-200:])
        files = _extracted(tmp)
        return _collect(files, sorted(files), set())


def _collect(files: dict[str, Path], names: list[str], failed: set[str]) -> Expanded:
    """Files a tool extracted, in the order given; the failed, missing or oversize are named."""
    result = Expanded()
    for name in names:
        target = files.get(name)
        if target and name not in failed and target.stat().st_size <= MAX_MEMBER_BYTES:
            result.members.append((name, target.read_bytes()))
        else:
            result.unreadable.append(name)
    return result


def _extracted(tmp: str) -> dict[str, Path]:
    """Regular files a tool wrote under `tmp`, by their name in the archive."""
    root = Path(tmp)
    return {
        _dos_name(os.fsencode(p.relative_to(root))): p
        for p in root.rglob("*")
        if not p.is_symlink() and p.is_file()
    }


def _dos_name(raw: bytes) -> str:
    """Tools pass DOS names through as raw bytes when they are not UTF-8: read those as CP437,
    the character set of the period, as Python does for ZIP names."""
    try:
        return raw.decode("utf-8").replace("\\", "/")
    except UnicodeDecodeError:
        return raw.decode("cp437").replace("\\", "/")


def _run(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    if shutil.which(args[0]) is None:
        raise ArchiveError("missing_reader", f"{args[0]} is not installed (ADR 0013)")
    return subprocess.run(
        args,
        capture_output=True,
        timeout=TOOL_TIMEOUT_SECONDS,
        check=False,  # tools report damaged members by exit code; callers read the output
    )
