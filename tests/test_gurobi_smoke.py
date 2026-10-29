"""An integration smoke test for the selected Windows Python interpreter.

If gurobipy IS installed but its license is unusable this test FAILS by design;
the research should not silently proceed on a broken solver installation.
"""
import pytest


def test_gurobi_can_solve_toy_lp():
    gp = pytest.importorskip('gurobipy')
    with gp.Model('wsl_smoke') as model:
        model.Params.OutputFlag = 0
        x = model.addVar(lb=0, name='x')
        y = model.addVar(lb=0, name='y')
        model.addConstr(x + 2 * y >= 1)
        model.setObjective(x + y, gp.GRB.MINIMIZE)
        model.optimize()
        assert model.Status == gp.GRB.OPTIMAL
        assert model.ObjVal == pytest.approx(0.5, abs=1e-8)
