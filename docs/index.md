![Thapar Institute of Engineering and Technology](assets/Thapar-logo.png){ .tiet-logo }

**UCS503: Software Engineering (Project)**  
**TIET Patiala**

# Hostel Room Swap Service

**Author(s)**:

- Aabhas Khandelwal, CSED, `1024030673`
- Aakash Chawla, CSED, `1024031097`
- Joy Soni, CSED, `1024030674`

Group `3C51`, under Dr. Raghav B. Venkataramaiyer.

![A hostel at TIET](assets/hostel-m.png)

## Problem

Students are allocated hostel rooms they did not ask for -- wrong
hostel, wrong floor, wrong roommate, wrong room type. Direct one-to-one
swaps rarely work, because two students hardly ever want exactly what
the other has.

A three-way rotation usually does work: A takes B's room, B takes C's,
C takes A's. Nobody can find those chains by hand across a few thousand
rooms.

## What it does

Students submit weighted preferences over hostel, floor, direction,
attached washroom, room type and roommate, marking any of them as hard
or soft. The service returns up to three swap options, each with a
match percentage and the list of preferences it does and does not meet.

The three options differ in kind, not just in score:

| Option | Best at |
|---|---|
| Best overall match | highest average satisfaction |
| Fastest to execute | shortest chain, fewest approvals |
| Best location fit | hostel, floor and direction |

An option is only labelled with one of these if it genuinely beats the
others on that measure, so sometimes fewer than three are shown.

![A double room](assets/room.png){ width=280 }

## Approach

The pool is closed: the only rooms available are the ones the
participants already hold. So a solution is a permutation of students
over bed slots, and the swap chains are that permutation's cycles.

+ **Hungarian algorithm** (`scipy.optimize.linear_sum_assignment`) over
  a students x slots cost matrix finds the best permutation.
+ **Murty's algorithm** enumerates the next best ones, which matters
  because the optimal assignment often makes somebody worse off and
  gets rejected.
+ A **feasibility layer** keeps only chains where nobody loses and at
  least one student gains.

## Running it

``` shell
pip install -e "./code[dev]"
pytest -q
uvicorn hostelswap.api:app --reload
```

Then open <http://127.0.0.1:8000>. Without `DATABASE_URL` the app
serves a built-in demo cohort, so no database is needed to try it.

To work on the web UI, run the Vite dev server next to the API. It
proxies `/api` to port 8000:

``` shell
npm --prefix frontend install
npm --prefix frontend run dev
```

## Status

+ Matching engine, fairness filter and ranking: done, unit-tested.
+ Swap rounds: enroll, set priorities, lock, run, offer chains,
  respond, execute.
+ FastAPI backend with student and admin logins, on Postgres
  (Supabase), with schema migrations in `db/migrations/`.
+ React + TypeScript web UI for students and admins.
+ 137 tests passing.

## Journals

Weekly journals, one folder per member:

+ [Aabhas Khandelwal](journals/1024030673-Aabhas/index.md)
+ [Aakash Chawla](journals/1024031097-Aakash/w2-schema-enum-mismatch.md)
+ [Joy Soni](journals/1024030674-Joy/w2-ui-fixes.md)
