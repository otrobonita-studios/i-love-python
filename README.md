# I ❤️ PY

**Otrobonita AI Labs — Jesper Karlsson**

A NiceGUI demo that *proves* it loves Python: live quality telemetry (ruff, mypy
strict, pytest+coverage, radon, bandit, pip-audit), deterministic review personas
on real git diffs, an "ask git" debugging session against this repo's own history,
and a load test whose k6 script is **compiled from a Python dataclass**.

See `MANIFEST.md` for the full requirement → file → check map, and `AGENTS.md` for
the rules every contributor (human or agent) must follow.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -e .[dev]
python app.py                   # open http://localhost:8321
```

## The pure-Python rule

Hand-authored source is Python. Non-Python files only exist when Python generated
them and they carry a `GENERATED` header: the k6 script, the CI workflow, and the
pre-commit hook. `python scripts/lang_audit.py` keeps it honest.
