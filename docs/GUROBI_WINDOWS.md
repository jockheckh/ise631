# Gurobi on Windows / PowerShell

Use the Python interpreter that will execute the research scripts. From the
`C:\ISE631` workspace in PowerShell, run:

```powershell
python scripts/preflight.py
python -m pytest -q
```

The preflight reports the interpreter path, Python/Gurobi versions, and the
status/objective of an actual tiny Gurobi LP. A successful import alone is not
evidence of a working license. Do not store or print license credentials.

On 2026-10-28, the restricted `codexsandboxoffline` context could import
Gurobi but could not start a model because the installed license was bound to
the normal Windows user. The same preflight in that normal user context solved
the toy LP with objective 0.5 (Gurobi 13.0.3, Python 3.13.7 at
`C:\Python313\python.exe`). This establishes a working small LP in the
selected runtime, not license sufficiency for the largest proposed models.

Every experiment must record solver version, parameters, status, objective,
best bound when relevant, residuals, runtime, and model dimensions. A license
limit or solver failure is reported, not hidden by silently shrinking the
instance.
