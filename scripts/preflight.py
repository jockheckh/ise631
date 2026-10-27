"""Read-only WSL/Gurobi/source preflight; never prints license contents."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inspect_sources():
    instructor = ROOT / 'sources' / '10_MDPs (1).pdf'
    paper_dir = ROOT / 'sources' / 'adelman'
    files = sorted(p for p in paper_dir.glob('**/*.pdf') if p.is_file())
    return {'instructor_pdf_present': instructor.is_file(),
            'instructor_sha256': sha256(instructor) if instructor.is_file() else None,
            'adelman_pdf_count': len(files),
            'adelman_pdfs': [{'filename': str(p.relative_to(ROOT)), 'sha256': sha256(p)} for p in files],
            'paper_appendices_complete': 'NOT VERIFIED — require manual inventory'}


def check_gurobi():
    res = {'importable': False, 'usable_for_tiny_lp': False, 'license_sufficient_for_research': 'NOT VERIFIED'}
    if importlib.util.find_spec('gurobipy') is None:
        res['error'] = 'gurobipy not installed in this Python interpreter'
        return res
    try:
        import gurobipy as gp
        res['importable'] = True
        res['version'] = '.'.join(map(str, gp.gurobi.version()))
        with gp.Model('preflight') as m:
            m.Params.OutputFlag = 0
            x = m.addVar(lb=0, name='x')
            y = m.addVar(lb=0, name='y')
            m.addConstr(x + 2*y >= 1)
            m.setObjective(x + y, gp.GRB.MINIMIZE)
            m.optimize()
            res['status_code'] = int(m.Status)
            if m.Status == gp.GRB.OPTIMAL and abs(m.ObjVal - 0.5) < 1e-7:
                res['usable_for_tiny_lp'] = True
                res['toy_objective'] = float(m.ObjVal)
            else:
                res['error'] = 'toy solve produced unexpected status/objective'
    except Exception as exc:
        res['error'] = f'{type(exc).__name__}: {str(exc)[:280]}'
    return res


def summary():
    return {'python': sys.version.split()[0], 'python_executable': sys.executable,
            'system': platform.system(), 'is_wsl': ('microsoft' in platform.release().lower()),
            'sources': inspect_sources(), 'gurobi': check_gurobi(),
            'note': 'This is only an environment test, NOT mathematical verification.'}

if __name__ == '__main__':
    print(json.dumps(summary(), indent=2, sort_keys=True))
