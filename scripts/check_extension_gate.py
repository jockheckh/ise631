"""Fail closed before optional surveillance pricing is allowed."""
import csv
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

def gate():
    issues=[]
    with (ROOT/'requirements.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        if r.get('status')!='verified': issues.append(f"{r.get('id')}: {r.get('status')} != verified")
        if r.get('status')=='verified':
            ev=r.get('evidence_path','')
            if not ev or not (ROOT/ev).is_file(): issues.append(f"{r.get('id')}: evidence file missing")
            if not r.get('reviewer'): issues.append(f"{r.get('id')}: independent reviewer missing")
    if len(rows)<14: issues.append('requirement matrix incomplete')
    dec=(ROOT/'DECISIONS.md').read_text(encoding='utf-8')
    # Require exact standalone flag (not text inside a paragraph).
    if 'EXTENSION_GATE_APPROVED: true' not in [line.strip() for line in dec.splitlines()]:
        issues.append('human has not released extension gate')
    return issues

if __name__=='__main__':
    issues=gate()
    if issues:
        print('BLOCKED: surveillance-pricing extension is not authorized.')
        for item in issues: print(' -',item)
        sys.exit(1)
    print('PASS: checklist satisfied. Reconfirm human authorization and source/data ethics before any data work.')
