# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest
from packs_on_disk import HORIZON, ingest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from stores import Stores
from tm.acquisitions import COLUMNS, load_acquisitions

pytestmark = pytest.mark.db


def record(path: Path, rows: list[dict[str, str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_every_file_says_where_and_when_it_was_fetched(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = tmp_path / "1995" / "a.zip"
    ingest(db, stores, pack, {"HORIZON.ANS": HORIZON})
    archive = hashlib.sha256(pack.read_bytes()).hexdigest()
    row = {
        "path": "1995/a.zip",
        "url": "rsync://16colo.rs/archive-pack/1995/a.zip",
        "method": "rsync",
        "retrieved_at": "2026-10-08T11:48:20+00:00",
        "retrieved_basis": "mirror_run",
        "remote": json.dumps({"mtime": "2012-03-07T20:52:00+00:00"}),
        "sha256": archive,
    }
    other = dict(row, sha256="c" * 64, path="1995/b.zip")
    tsv = record(tmp_path / "acquisitions.tsv", [row, other])
    loaded = load_acquisitions(db, tsv, "16colo")
    assert (loaded.recorded, loaded.already, loaded.not_held) == (1, 0, 1)
    again = load_acquisitions(db, tsv, "16colo")
    assert (again.recorded, again.already) == (0, 1)
    provenance = db.execute(
        text(
            "select via_archive, path_in_archive, url, source, remote ->> 'mtime'"
            " from artifact_provenance where sha256 = :s"
        ),
        {"s": hashlib.sha256(HORIZON).hexdigest()},
    ).one()
    assert tuple(provenance) == (
        archive,
        "HORIZON.ANS",
        row["url"],
        "16colo",
        "2012-03-07T20:52:00+00:00",
    )


def test_an_acquisition_is_append_only_and_honest_about_its_time(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = tmp_path / "1995" / "a.zip"
    ingest(db, stores, pack, {"HORIZON.ANS": HORIZON})
    insert = (
        "insert into acquisition (sha256, source_id, url, method, retrieved_at,"
        " retrieved_basis, recorded_by) select :s, id, 'http://x/a.zip', 'http', :at, :basis,"
        " 'algo:test' from source where name = '16colo'"
    )
    sha = hashlib.sha256(pack.read_bytes()).hexdigest()
    for at, basis in ((None, "recorded"), ("2026-10-09T00:00:00Z", "unknown")):
        savepoint = db.begin_nested()
        with pytest.raises(DBAPIError, match="check"):
            db.execute(text(insert), {"s": sha, "at": at, "basis": basis})
        savepoint.rollback()
    db.execute(text(insert), {"s": sha, "at": None, "basis": "unknown"})
    for statement in ("delete from acquisition", "update acquisition set url = 'http://y'"):
        savepoint = db.begin_nested()
        with pytest.raises(DBAPIError, match="append-only"):
            db.execute(text(statement))
        savepoint.rollback()
