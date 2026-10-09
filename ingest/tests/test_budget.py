# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from tm.budget import BudgetError, Ledger
from tm.cli import app
from tm.config import settings
from typer.testing import CliRunner

runner = CliRunner()


def test_no_grant_no_call(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.jsonl")
    called = False
    with pytest.raises(BudgetError, match="exceeds"), ledger.call("q33", 0.01, "m"):
        called = True
    assert not called


def test_a_call_spends_what_it_cost_and_frees_its_reservation(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.grant("q33", 1.0, "owner", "chat 2026-10-10")
    with ledger.call("q33", 0.30, "model@1") as record:
        assert ledger.balance("q33").reserved == pytest.approx(0.30)
        record(0.12, tokens_in=1500, tokens_out=900)
    balance = ledger.balance("q33")
    assert (balance.spent, balance.reserved) == (pytest.approx(0.12), pytest.approx(0))
    assert balance.left == pytest.approx(0.88)


def test_the_grant_is_a_hard_cap(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.grant("q33", 0.5, "owner", "")
    with ledger.call("q33", 0.4, "m") as record:
        record(0.4)
    with pytest.raises(BudgetError, match="left"), ledger.call("q33", 0.2, "m"):
        pass
    assert ledger.balance("other").granted == 0  # a grant covers its scope only


def test_an_unrecorded_or_failed_call_is_charged_its_estimate(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.grant("q33", 1.0, "owner", "")
    with pytest.raises(RuntimeError), ledger.call("q33", 0.25, "m"):
        raise RuntimeError("network")
    assert ledger.balance("q33").spent == pytest.approx(0.25)


def test_the_ledger_only_grows_and_never_holds_a_key(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path)
    ledger.grant("q33", 1.0, "owner", "ok")
    before = path.read_text()
    with pytest.raises(BudgetError, match="credential"):
        ledger.grant("q33", 1.0, "owner", "sk-or-v1-0123456789abcdef")
    with pytest.raises(BudgetError, match="negative"):
        ledger.grant("q33", -1.0, "owner", "")
    assert path.read_text() == before


def test_cli_grant_asks_and_status_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TM_MODEL_LEDGER", str(tmp_path / "ledger.jsonl"))
    settings.cache_clear()
    try:
        assert "no grant" in runner.invoke(app, ["budget", "status"]).output
        args = ["budget", "grant", "--scope", "q33", "--usd", "2", "--note", "chat"]
        assert runner.invoke(app, args, input="n\n").exit_code == 1
        assert runner.invoke(app, args, input="y\n").exit_code == 0
        assert "q33: granted $2.00" in runner.invoke(app, ["budget", "status"]).output
    finally:
        settings.cache_clear()
