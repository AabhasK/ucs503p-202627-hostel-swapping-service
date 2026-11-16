# Week 6 : The setup steps failed on a fresh clone

## Problem

After fixing CI for the `pyproject.toml` move, I followed our own README
from scratch: clone, new virtual environment, install. The install
failed straight away:

```text
pip install -e ".[dev]"
ERROR: file:///.../c does not appear to be a Python project:
neither 'setup.py' nor 'pyproject.toml' found.
```

The docs site had the same command under "Running it".

## Cause

When I fixed CI, I only changed the workflow. The same command was
written in two more places that nobody runs automatically:

```text
.github/workflows/tests.yml   pip install -e "./code[dev]"   <- fixed
README.md                     pip install -e ".[dev]"        <- stale
docs/index.md                 pip install -e ".[dev]"        <- stale
```

None of us noticed, because everyone in the team already had the
package installed in an old environment. `pytest -q` kept passing on
every laptop, while a new teammate or the evaluator would fail at the
first step.

## Fix

The same one-line change in both files:

```shell
pip install -e "./code[dev]"
```

While updating the docs home page I also listed all three members, added
a short status section, the frontend dev-server steps, and links to each
member's journal.

## Proof

On a fresh clone in a temporary folder:

```text
pip install -e ".[dev]"         -> ERROR, no pyproject.toml found
pip install -e "./code[dev]"    -> installs
pytest -q                       -> 137 passed
```

The docs site also builds with no warnings. My first link to the
journals pointed at `journals/`, which has no index page and would have
been a 404, so each member's journal is now linked directly.

## What I learned

Setup instructions are code that is never tested. The only real check
is the one a new person does: clone into an empty folder and follow
the steps exactly. After any move of `pyproject.toml`, I now search the
whole repo for the old command, not just the file that failed.
