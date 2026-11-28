"""The one-live-proposal rule, checked against a real PostgreSQL.

These need a throwaway database with the migrations applied, named by
TEST_DATABASE_URL (never DATABASE_URL, which conftest clears so the
rest of the suite stays hermetic). Every test empties the tables first,
so the URL must never point at a shared database.
"""

import os
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from hostelswap import db

DSN = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(not DSN, reason="TEST_DATABASE_URL not set")

NOW = datetime.now(timezone.utc)
PAST, FUTURE = NOW - timedelta(minutes=1), NOW + timedelta(days=3)


@pytest.fixture
def cohort():
    """Three students in three single rooms, and a completed round."""
    assert "supabase" not in DSN, "refusing to wipe a shared database"
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute(
            "truncate students, hostels, swap_rounds, swap_proposals restart identity cascade"
        )
        cur.execute("insert into hostels (code, name) values ('T', 'Test') returning id")
        hostel = cur.fetchone()[0]
        cur.execute(
            "insert into swap_rounds (hostel_id, status) values (%s, 'completed') returning id",
            (hostel,),
        )
        round_id = str(cur.fetchone()[0])
        students = {}
        for n, roll in enumerate("abc", 1):
            cur.execute(
                "insert into rooms (hostel_id, room_no, floor, direction, capacity) "
                "values (%s, %s, 1, 'N', 1) returning id",
                (hostel, f"10{n}"),
            )
            cur.execute(
                "insert into bed_slots (room_id, label) values (%s, 'a') returning id",
                (cur.fetchone()[0],),
            )
            slot = str(cur.fetchone()[0])
            cur.execute(
                "insert into students (roll_no, name, email) values (%s, %s, %s) returning id",
                (roll, roll.upper(), f"{roll}@test"),
            )
            students[roll] = (str(cur.fetchone()[0]), slot)
    return round_id, students


def offer(cohort, rolls, expires_at=FUTURE):
    """Offer a ring through the rolls given, the first of them offering."""
    round_id, students = cohort
    members = [
        {
            "studentId": students[roll][0],
            "rollNo": roll,
            "fromSlotId": students[roll][1],
            "toSlotId": students[rolls[(i + 1) % len(rolls)]][1],
            "matchValue": 0.5,
        }
        for i, roll in enumerate(rolls)
    ]
    return db.insert_proposal(
        DSN, round_id, "recommended", 0.5, len(rolls), expires_at, members, rolls[0]
    )


def status_of(proposal_id):
    return db.fetch_proposal(DSN, proposal_id)["status"]


def test_a_student_cannot_be_live_in_two_chains(cohort):
    offer(cohort, "ab")

    with pytest.raises(db.AlreadyReserved):
        offer(cohort, "ac")


def test_a_non_responder_stops_blocking_once_the_proposal_expires(cohort):
    stale = offer(cohort, "ab", expires_at=PAST)
    with pytest.raises(db.AlreadyReserved):
        offer(cohort, "ac")

    db.expire_due_proposals(DSN)

    assert status_of(stale) == "expired"
    offer(cohort, "ac")


def test_a_member_of_an_executed_chain_can_join_another(cohort):
    round_id, students = cohort
    done = offer(cohort, "ab")
    approvals = {students[r][0]: "approved" for r in "ab"}
    db.update_proposal(DSN, done, "executed", approvals, settled=True)

    offer(cohort, "ac")


def test_cancelling_a_round_frees_its_members(cohort):
    round_id, _ = cohort
    pending = offer(cohort, "ab")

    db.cancel_round(DSN, round_id)

    assert status_of(pending) == "cancelled"
    assert db.fetch_round(DSN, round_id)["status"] == "cancelled"
    offer(cohort, "ac")
