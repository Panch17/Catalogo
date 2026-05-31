from __future__ import annotations

import subprocess
import sys
from collections import Counter
from pathlib import Path


STATUS_LABELS = {
    "A": "agregado",
    "M": "modificado",
    "D": "eliminado",
    "R": "renombrado",
    "C": "copiado",
    "U": "actualizado",
    "?": "nuevo",
}


def run_git_command(repo_dir: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
    )


def get_changed_entries(repo_dir: Path) -> list[tuple[str, str]]:
    result = run_git_command(repo_dir, "status", "--porcelain")
    entries: list[tuple[str, str]] = []
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        status_code = raw_line[:2]
        path_text = raw_line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]

        normalized_status = next((char for char in status_code if char not in {" ", "?"}), None)
        if normalized_status is None:
            normalized_status = "?" if "?" in status_code else "M"

        entries.append((normalized_status, path_text))

    return entries


def build_commit_message(entries: list[tuple[str, str]]) -> str:
    counts = Counter(status for status, _ in entries)
    summary_parts = []
    for status in ("M", "A", "D", "R", "C", "U", "?"):
        count = counts.get(status)
        if count:
            label = STATUS_LABELS[status]
            if count > 1:
                label = f"{label}s"
            summary_parts.append(f"{count} {label}")

    names = []
    seen = set()
    for _, path_text in entries:
        filename = Path(path_text).name
        if filename not in seen:
            seen.add(filename)
            names.append(filename)
        if len(names) == 3:
            break

    details = ", ".join(names)
    summary = ", ".join(summary_parts)

    if details:
        return f"Actualiza proyecto ({summary}): {details}"
    return f"Actualiza proyecto ({summary})"


def get_current_branch(repo_dir: Path) -> str:
    result = run_git_command(repo_dir, "branch", "--show-current")
    branch = result.stdout.strip()
    return branch or "main"


def main() -> int:
    repo_dir = Path(__file__).resolve().parent

    try:
        run_git_command(repo_dir, "rev-parse", "--is-inside-work-tree")
    except subprocess.CalledProcessError:
        print("Este directorio no es un repositorio Git.")
        return 1

    entries = get_changed_entries(repo_dir)
    if not entries:
        print("No hay cambios para guardar y desplegar.")
        return 0

    commit_message = build_commit_message(entries)
    branch = get_current_branch(repo_dir)

    print("Cambios detectados:")
    for status, path_text in entries:
        print(f"- {STATUS_LABELS.get(status, status)}: {path_text}")

    print(f"\nMensaje de commit: {commit_message}")
    print(f"Rama destino: {branch}\n")

    try:
        run_git_command(repo_dir, "status")
        run_git_command(repo_dir, "add", ".")
        run_git_command(repo_dir, "commit", "-m", commit_message)
        run_git_command(repo_dir, "push", "origin", branch)
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout.strip())
        if exc.stderr:
            print(exc.stderr.strip())
        return exc.returncode or 1

    print("Cambios guardados y enviados correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())