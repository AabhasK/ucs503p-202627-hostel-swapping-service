from datetime import datetime, timedelta, timezone

import pytest

from hostelswap import rounds


def _proposal(expires_at):
    return {
        "id": "p1",
        "status": "proposed",
        "expiresAt": expires_at,
        "settledAt": None,
        "members": [
            {"rollNo": "a", "studentId": "uuid-a", "fromSlotId": "s1", "toSlotId": "s2", "approval": "pending"},
            {"rollNo": "b", "studentId": "uuid-b", "fromSlotId": "s2", "toSlotId": "s1", "approval": "pending"},
        ],
    }


@pytest.fixture
def updates(monkeypatch):
    calls = []
    monkeypatch.setattr(
        rounds.db, "update_proposal",
        lambda dsn, pid, status, approvals, settled: calls.append((pid, status, settled)),
    )
    return calls


def test_a_late_accept_is_refused_and_the_proposal_expires(monkeypatch, updates):
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    monkeypatch.setattr(rounds.db, "fetch_proposal", lambda dsn, pid: _proposal(past))

    with pytest.raises(rounds.InvalidRoundState, match="expired"):
        rounds.respond("dsn", "p1", "a", accept=True)

    assert updates == [("p1", "expired", True)]


def test_an_accept_before_the_deadline_still_counts(monkeypatch, updates):
    future = datetime.now(timezone.utc) + timedelta(days=1)
    monkeypatch.setattr(rounds.db, "fetch_proposal", lambda dsn, pid: _proposal(future))

    assert rounds.respond("dsn", "p1", "a", accept=True) == {"status": "proposed"}


def test_offering_a_chain_first_expires_overdue_proposals(monkeypatch):
    order = []
    member = {"rollNo": "a", "studentId": "uuid-a", "fromSlotId": "s1", "toSlotId": "s2", "match": 80}
    monkeypatch.setattr(rounds, "_require_round", lambda dsn, rid: {"status": "completed"})
    monkeypatch.setattr(
        rounds.db, "fetch_chain_options",
        lambda dsn, rid: [{"optionKind": "recommended", "chainNo": 1, "members": [member]}],
    )
    monkeypatch.setattr(rounds.db, "expire_due_proposals", lambda dsn: order.append("sweep"))
    monkeypatch.setattr(rounds.db, "insert_proposal", lambda *a, **k: order.append("insert") or "p2")

    assert rounds.offer_chain("dsn", "r1", "a", "recommended", 1) == "p2"
    assert order == ["sweep", "insert"]
