# Portability

## Philosophy

This repo should not assume it only runs on the original author's machine.

Machine-specific issues are normal in software work. The goal is to:

- detect them early
- report them clearly
- isolate them where possible
- avoid silent environment assumptions

## Current approach

- keep dependencies light
- use `scripts/preflight.py` before pipeline execution
- prefer explicit checks over hidden setup behavior

## Preflight vs setup

Preflight is for checking and reporting.

Setup should only be added when the dependency surface justifies it. Until then, the repo should stay lightweight and transparent.

## Expected evolution

Preflight should be updated whenever the repo gains:

- new command-line dependencies
- new Python package dependencies
- new network services
- new required directories or generated assets
