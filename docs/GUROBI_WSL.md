# Gurobi on Linux/WSL — field setup

**Important:** having Gurobi installed or licensed on Windows does not establish that `gurobipy` and its license work from WSL. Test from the very Python interpreter used by Codex.

## Preparation
1. On WSL Ubuntu, keep the repository under `~/projects/` (Linux filesystem) rather than `/mnt/c/` for better tool/IO behavior.
2. Install Python and virtual environment support; create `.venv` in the project root. Run `python -m pip install -r requirements-dev.txt` from the venv.
3. Obtain and configure a legally authorized **Linux-usable** license through Gurobi's instructions. Check default Linux locations or set `GRB_LICENSE_FILE` to an absolute WSL path **outside this repository**. Never print, paste or commit license contents.
4. WLS licenses may need network access to acquire a token. Project Codex sandbox denies network by default; obtain permission for any needed access, keeping license secrets outside Codex project files.
5. Run `python scripts/preflight.py`. The script creates a toy LP through Gurobi and reports import status versus actual optimization status. On failure, stop before any analytical experiments.

## Suggested commands (inside WSL)
```bash
sudo apt-get update && sudo apt-get install -y python3 python3-venv unzip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python scripts/preflight.py
python -m pytest -q
```

Do not assume an unrestricted academic license from a successful tiny LP; document whether your license permits the intended model sizes. For reproducibility, collect Gurobi version, configuration/parameter values, solver status, LP infeasibility metrics and runtime in each experiment manifest.

Gurobi license help: https://support.gurobi.com/hc/en-us/articles/12684663118993-How-do-I-obtain-a-Gurobi-license
WLS setup: https://support.gurobi.com/hc/en-us/articles/13232844297489-How-do-I-set-up-a-Web-License-Service-WLS-license
