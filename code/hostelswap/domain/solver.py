"""Hungarian assignment over the cost matrix."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment

from .matrix import INFEASIBLE, CostMatrix

Edge = tuple[str, str]


class NoFeasibleAssignment(Exception):
    pass


@dataclass(frozen=True)
class Assignment:
    slot_by_student: Mapping[str, str]
    cost: float

    @property
    def edges(self) -> frozenset[Edge]:
        return frozenset(self.slot_by_student.items())

    def __len__(self) -> int:
        return len(self.slot_by_student)


def solve(
    matrix: CostMatrix,
    forbidden: Iterable[Edge] = (),
    required: Iterable[Edge] = (),
) -> Assignment:
    """Best assignment with some edges forbidden and some fixed.

    A fixed edge is forced by setting the rest of its row and column to
    infinity, on the full matrix. Cutting fixed rows and columns out
    instead is faster and finds assignments of the same cost, but a
    round has many exactly tied optima, and which of them the solver
    returns decides which chains Murty's search ever sees: on 300
    students the cut-out version offered 3-10x fewer chains.
    """
    costs = matrix.costs.copy()
    for s, t in forbidden:
        costs[matrix.row_of[s], matrix.column_of[t]] = INFEASIBLE
    for s, t in required:
        row, column = matrix.row_of[s], matrix.column_of[t]
        keep = costs[row, column]
        costs[row, :] = INFEASIBLE
        costs[:, column] = INFEASIBLE
        costs[row, column] = keep

    try:
        rows, columns = linear_sum_assignment(costs)
    except ValueError as exc:
        raise NoFeasibleAssignment("hard constraints cannot all be met") from exc

    total = float(costs[rows, columns].sum())
    if not np.isfinite(total):
        raise NoFeasibleAssignment("hard constraints cannot all be met")

    return Assignment(
        slot_by_student={matrix.student_ids[r]: matrix.slot_ids[c] for r, c in zip(rows, columns)},
        cost=total,
    )
