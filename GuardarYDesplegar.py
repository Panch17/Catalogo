from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


STATUS_LABELS = {
    "A": "agregado",
    "M": "modificado",
    "D": "eliminado",
    "R": "renombrado",
    "C": "copiado",
    "U": "actualizado",
    "?": "nuevo",
}

NON_FAST_FORWARD_MARKERS = (
    "fetch first",
    "non-fast-forward",
    "failed to push some refs",
)

REPO_OPERATION_MESSAGES = {
    "rebase-merge": (
        "Hay un rebase en curso.",
        "Termina con 'git rebase --continue' o cancela con 'git rebase --abort' antes de usar esta opcion.",
    ),
    "rebase-apply": (
        "Hay un rebase en curso.",
        "Termina con 'git rebase --continue' o cancela con 'git rebase --abort' antes de usar esta opcion.",
    ),
    "MERGE_HEAD": (
        "Hay un merge en curso.",
        "Resuelve los conflictos y ejecuta 'git commit', o cancela con 'git merge --abort' antes de usar esta opcion.",
    ),
    "CHERRY_PICK_HEAD": (
        "Hay un cherry-pick en curso.",
        "Termina con 'git cherry-pick --continue' o cancela con 'git cherry-pick --abort' antes de usar esta opcion.",
    ),
    "REVERT_HEAD": (
        "Hay un revert en curso.",
        "Termina con 'git revert --continue' o cancela con 'git revert --abort' antes de usar esta opcion.",
    ),
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


def collect_files_for_api_deploy(repo_dir: Path) -> list[Path]:
    default_files = ["datos/productos.xlsx", "index.html"]
    raw = normalize_text(os.getenv("DEPLOY_FILES"))
    values = [item.strip() for item in raw.split(",") if item.strip()] if raw else default_files

    files: list[Path] = []
    for rel in values:
        candidate = (repo_dir / rel).resolve()
        try:
            candidate.relative_to(repo_dir.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            files.append(candidate)
    return files


def github_api_request(
    method: str,
    url: str,
    token: str,
    payload: dict | None = None,
) -> dict:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "catalogo-deploy-script",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urlrequest.Request(url, method=method, headers=headers, data=data)
    try:
        with urlrequest.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urlerror.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            parsed = json.loads(raw)
            message = parsed.get("message") or raw
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"GitHub API {exc.code}: {message}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"No se pudo conectar a GitHub API: {exc.reason}") from exc


def get_remote_file_sha(repo_slug: str, branch: str, rel_path: Path, token: str) -> str:
    encoded_path = urlparse.quote(rel_path.as_posix(), safe="/")
    url = f"https://api.github.com/repos/{repo_slug}/contents/{encoded_path}?ref={urlparse.quote(branch)}"
    try:
        payload = github_api_request("GET", url, token)
    except RuntimeError as exc:
        text = str(exc)
        if "GitHub API 404" in text:
            return ""
        raise
    return str(payload.get("sha") or "")


def push_files_via_github_api(repo_dir: Path, branch: str, commit_message: str) -> None:
    token = normalize_text(os.getenv("GITHUB_TOKEN")) or normalize_text(os.getenv("GH_TOKEN"))
    if not token:
        raise RuntimeError("Falta GITHUB_TOKEN (o GH_TOKEN) para subir cambios a GitHub.")

    repo_slug = normalize_text(os.getenv("GITHUB_REPO")) or infer_repo_slug_from_origin(repo_dir)
    if not repo_slug:
        raise RuntimeError("Falta GITHUB_REPO y no se pudo inferir origin para subir a GitHub.")

    files = collect_files_for_api_deploy(repo_dir)
    if not files:
        raise RuntimeError("No se encontraron archivos a subir. Revisa DEPLOY_FILES o existencia de index.html/datos/productos.xlsx.")

    for absolute_file in files:
        rel_path = absolute_file.relative_to(repo_dir)
        encoded_path = urlparse.quote(rel_path.as_posix(), safe="/")
        url = f"https://api.github.com/repos/{repo_slug}/contents/{encoded_path}"

        content_b64 = base64.b64encode(absolute_file.read_bytes()).decode("ascii")
        sha = get_remote_file_sha(repo_slug, branch, rel_path, token)
        payload = {
            "message": commit_message,
            "content": content_b64,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        github_api_request("PUT", url, token, payload)
        print(f"Subido por API: {rel_path.as_posix()}")


def push_changes(repo_dir: Path, branch: str) -> subprocess.CompletedProcess[str]:
    token = normalize_text(os.getenv("GITHUB_TOKEN")) or normalize_text(os.getenv("GH_TOKEN"))
    if not token:
        return run_git_command(repo_dir, "push", "origin", branch)

    repo_slug = normalize_text(os.getenv("GITHUB_REPO")) or infer_repo_slug_from_origin(repo_dir)
    if not repo_slug:
        raise RuntimeError("No se encontro GITHUB_REPO ni se pudo inferir origin para push con token.")

    auth_remote = f"https://x-access-token:{token}@github.com/{repo_slug}.git"
    return run_git_command(repo_dir, "push", auth_remote, f"HEAD:{branch}")


def get_repo_operation_state(repo_dir: Path) -> tuple[str, str] | None:
    git_dir_result = run_git_command(repo_dir, "rev-parse", "--git-dir", check=False)
    if git_dir_result.returncode != 0:
        return None

    git_dir = (repo_dir / git_dir_result.stdout.strip()).resolve()
    for marker, messages in REPO_OPERATION_MESSAGES.items():
        if (git_dir / marker).exists():
            return messages

    return None


def get_upstream_branch(repo_dir: Path) -> str:
    result = run_git_command(
        repo_dir,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_branch_sync_counts(repo_dir: Path) -> tuple[int, int] | None:
    if not get_upstream_branch(repo_dir):
        return None

    result = run_git_command(repo_dir, "rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    counts = result.stdout.strip().split()
    if len(counts) != 2:
        return None

    behind_count, ahead_count = (int(value) for value in counts)
    return behind_count, ahead_count


def has_staged_changes(repo_dir: Path) -> bool:
    result = run_git_command(repo_dir, "diff", "--cached", "--quiet", check=False)
    return result.returncode == 1


def print_git_failure(error: subprocess.CalledProcessError) -> None:
    if error.stdout:
        print(error.stdout.strip())
    if error.stderr:
        print(error.stderr.strip())


def is_non_fast_forward_error(error: subprocess.CalledProcessError) -> bool:
    combined_output = "\n".join(part for part in (error.stdout, error.stderr) if part).lower()
    return any(marker in combined_output for marker in NON_FAST_FORWARD_MARKERS)


def push_with_rebase_retry(repo_dir: Path, branch: str) -> None:
    upstream_branch = get_upstream_branch(repo_dir)
    push_args = ["push", "origin", branch]
    if not upstream_branch:
        push_args.insert(1, "-u")

    try:
        run_git_command(repo_dir, *push_args)
        return
    except subprocess.CalledProcessError as error:
        if not is_non_fast_forward_error(error):
            raise

        print("El remoto tiene cambios nuevos. Intentando sincronizar con git pull --rebase...")

    try:
        run_git_command(repo_dir, "pull", "--rebase", "origin", branch)
    except subprocess.CalledProcessError as error:
        print_git_failure(error)
        print(
            "No se pudo sincronizar automaticamente. Resuelve el rebase manualmente y vuelve a intentar."
        )
        raise

    run_git_command(repo_dir, *push_args)


def main() -> int:
    repo_dir = Path(__file__).resolve().parent

    git_check = run_git_command(repo_dir, "rev-parse", "--is-inside-work-tree", check=False)
    git_available = git_check.returncode == 0
    branch = get_current_branch(repo_dir)

    if not git_available:
        print("Runtime sin metadata Git. Se intentara subida por GitHub API.")
        try:
            push_files_via_github_api(
                repo_dir,
                branch,
                f"Actualiza catalogo desde panel ({branch})",
            )
        except RuntimeError as exc:
            print(str(exc))
            return 1

        print("Cambios subidos correctamente por GitHub API.")
        return 0

    repo_operation_state = get_repo_operation_state(repo_dir)
    if repo_operation_state:
        headline, guidance = repo_operation_state
        print(headline)
        print(guidance)
        return 1

    entries = get_changed_entries(repo_dir)
    branch = get_current_branch(repo_dir)
    sync_counts = get_branch_sync_counts(repo_dir)

    if not entries and (sync_counts is None or sync_counts[1] == 0):
        print("No hay cambios para guardar ni commits pendientes para enviar.")
        return 0

    commit_message = build_commit_message(entries) if entries else ""

    if entries:
        if not ensure_git_identity(repo_dir):
            return 1

        print("Cambios detectados:")
        for status, path_text in entries:
            print(f"- {STATUS_LABELS.get(status, status)}: {path_text}")

        print(f"\nMensaje de commit: {commit_message}")
    else:
        print("No hay cambios nuevos en archivos, pero existen commits pendientes por enviar.")

    if sync_counts:
        behind_count, ahead_count = sync_counts
        print(f"Remoto pendiente de integrar: {behind_count}")
        print(f"Commits locales pendientes de enviar: {ahead_count}")

    print(f"Rama destino: {branch}\n")

    try:
        if entries:
            run_git_command(repo_dir, "add", ".")
            if has_staged_changes(repo_dir):
                run_git_command(repo_dir, "commit", "-m", commit_message)

        push_with_rebase_retry(repo_dir, branch)
    except subprocess.CalledProcessError as exc:
        print_git_failure(exc)
        return exc.returncode or 1

    print("Cambios guardados y enviados correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())