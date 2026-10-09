# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "research" / "explorer" / f"{name}.py"
    )
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


access = load("access")
museum = load("museum")
reading_module = load("readings")
graph_module = load("graph")


def decision(*, withdrawn=False, level=None, permission=True):
    return access.classify(
        SimpleNamespace(
            rights={"permission": {"display": permission}},
            privacy={"withdrawn": withdrawn},
            level=level,
            reviewed=level is not None,
            descriptors=[],
            notices=[],
        )
    )


def test_withdrawn_and_withheld_are_absent():
    assert decision(withdrawn=True).shown == "nothing"
    assert decision(level="withheld").shown == "nothing"


def test_metadata_only_and_adult_do_not_gain_file_access():
    assert decision(permission=False).shown == "record"
    assert decision(level="18").shown == "record"
    assert decision().shown == "files"


def test_static_host_cannot_read_outside_the_museum(tmp_path: Path):
    root = tmp_path / "site"
    root.mkdir()
    (tmp_path / "secret.env").write_text("private")
    (root / "work.html").write_text("shared work")
    assert museum.asset(root, "work") == ("text/html", b"shared work")
    assert museum.english(["en", "work"]) == "/work"
    assert museum.english(["en"]) == "/"
    assert museum.english(["fr", "work"]) is None
    assert museum.asset(root, "../secret.env") is None
    assert museum.asset(root, "%2e%2e/secret.env") is None


def vision():
    return dict(
        id="reading",
        title="Observation",
        body="A possible figure.",
        locale="en",
        kind="vision",
        nature="inferred",
        asserted_by="algo:reader@1",
        method="blind",
        input_sha256="a" * 64,
        uncertainty="Unverified",
        model="local-model@1",
        prompt_sha256="b" * 64,
        representation_sha256="c" * 64,
    )


def test_vision_cannot_be_presented_as_a_documented_fact():
    row = vision()
    row["nature"] = "documented"
    with pytest.raises(ValidationError, match="never documented"):
        reading_module.Reading.model_validate(row)


def test_model_identity_and_input_trace_are_required():
    row = vision()
    del row["model"]
    with pytest.raises(ValidationError, match="model and prompt"):
        reading_module.Reading.model_validate(row)
    assert reading_module.readings(Path("/nonexistent-readings"), "a" * 64) == []


def test_reading_cannot_be_attached_to_another_work(tmp_path):
    (tmp_path / f"{'b' * 64}.json").write_text(json.dumps([vision()]))
    with pytest.raises(ValueError, match="does not match"):
        reading_module.readings(tmp_path, "b" * 64)


def test_filtered_graph_keeps_indices_and_removes_hidden_examples(tmp_path):
    hashes = [letter * 64 for letter in "abc"]
    pq.write_table(
        pa.table(
            {
                "sha256": hashes,
                "x": [0.0, 1.0, 2.0],
                "y": [0.0, 1.0, 2.0],
                "community": [0, 0, 1],
                "in_degree": [1, 1, 1],
            }
        ),
        tmp_path / "nodes.parquet",
    )
    pq.write_table(
        pa.table(
            {
                "sha256": hashes,
                "year": [1996] * 3,
                "content_kind": ["text"] * 3,
                "sauce_group": ["group"] * 3,
                "sauce_author": ["signature"] * 3,
                "pack": ["pack"] * 3,
                "path": ["file"] * 3,
                "archive": ["16colo"] * 3,
                "sauce_title": ["title"] * 3,
            }
        ),
        tmp_path / "works.parquet",
    )
    pq.write_table(
        pa.table({"sha256": hashes, "fg_hist": [[1] * 16] * 3}), tmp_path / "features.parquet"
    )
    pq.write_table(
        pa.table(
            {
                "source": [hashes[0], hashes[0], hashes[1]],
                "target": [hashes[1], hashes[2], hashes[2]],
                "rank": [0, 1, 0],
            }
        ),
        tmp_path / "edges.parquet",
    )
    communities = [
        dict(
            community=i,
            works=2,
            typical=[hashes[1]],
            archetype=hashes[1],
            axis={"from_works": [hashes[1]], "to_works": [hashes[2]]},
        )
        for i in range(2)
    ]
    (tmp_path / "communities.json").write_text(json.dumps({"communities": communities}))
    graph = graph_module.Graph(tmp_path, tmp_path, {hashes[0], hashes[2]})
    assert json.loads(graph.nodes)["sha256"] == [hashes[0], hashes[2]]
    assert np.frombuffer(graph.edges, dtype="<u4").tolist() == [0, 1]
    assert hashes[1] not in graph.communities.decode()
    assert graph.neighbours() == {hashes[0]: [hashes[2]]}
