# Week 5 : CI could not install the package any more

## Problem

During the prototype-stage cleanup, `pyproject.toml` and
`requirements.txt` were moved from the repo root into `code/`, next to
the `hostelswap` package. My local environment was already installed,
so nothing looked wrong there. But the tests workflow on GitHub
installs the package fresh on every run, and that install step still
pointed at the old location.

## Cause

Two paths were still written relative to the old location.

The workflow installed from the repo root:

```yaml
- name: Install
  run: pip install -e ".[dev]"
```

But the root no longer had a `pyproject.toml`, so pip had nothing to
install.

Inside `code/pyproject.toml`, the wheel target still pointed at the old
path, and `readme` pointed at a file that is not in `code/`:

```toml
readme = "README.md"

[tool.hatch.build.targets.wheel]
packages = ["code/hostelswap"]
```

Paths in `pyproject.toml` are relative to the file itself, so after the
move `code/hostelswap` meant `code/code/hostelswap`.

## Fix

Point the workflow at the new project folder, and make the package path
relative to where `pyproject.toml` now lives:

```yaml
run: pip install -e "./code[dev]"
```

```toml
[tool.hatch.build.targets.wheel]
packages = ["hostelswap"]
```

The `readme` line was dropped, since the README stays at the repo root.

## Proof

A fresh install from the new path, then the suite:

```text
pip install -e "./code[dev]"
pytest -q
137 passed
```

## What I learned

Moving a config file moves every relative path inside it. When a file
like `pyproject.toml` moves, the paths it names have to move with it,
and the commands that point at it (CI, the README setup steps) have to
be checked in the same commit.
