# Tutorial: Run a Swap Round End to End

This walks one round from an empty database to a swap offer that every
member must answer. It takes about ten minutes. Every account the seed
scripts create uses the password `swap1234`.

## 1. Install

``` shell
git clone https://github.com/AakashChawla07/ucs503p-202627-hostel-swapping-service
cd ucs503p-202627-hostel-swapping-service
python -m venv .venv
.venv/Scripts/activate            # source .venv/bin/activate on Linux/macOS
pip install -e "./code[dev]"
```

## 2. Point it at a database

Any PostgreSQL 13 or later works: a local one, or a free Supabase
project (Connect, then Session pooler, then copy the URI). Put the
connection string in `.env` at the repository root:

``` shell
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Use a database of its own. The seed step below empties every table.

## 3. Create the tables and the demo hostel

``` shell
python db/migrate.py     # applies db/migrations/0001, 0002, ...
python db/seed.py        # hostel A: 30 rooms, 30 students, warden admin001
```

## 4. Start the app

``` shell
uvicorn hostelswap.api:app
```

Open <http://127.0.0.1:8000>.

## 5. Open a round (warden)

1. Sign in as `admin001` / `swap1234`.
2. Under **Round control**, press **Create a round**, then **Open
   registration**.

## 6. Fill the round with students

Students normally enrol and set their own priorities on the student
page. To fill a round quickly, a script adds 28 enrolled students with
priorities (roll numbers `1024030040` to `1024030067`):

``` shell
python db/seed_round.py
```

Reload the warden page: **Enrolled** and **Priorities set** read 28.

## 7. Run the matching (warden)

Press **Lock and run matching** and keep the chain cap at 8. Locking
closes registration for good, then the engine runs (Hungarian
assignment, Murty's alternatives, cycles, the "nobody worse off" filter).
The page then shows how many rings were found and how many students have
at least one.

## 8. Offer a ring (student)

1. Log out, and sign in as a student, for example `1024030041`.
2. **Your options** lists up to three rings that include you, best for
   you first, with the match each member gets.
3. Press **Offer this swap** on one, then **Offer to N others**. It
   becomes a proposal with a three-day deadline, and you have approved
   it already.

If a student has no options, try another roll number: not everyone is in
a ring.

## 9. Answer it (the other members)

Sign in as each other member of the ring. Under **Offers awaiting a
reply** they see the ring, everyone's reply so far and "closes in 3 d".

- When the last member presses **Accept**, the swap executes: everyone
  moves, and the room history records the new allocations.
- One **Reject** ends the ring at once and frees all its members.
- If someone never answers, the ring expires after three days and its
  members are free to join another.

## 10. What the warden can do meanwhile

- Follow every ring and reply under **Swap rings offered this round**.
- **Withdraw** a ring that is stuck; its students are freed.
- **Cancel round** withdraws all of the round's open rings. Swaps that
  already executed stay.

## Without a database

With no `DATABASE_URL`, sign-in is unavailable, but the engine still
runs on a built-in 30-student cohort:
<http://127.0.0.1:8000/api/demo?k=50>. Compare `k=1` with `k=50`: the
same 77% satisfaction, but the longest chain falls from 28 students
to 11.

See the [API reference](api-reference.md) for every endpoint.
