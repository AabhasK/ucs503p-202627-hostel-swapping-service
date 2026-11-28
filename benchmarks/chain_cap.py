"""Reproduce the chain-cap benchmark.

    python benchmarks/chain_cap.py [--students 300] [--k 200] [--seeds 10]

For each seeded cohort, one Murty search (the K best assignments) is
shared by every cap. Per cap:

- offered: share of students in at least one Pareto-improving chain
  no longer than the cap, among the chains each student would be shown
  (`candidate_chains`, up to three per student);
- served: share of students moved when the offered chains are taken
  greedily, best mean match first, skipping any chain that shares a
  student with one already taken (chains compete for the same rooms);
- satisfaction: mean score over the whole cohort after the served
  chains move;
- chains, mean length: of the offered chains.

Prints mean and population standard deviation over the seeds.
"""

import argparse
import pathlib
import sys
import time
from statistics import fmean, pstdev

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "code"))

from hostelswap.domain.kbest import k_best  # noqa: E402
from hostelswap.domain.matrix import build_matrix  # noqa: E402
from hostelswap.domain.ranking import candidate_chains  # noqa: E402
from hostelswap.synth.generator import generate_pool  # noqa: E402

CAPS = (5, 8, 10)


def measure(students: int, k: int, seed: int) -> dict:
    pool = generate_pool(students, seed=seed, hostels=("A",))  # one hostel, as a round is
    matrix = build_matrix(pool)
    candidates = k_best(matrix, k)
    current = {s.id: matrix.score_for(s.id, pool.current_slot_id(s.id)).value for s in pool.students}
    out = {"baseline": fmean(current.values())}
    for cap in CAPS:
        offers = candidate_chains(pool, matrix, candidates, per_student=3, max_chain=cap)
        offered = {s for o in offers for s in o.students}
        moved: dict[str, float] = {}
        for offer in offers:  # already best mean match first
            if not moved.keys() & set(offer.students):
                moved.update({s: offer.outcomes[s].match.value for s in offer.students})
        out[cap] = {
            "offered": 100 * len(offered) / students,
            "served": 100 * len(moved) / students,
            "satisfaction": 100 * fmean(moved.get(s, v) for s, v in current.items()),
            "chains": len(offers),
            "length": fmean(len(o.students) for o in offers) if offers else 0.0,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", type=int, default=300)
    parser.add_argument("--k", type=int, default=200)
    parser.add_argument("--seeds", type=int, default=10)
    args = parser.parse_args()

    runs = []
    for seed in range(1, args.seeds + 1):
        start = time.perf_counter()
        runs.append(measure(args.students, args.k, seed))
        print(f"seed {seed}: {time.perf_counter() - start:.1f}s", file=sys.stderr)

    print(f"{args.students} students, K={args.k}, seeds 1-{args.seeds}; "
          f"baseline satisfaction {100 * fmean(r['baseline'] for r in runs):.1f}%")
    print("cap | offered %   | served %    | satisfaction % | chains       | mean length")
    for cap in CAPS:
        cells = []
        for key in ("offered", "served", "satisfaction", "chains", "length"):
            values = [r[cap][key] for r in runs]
            cells.append(f"{fmean(values):5.1f} ± {pstdev(values):4.1f}")
        print(f"{cap:>3} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
