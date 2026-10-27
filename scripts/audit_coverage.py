"""Conservative coverage audit; does not make mathematical correctness claims."""
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED = {'planned', 'in_progress', 'blocked', 'submitted_for_review', 'verified'}


def audit(path=ROOT / 'requirements.csv'):
    rows = list(csv.DictReader(path.open(newline='', encoding='utf-8')))
    issues = []
    keys = [row.get('id','') for row in rows]
    if len(set(keys)) != len(keys): issues.append('duplicate requirement IDs')
    if len(rows) < 14: issues.append('fewer than 14 mapped instructor requirements')
    for row in rows:
        key = row['id']
        if row.get('status') not in ALLOWED:
            issues.append(f'{key}: invalid status {row.get("status")}')
        if not row.get('instructor_requirement') or not row.get('milestone'):
            issues.append(f'{key}: missing requirement text or milestone')
        if row.get('status') == 'verified':
            ev = row.get('evidence_path','')
            if not ev or not (ROOT / ev).is_file():
                issues.append(f'{key}: marked verified but evidence file missing')
            if not row.get('reviewer'):
                issues.append(f'{key}: marked verified without reviewer')
    print(f'Coverage: {len(rows)} mapped; {sum(r["status"] == "verified" for r in rows)} verified; {sum(r["status"] == "blocked" for r in rows)} blocked')
    for issue in issues: print('ERROR:', issue)
    return issues

if __name__ == '__main__':
    sys.exit(bool(audit()))
