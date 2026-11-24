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

    Fixed edges are cut out of the matrix rather than forced by setting
    the rest of their row and column to infinity, so each of Murty's
    subproblems is smaller than its parent instead of the same size.
    """
    fixed = {matrix.row_of[s]: matrix.column_of[t] for s, t in required}
    rows = [r for r in range(len(matrix.student_ids)) if r not in fixed]
    taken = set(fixed.values())
    columns = [c for c in range(len(matrix.slot_ids)) if c not in taken]
    sub_row = {r: i for i, r in enumerate(rows)}
    sub_column = {c: j for j, c in enumerate(columns)}

    costs = matrix.costs[np.ix_(rows, columns)]
    for s, t in forbidden:
        # A forbidden edge whose row or column is fixed is already excluded.
        i, j = sub_row.get(matrix.row_of[s]), sub_column.get(matrix.column_of[t])
        if i is not None and j is not None:
            costs[i, j] = INFEASIBLE

    try:
        picked_rows, picked_columns = linear_sum_assignment(costs)
    except ValueError as exc:
        raise NoFeasibleAssignment("hard constraints cannot all be met") from exc

    pairs = fixed | {rows[i]: columns[j] for i, j in zip(picked_rows, picked_columns)}
    total = float(sum(matrix.costs[r, c] for r, c in pairs.items()))
    if not np.isfinite(total):
        raise NoFeasibleAssignment("hard constraints cannot all be met")

    return Assignment(
        slot_by_student={matrix.student_ids[r]: matrix.slot_ids[c] for r, c in pairs.items()},
        cost=total,
    )
