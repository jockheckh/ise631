from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.preflight import inspect_sources
from scripts.check_extension_gate import gate
from scripts.write_manifest import make_manifest


def test_project_codex_config_and_agent_schema():
    config=tomllib.loads((ROOT/'.codex/config.toml').read_text())
    assert config['agents']['max_concurrent_threads_per_session']==3
    assert config['approval_policy']=='on-request'
    assert config['sandbox_mode']=='workspace-write'
    for agent in (ROOT/'.codex/agents').glob('*.toml'):
        obj=tomllib.loads(agent.read_text())
        assert all(obj.get(k) for k in ('name','description','developer_instructions'))


def test_prompt_pdf_is_present_and_extension_blocked():
    assert inspect_sources()['instructor_pdf_present']
    assert gate(), 'extension must fail closed in starter scaffold'


def test_manifest_has_reproducibility_fields():
    obj=make_manifest('toy',0)
    assert obj['experiment']=='toy'
    assert obj['seed']==0
    assert 'gurobipy' in obj['packages']
    assert obj['research_python_sha256']
