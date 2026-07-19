from __future__ import annotations

import os
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


def normalize_text(value: object) -> str:
    return str(value or "").strip()


def is_non_interactive() -> bool:
    return (not sys.stdin.isatty()) or bool(os.getenv("RENDER")) or bool(os.getenv("CI"))


def get_git_config(repo_dir: Path, key: str) -> str:
    result = run_git_command(repo_dir, "config", "--get", key, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_last_commit_author(repo_dir: Path) -> tuple[str, str]:
    result = run_git_command(repo_dir, "log", "-1", "--format=%an%n%ae", check=False)
    if result.returncode != 0:
        return "", ""

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return "", ""

    return lines[0], lines[1]


def prompt_with_default(label: str, default_value: str) -> str:
    suffix = f" [{default_value}]" if default_value else ""
    try:
        value = input(f"{label}{suffix}: ").strip()
    except EOFError:
        return default_value

    return value or default_value


def ensure_git_identity(repo_dir: Path) -> bool:
    current_name = get_git_config(repo_dir, "user.name")
    current_email = get_git_config(repo_dir, "user.email")
    if current_name and current_email:
        return True

    env_name = normalize_text(os.getenv("GIT_AUTHOR_NAME")) or normalize_text(os.getenv("GITHUB_ACTOR"))
    env_email = normalize_text(os.getenv("GIT_AUTHOR_EMAIL"))
    if env_name and env_email:
        run_git_command(repo_dir, "config", "user.name", env_name)
        run_git_command(repo_dir, "config", "user.email", env_email)
        print(f"Identidad Git configurada desde entorno: {env_name} <{env_email}>\n")
        return True

    default_name, default_email = get_last_commit_author(repo_dir)

    if is_non_interactive():
        auto_name = current_name or default_name or env_name or "Catalogo Bot"
        auto_email = current_email or default_email or env_email or "catalogo-bot@local"
        run_git_command(repo_dir, "config", "user.name", auto_name)
        run_git_command(repo_dir, "config", "user.email", auto_email)
        print(f"Identidad Git configurada automaticamente: {auto_name} <{auto_email}>\n")
        return True

    print("Git no tiene configurados user.name y user.email para esta laptop o este repositorio.")
    if default_name and default_email:
        print(f"Se usara como sugerencia el ultimo autor del repositorio: {default_name} <{default_email}>")
    print("Ingresa los datos para configurar Git solo en este repositorio.\n")

    name = prompt_with_default("Nombre", current_name or default_name)
    email = prompt_with_default("Email", current_email or default_email)

    if not name or not email:
        print("No se pudo configurar la identidad de Git. Ejecuta git config y vuelve a intentar.")
        return False

    run_git_command(repo_dir, "config", "user.name", name)
    run_git_command(repo_dir, "config", "user.email", email)

    print(f"Identidad Git configurada para este repositorio: {name} <{email}>\n")
    return True


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
    return normalize_text(os.getenv("GIT_BRANCH")) or branch or "main"


def infer_repo_slug_from_origin(repo_dir: Path) -> str:
    result = run_git_command(repo_dir, "remote", "get-url", "origin", check=False)
    if result.returncode != 0:
        return ""

    remote = result.stdout.strip()
    if remote.startswith("git@github.com:"):
        slug = remote.split("git@github.com:", 1)[1]
    elif "github.com/" in remote:
        slug = remote.split("github.com/", 1)[1]
    else:
        return ""

    if slug.endswith(".git"):
        slug = slug[:-4]
    return slug.strip("/")


def push_changes(repo_dir: Path, branch: str) -> subprocess.CompletedProcess[str]:
    token = normalize_text(os.getenv("GITHUB_TOKEN")) or normalize_text(os.getenv("GH_TOKEN"))
    if not token:
        return run_git_command(repo_dir, "push", "origin", branch)

    repo_slug = normalize_text(os.getenv("GITHUB_REPO")) or infer_repo_slug_from_origin(repo_dir)
    if not repo_slug:
        raise RuntimeError("No se encontro GITHUB_REPO ni se pudo inferir origin para push con token.")

    auth_remote = f"https://x-access-token:{token}@github.com/{repo_slug}.git"
    return run_git_command(repo_dir, "push", auth_remote, f"HEAD:{branch}")


def main() -> int:
    repo_dir = Path(__file__).resolve().parent

    try:
        run_git_command(repo_dir, "rev-parse", "--is-inside-work-tree")
    except subprocess.CalledProcessError:
        print("Este directorio no es un repositorio Git.")
        print("En Render, el deploy automatico por Git requiere que el runtime tenga repo Git y credenciales.")
        print("Configura GITHUB_TOKEN y GITHUB_REPO o usa auto-deploy desde Dashboard.")
        return 1

    entries = get_changed_entries(repo_dir)
    if not entries:
        print("No hay cambios para guardar y desplegar.")
        return 0

    if not ensure_git_identity(repo_dir):
        return 1

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
        commit_result = run_git_command(repo_dir, "commit", "-m", commit_message, check=False)
        if commit_result.returncode != 0:
            commit_out = f"{commit_result.stdout}\n{commit_result.stderr}".lower()
            if "nothing to commit" not in commit_out and "no changes added" not in commit_out:
                if commit_result.stdout:
                    print(commit_result.stdout.strip())
                if commit_result.stderr:
                    print(commit_result.stderr.strip())
                return commit_result.returncode or 1
            print("No hubo cambios nuevos para commit despues de sincronizar archivos.")

        push_result = push_changes(repo_dir, branch)
        if push_result.stdout:
            print(push_result.stdout.strip())
        if push_result.stderr:
            print(push_result.stderr.strip())
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout.strip())
        if exc.stderr:
            print(exc.stderr.strip())
        return exc.returncode or 1
    except RuntimeError as exc:
        print(str(exc))
        return 1

    print("Cambios guardados y enviados correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())