"""Diagnose structural row-rank defects in phase constraint Jacobians.

Purpose: Provide deterministic, row-scale-invariant reports for constraint
Jacobians used to border phase matrices in the equilibrium minimizer.
Created: 2026-10-10.
Authoring agent/model: OpenAI Codex (gpt-5.6-sol).
Rationale: Explain exact structural singularities under opt-in solver debugging
without making scale-sensitive claims about global equilibrium conditioning.
Inputs: A finite two-dimensional constraint Jacobian and ordered row labels.
Outputs: An immutable rank-deficiency report or ``None``; no side effects.
"""

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np


__all__ = ["ConstraintRankDeficiency", "analyze_constraint_jacobian"]


@dataclass(frozen=True)
class ConstraintRankDeficiency:
    """Row-rank deficiency in a row-normalized constraint Jacobian."""

    rank: int
    num_rows: int
    row_labels: tuple[str, ...]

    def format(self, title: str) -> str:
        """Render the bounded diagnostic contract for solver debug output."""
        labels = ", ".join(self.row_labels)
        return (
            f"!! RANK DEFICIENT CONSTRAINT JACOBIAN {title} "
            f"rank={self.rank}/{self.num_rows}\n"
            f"   row-normalized numerical rank; rows=[{labels}]"
        )


def analyze_constraint_jacobian(
    jacobian: np.ndarray,
    row_labels: Sequence[str],
) -> Optional[ConstraintRankDeficiency]:
    """Return a report when ``jacobian`` does not have full row rank.

    Each nonzero row is L2-normalized before singular-value decomposition. This
    removes arbitrary equation scaling while retaining the structural row space.
    The numerical-rank threshold follows NumPy's default matrix-rank convention:
    ``max(shape) * eps * largest_singular_value``.

    Invalid, empty, or non-finite inputs return ``None`` because this function is
    diagnostic-only and must not interrupt the calculation being inspected.
    """
    matrix = np.asarray(jacobian, dtype=np.float64)
    labels = tuple(str(label) for label in row_labels)
    if (
        matrix.ndim != 2
        or matrix.shape[0] == 0
        or matrix.shape[1] == 0
        or len(labels) != matrix.shape[0]
        or not np.all(np.isfinite(matrix))
    ):
        return None

    row_norms = np.linalg.norm(matrix, axis=1)
    normalized = np.zeros_like(matrix)
    np.divide(
        matrix,
        row_norms[:, np.newaxis],
        out=normalized,
        where=row_norms[:, np.newaxis] > 0.0,
    )
    try:
        singular_values = np.linalg.svd(normalized, compute_uv=False)
    except np.linalg.LinAlgError:
        return None

    largest_singular_value = float(singular_values[0])
    if largest_singular_value == 0.0:
        rank = 0
    else:
        tolerance = (
            max(normalized.shape)
            * np.finfo(np.float64).eps
            * largest_singular_value
        )
        rank = int(np.count_nonzero(singular_values > tolerance))
    if rank == matrix.shape[0]:
        return None
    return ConstraintRankDeficiency(
        rank=rank,
        num_rows=matrix.shape[0],
        row_labels=labels,
    )
