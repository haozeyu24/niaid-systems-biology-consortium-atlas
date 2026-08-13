#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ["python3", "scripts/preflight.py"],
    ["python3", "scripts/fetch_program_papers.py"],
    ["python3", "scripts/build_review_queue.py"],
    ["python3", "scripts/classify_current_program_review_queue.py"],
    ["python3", "scripts/fetch_hpmi_papers.py"],
    ["python3", "scripts/build_hpmi_review_queue.py"],
    ["python3", "scripts/classify_hpmi_review_queue.py"],
    ["python3", "scripts/fetch_pi_backlog_papers.py"],
    ["python3", "scripts/build_pi_backlog_review_queue.py"],
    ["python3", "scripts/classify_pi_backlog_review_queue.py"],
    ["python3", "scripts/build_initial_literature_shortlist.py"],
    ["python3", "scripts/build_full_collection_manifest.py"],
    ["python3", "scripts/build_final_corpus_candidates.py"],
    ["python3", "scripts/build_full_text_inventory.py"],
    ["python3", "scripts/download_pmc_oa_full_texts.py"],
    ["python3", "scripts/build_full_text_inventory.py"],
    ["python3", "scripts/build_literature_summary_reports.py"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"+ {' '.join(command)}")
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
