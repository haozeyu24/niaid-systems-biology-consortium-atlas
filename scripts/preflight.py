#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = [
    PROJECT_ROOT / "consortium",
    PROJECT_ROOT / "papers" / "sources" / "current-program",
    PROJECT_ROOT / "papers" / "sources" / "pi-backlog",
    PROJECT_ROOT / "papers" / "derived" / "consortium-subset",
    PROJECT_ROOT / "datasets",
    PROJECT_ROOT / "resources",
    PROJECT_ROOT / "pathways",
    PROJECT_ROOT / "schemas",
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT / "workflows",
    PROJECT_ROOT / "outputs",
]
TEST_URLS = [
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed",
    "https://pubmed.ncbi.nlm.nih.gov/",
]


def ok(label: str, detail: str) -> tuple[bool, str]:
    return True, f"[PASS] {label}: {detail}"


def fail(label: str, detail: str) -> tuple[bool, str]:
    return False, f"[FAIL] {label}: {detail}"


def check_python() -> tuple[bool, str]:
    if sys.version_info < (3, 10):
        return fail("python", f"need Python >= 3.10, found {sys.version.split()[0]}")
    return ok("python", sys.version.split()[0])


def check_command(name: str) -> tuple[bool, str]:
    path = shutil.which(name)
    if not path:
        return fail(name, "not found in PATH")
    return ok(name, path)


def check_repo_dirs() -> tuple[bool, str]:
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in REQUIRED_DIRS if not path.exists()]
    if missing:
        return fail("repo-layout", f"missing required paths: {', '.join(missing)}")
    return ok("repo-layout", "required directories present")


def check_writable() -> tuple[bool, str]:
    probe = PROJECT_ROOT / ".preflight-write-test"
    try:
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return fail("write-access", str(exc))
    return ok("write-access", str(PROJECT_ROOT))


def check_curl_fetch(url: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [
                "curl",
                "--silent",
                "--show-error",
                "--fail",
                "--location",
                "--max-time",
                "20",
                "--output",
                os.devnull,
                url,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip() or f"exit code {exc.returncode}"
        return fail("network", f"{url} -> {stderr}")
    return ok("network", url)


def main() -> int:
    checks = [
        check_python(),
        check_command("curl"),
        check_repo_dirs(),
        check_writable(),
    ]
    for url in TEST_URLS:
        checks.append(check_curl_fetch(url))

    failed = False
    print("NIAID Systems Biology Consortium Atlas preflight\n")
    for success, message in checks:
        print(message)
        if not success:
            failed = True

    print()
    if failed:
        print("Preflight failed. Fix the failing checks before running pipeline scripts.")
        return 1

    print("Preflight passed. This machine looks ready for the current lightweight pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
