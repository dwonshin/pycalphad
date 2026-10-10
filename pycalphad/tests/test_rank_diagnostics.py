"""Tests for opt-in solver rank diagnostics.

Purpose: Verify deterministic constraint-Jacobian rank reports and their
solver debugging integration.
Created: 2026-10-10.
Authoring agent/model: OpenAI Codex (gpt-5.6-sol).
Rationale: Make structurally singular phase constraints explainable without
adding scale-sensitive claims to the normal solve path.
Inputs: Synthetic matrices, an inline unary database, and a charged Ti-O test
fixture.
Outputs: Pytest pass/fail results and captured diagnostic text; no persistent
side effects.
"""

import warnings

import numpy as np
import pytest

from pycalphad import Database, Workspace, variables as v
from pycalphad.core.rank_diagnostics import (
    ConstraintRankDeficiency,
    analyze_constraint_jacobian,
)
from pycalphad.core.solver import Solver
from pycalphad.tests.fixtures import load_database, select_database


RANK_DIAGNOSTIC_PREFIX = "!! RANK DEFICIENT CONSTRAINT JACOBIAN"


@pytest.mark.parametrize("row_scale", [1.0, 1e-100, 1e100])
def test_constraint_rank_report_is_invariant_to_row_scale(row_scale):
    jacobian = np.array(
        [
            [1.0, 2.0, -3.0],
            [7.0 * row_scale, 14.0 * row_scale, -21.0 * row_scale],
        ]
    )
    labels = ("internal_cons[0]", "phase_local_cons[0]")

    report = analyze_constraint_jacobian(jacobian, labels)

    assert isinstance(report, ConstraintRankDeficiency)
    assert report.rank == 1
    assert report.num_rows == 2
    assert report.row_labels == labels
    assert report.format("phase=PURE:cs0") == (
        "!! RANK DEFICIENT CONSTRAINT JACOBIAN phase=PURE:cs0 rank=1/2\n"
        "   row-normalized numerical rank; rows=[internal_cons[0], "
        "phase_local_cons[0]]"
    )


@pytest.mark.parametrize("row_scale", [1e-200, 1e-100, 1.0, 1e100, 1e200])
def test_constraint_rank_report_ignores_scaled_full_row_rank_without_warning(
    row_scale,
):
    labels = ("internal_cons[0]", "internal_cons[1]")

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        report = analyze_constraint_jacobian(
            np.diag([1.0, row_scale]), labels
        )

    assert report is None


def test_constraint_rank_report_ignores_nonfinite_input():
    labels = ("internal_cons[0]", "internal_cons[1]")

    assert analyze_constraint_jacobian(
        np.array([[1.0, 0.0], [np.nan, 1.0]]), labels
    ) is None


def test_constraint_rank_report_handles_zero_constraint_row():
    labels = ("internal_cons[0]", "internal_cons[1]")

    report = analyze_constraint_jacobian(np.array([[1.0], [0.0]]), labels)

    assert isinstance(report, ConstraintRankDeficiency)
    assert report.rank == 1
    assert report.num_rows == 2


def test_solver_debugging_reports_duplicate_phase_local_constraint(capsys):
    database = Database(
        """
ELEMENT AL FCC_A1 26.9815 0 0 !
TYPE_DEFINITION % SEQ * !
PHASE PURE % 1 1 !
CONSTITUENT PURE : AL : !
PARAMETER G(PURE,AL;0) 298.15 0; 6000 N !
"""
    )
    workspace = Workspace(
        database=database,
        components=["AL"],
        phases=["PURE"],
        conditions={
            v.N: 1,
            v.P: 1e5,
            v.T: 700.0,
            v.Y("PURE", 0, "AL"): 1.0,
        },
        solver=Solver(
            debugging_output=True,
            max_iterations=1,
            remove_metastable=False,
        ),
    )

    workspace.get("GM")
    output = capsys.readouterr().out

    assert (
        f"{RANK_DIAGNOSTIC_PREFIX} phase=PURE:cs0 rank=1/2" in output
    )
    assert (
        "rows=[internal_cons[0], phase_local_cons[0]]" in output
    )


@pytest.mark.solver
@select_database("TiO-17Yan.tdb")
def test_solver_debugging_does_not_report_healthy_charged_constraints(
    load_database, capsys
):
    workspace = Workspace(
        database=load_database(),
        components=["TI", "O", "VA"],
        phases=["TI3O2", "TIO_ALPHA"],
        conditions={v.N: 1, v.P: 1e5, v.T: 620.0, v.X("O"): 0.41},
        solver=Solver(debugging_output=True, max_iterations=1),
    )

    workspace.get("GM")
    output = capsys.readouterr().out

    assert RANK_DIAGNOSTIC_PREFIX not in output
