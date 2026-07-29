#!/usr/bin/env bash
# Format + check the whole project in one go.
#   ./scripts/format.sh              # format + check, stop on error
#   ./scripts/format.sh --check      # CI mode: never rewrites hand-written source
#
# --check is non-mutating for everything you author. The one exception is step 1:
# generate_stubs.py has no --check mode, so it always rewrites its three outputs.
# Those are git-tracked, so instead of suppressing the write we diff the result
# against HEAD and fail on drift — same guarantee, no generator changes. On a
# clean CI checkout that leaves the tree byte-identical; locally it can leave the
# `# Ref:` header rewritten to wherever your node_modules resolved (see below).
#
# Order matches AGENTS.md "檢查指令" section.

set -euo pipefail

cd "$(dirname "$0")/.."

MODE="${1:-format}"

# The three outputs of generate_stubs.py. All git-tracked, so in --check mode we
# regenerate and let git prove there was no drift — no --check mode needed in the
# 2.5k-line generator.
GENERATED=(src/minethon/bot.pyi src/minethon/_events.py src/minethon/_handlers.py)

# Compare against HEAD, not the index: the question is "do the COMMITTED generated
# files match what the generator produces", so a staged change must not move the
# baseline. (Bare `git diff` is worktree-vs-index.)
#
# `-I` skips hunks whose every changed line matches the regex. The `# Ref:` header
# records where each .d.ts actually resolved, which legitimately differs per
# machine (repo-vendored src/mineflayer/js/node_modules/<pkg>/ vs the venv's
# version-hashed site-packages/javascript/js/node_modules/<pkg>--<hash>/) — see
# _portable_ref in generate_stubs.py. Everything else in the files is compared.
#
# Scope note: this catches a stale COMMIT (generator or .d.ts changed, output not
# regenerated). A hand-edit of a generated file is silently overwritten by step 1
# before the diff runs — that case is check_stubs.py's job (step 6).
echo "[1/6] regenerate stubs…"
uv run python scripts/generate_stubs.py
if [[ "$MODE" == "--check" ]]; then
    if ! git diff --quiet HEAD -I'^# Ref: ' -- "${GENERATED[@]}"; then
        echo "✗ generated files are stale — run ./scripts/format.sh and commit the result:" >&2
        git --no-pager diff --stat HEAD -I'^# Ref: ' -- "${GENERATED[@]}" >&2
        exit 1
    fi
fi

if [[ "$MODE" == "--check" ]]; then
    echo "[2/6] ruff format --check…"
    uv run ruff format --check src scripts tests
else
    echo "[2/6] ruff format…"
    uv run ruff format src scripts tests
fi

# `fix = true` in pyproject.toml means a bare `ruff check` REWRITES files. In
# --check mode that both violates "no writes" and hides real findings: an
# auto-fixed RUF100 reports green, so CI can't prove the commit was lint-clean.
echo "[3/6] ruff check…"
if [[ "$MODE" == "--check" ]]; then
    uv run ruff check --no-fix src scripts tests
else
    uv run ruff check src scripts tests
fi

echo "[4/6] pyright…"
uv run pyright src/

echo "[5/6] pytest (unit)…"
uv run pytest -m "not integration" --tb=short -q

echo "[6/6] check_stubs (TS↔.pyi drift gate)…"
uv run python scripts/check_stubs.py

echo "✓ all green"
