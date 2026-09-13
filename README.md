# I ❤️ PY

**Jesper Karlsson — Otrobonita AI Labs**

A NiceGUI repo that *proves* it loves Python: live quality telemetry (ruff, mypy
strict, pytest+coverage, radon, bandit, pip-audit), deterministic review personas
on real git diffs, an "ask git" debugging session against this repo's own history,
and a load test whose k6 script is **compiled from a Python dataclass**.

It is also an experiment. If agents work better in a single language than when
task-switching across languages, frameworks and config formats — each one loading
its own rules into the context window — then a deliberately narrow repo should be
measurably easier to work in. That's the hypothesis this repo exists to test, not
a finding it reports.

🎧 **[40-minute podcast walkthrough](http://cdn-media.otrobonita.com/audio/podcasts/i-love-python/i-love-python-podcast.m4a)** — the long-form tour of what this is and why.

See `MANIFEST.md` for the full requirement → file → check map, and `AGENTS.md` for
the rules every contributor (human or agent) must follow.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -e .[dev]
python app.py                   # open http://localhost:8321
```

The landing page renders the I ❤️ PY mark procedurally — a parametric heart curve
drawn by the same codebase you're about to inspect. Five tabs from there:

| Tab | What it does |
|---|---|
| **Quality** | Runs ruff (format + lint), mypy strict, pytest+coverage, radon, bandit, pip-audit and the pure-Python language audit for real, rendering their output live |
| **Review** | Purist / Skeptic / Pragmatist personas issue rule-based verdicts over actual `git diff` output |
| **Git discipline** | An "ask git" console — log, show, blame — against this repo's own history (bisect is a documented gap, not a feature) |
| **Explain** | Plain-language translation of any diff or tool output, alongside the raw version |
| **Load test** | A k6 scenario compiled from a typed Python spec, with a pure-Python VU fallback if k6 isn't installed |

## The pure-Python rule

The rule is, first and foremost, a discipline exercise — a way of holding a single
mental model and a unified toolchain across the entire repo.

It also has a forward-looking angle: if AI orchestration (agent loops, tool
selection, RAG) keeps shifting the center of gravity in web apps from interface to
model infrastructure, that infrastructure already lives in Python. This isn't a
claim that it will happen — just a scenario in which the choice would already turn
out to have been right, rather than a retrofitted justification.

Hand-authored source is Python. Non-Python files only exist when Python generated
them and they carry a `GENERATED` header:

- `generated/k6/load.js` — k6 script compiled from `LoadSpec` (`python -m loadtest.generate`)
- `generated/ci/ci-pipeline.yml` + live `.github/workflows/ci.yml` (`python -m scripts.ci_yaml`)
- `generated/hooks/pre-commit.sh` + live `.git/hooks/pre-commit` (`python -m scripts.install_hooks`)
- `generated/docs/wiring-diagram.html` — open it in a browser for a hand-drawn
  schematic of how the five tabs wire to real tools (`python -m scripts.wiring_diagram`)

`python scripts/lang_audit.py` keeps it honest — it runs in the pre-commit hook and in CI.

So "pure Python" doesn't mean isolated from the rest of the toolchain. It means
Python owns everything, including the things it delegates.

## Reusable parts

This is an experimental project, but several pieces are portable on their own:

- **Live quality telemetry** (`panel/telemetry.py`) — real subprocess calls to ruff, mypy, pytest, radon, bandit and pip-audit, rendered live instead of as static badges. Worth borrowing if you want a quality dashboard for your own repo.
- **Deterministic review personas** (`review/personas.py`) — Purist / Skeptic / Pragmatist verdicts over real `git diff` output. Rule-based, no LLM call. Worth borrowing if you want review automation that's cheap and explainable.
- **Generated-artifact governance** (`scripts/lang_audit.py`) — the CI YAML, the pre-commit hook and the wiring diagram are all compiled from Python, with a script that fails the build if a hand-authored non-Python file sneaks in. A portable technique if config drift is a problem you have.
- **Load spec as a typed dataclass** (`loadtest/spec.py` → `generate.py`) — a k6 script generated from a validated Python object, with a Python VU fallback when k6 isn't installed. Worth it if you want load tests that are type-checked and unit-testable rather than hand-written JS.
- **Onboarding reference** — `MANIFEST.md`, `AGENTS.md` and the wiring diagram together are polished enough to hand to a new hire independently of the app itself.

## Docs

- [spec.md](./docs/spec.md) — full specification: modules, repo structure, open questions, and the specified-but-not-shipped gap list
- [MANIFEST.md](./MANIFEST.md) — application-level intent, per the Otrobonita playbook convention
- [AGENTS.md](./AGENTS.md) — standing instructions for coding agents: git discipline, the pure-Python constraint, architecture
- [llms.txt](./llms.txt) — navigation map for agents reading this repo
- [wiring map](./generated/docs/wiring-diagram.html) — the five tabs wired to their real tools, as generated HTML (open in a browser)

Related: the engineering playbook this repo demonstrates lives at [playbook.otrobonita.com](https://playbook.otrobonita.com).

## Status

Experimental. Version 0.1.0 — see `docs/spec.md` for what's shipped and what's open.
Apache 2.0 licensed (see `LICENSE`); made by Jesper Karlsson with another, much larger AI. 
