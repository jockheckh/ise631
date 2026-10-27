"""Create a reproducibility manifest for one experiment run; never store credentials."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def version(pkg):
    try: return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError: return None


def git_rev():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def files_hash(root):
    h=hashlib.sha256()
    files=sorted(p for p in root.rglob('*.py') if p.is_file())
    for p in files:
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def make_manifest(experiment, seed):
    return {'experiment':experiment,'seed':seed,'created_utc':datetime.now(timezone.utc).isoformat(),
            'python':sys.version.split()[0],'os':platform.platform(), 'git_commit':git_rev(),
            'research_python_sha256':files_hash(ROOT/'src'),
            'packages':{name:version(name) for name in ('gurobipy','numpy','scipy','pandas','pytest')},
            'model_definition':'RECORD IN EXPERIMENT CONFIG',
            'solver_settings':'RECORD SOLVER PARAMS AND TERMINATION STATUS',
            'input_data_hashes':'RECORD HASHES OF NONSECRET INPUTS',
            'paper_table_id':'IF THIS CLAIMS PUBLISHED REPLICATION, RECORD ID'}

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--experiment',required=True)
    ap.add_argument('--seed',required=True,type=int)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise SystemExit(f'Refusing to overwrite existing manifest: {args.output}')
    args.output.write_text(json.dumps(make_manifest(args.experiment,args.seed), indent=2) + chr(10))
    print(args.output)
