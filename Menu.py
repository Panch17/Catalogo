import hashlib
import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


def run_command(cmd, cwd):
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
        return True
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return False
    except subprocess.CalledProcessError as exc:
        print(f"Command failed ({exc.returncode}): {' '.join(cmd)}")
        return False


def run_catalog(repo_dir):
    exe_candidates = [
        repo_dir / "GenerarCatalogo.exe",
        repo_dir / "dist" / "GenerarCatalogo.exe",
    ]

    for exe_path in exe_candidates:
        if exe_path.exists():
            print("Running:", exe_path)
            run_command([str(exe_path)], cwd=str(repo_dir))
            return

    print("GenerarCatalogo.exe not found. Compile it first.")


def compile_menu_exe(repo_dir):
    cmd = ["pyinstaller", "--onefile", "Menu.py"]
    print("Running:", " ".join(cmd))
    run_command(cmd, cwd=str(repo_dir))


def get_safe_filename(url):
    parsed = urllib.parse.urlparse(url)
    name = os.path.basename(parsed.path)
    name = urllib.parse.unquote(name)
    if name:
        name = name.replace(" ", "_")
        name = re.sub(r"[<>:\"/\\|?*]", "_", name)
        if len(name) > 120:
            ext = os.path.splitext(name)[1] or ".jpg"
            digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
            return f"img_{digest}{ext}"
        return name

    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return f"img_{digest}.jpg"


def download_images(repo_dir):
    datos_dir = repo_dir / "datos"
    excel_path = datos_dir / "productos.xlsx"
    output_dir = repo_dir / "IMAGENES" / "Descargadas"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not excel_path.exists():
        print(f"Excel not found: {excel_path}")
        return

    try:
        df = pd.read_excel(excel_path)
    except Exception as exc:
        print(f"Failed to read Excel: {exc}")
        return

    if "ImagenURL" not in df.columns:
        print("Column ImagenURL not found in Excel.")
        return

    urls = []
    for raw in df["ImagenURL"].fillna("").astype(str).tolist():
        for part in raw.split(";"):
            url = part.strip()
            if url:
                urls.append(url)

    if not urls:
        print("No image URLs found.")
        return

    print(f"Found {len(urls)} URLs. Downloading...")

    failed = []
    skipped = 0
    total = len(urls)
    log_path = output_dir / "download_log.txt"

    for index, url in enumerate(urls, start=1):
        print(f"[{index}/{total}] {url}")
        parsed = urllib.parse.urlsplit(url)
        safe_path = urllib.parse.quote(parsed.path, safe="/-._~")
        safe_url = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, safe_path, parsed.query, parsed.fragment)
        )
        filename = get_safe_filename(url)
        target = output_dir / filename

        if target.exists():
            skipped += 1
            print(f"Skip (exists): {target.name}")
            continue

        try:
            request = urllib.request.Request(
                safe_url,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=10) as response, open(target, "wb") as out_file:
                out_file.write(response.read())
            print(f"Downloaded: {target.name}")
        except Exception as exc:
            failed.append((url, str(exc)))
            print(f"Failed: {url} -> {exc}")

    if failed:
        with open(log_path, "w", encoding="utf-8") as log_file:
            for url, error in failed:
                log_file.write(f"{url}\t{error}\n")

    print("Done.")
    print(f"Skipped (already existed): {skipped}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"See log: {log_path}")


def push_changes(repo_dir, branch):
    if not run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(repo_dir)):
        print("Not a git repository.")
        return

    run_command(["git", "status", "-s"], cwd=str(repo_dir))
    if not run_command(["git", "add", "."], cwd=str(repo_dir)):
        return

    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(repo_dir),
    )
    if staged.returncode == 0:
        print("No staged changes. Pushing anyway.")
    else:
        message = input("Describe los cambios para el commit: ").strip()
        if not message:
            print("Commit message is required. Aborting.")
            return
        if not run_command(["git", "commit", "-m", message], cwd=str(repo_dir)):
            return

    run_command(["git", "push", "origin", branch], cwd=str(repo_dir))


def main():
    repo_dir = Path(__file__).resolve().parent
    branch = "main"

    while True:
        print("\nSelecciona una opcion:")
        print("1) Generar catalogo")
        print("2) Guardar y desplegar (git add/commit/push)")
        print("3) Compilar Menu.exe")
        print("4) Descargar imagenes")
        print("0) Salir")
        choice = input("Opcion: ").strip()

        if choice == "1":
            run_catalog(repo_dir)
        elif choice == "2":
            branch_input = input(f"Rama destino (Enter = {branch}): ").strip()
            target_branch = branch_input or branch
            push_changes(repo_dir, target_branch)
        elif choice == "3":
            compile_menu_exe(repo_dir)
        elif choice == "4":
            download_images(repo_dir)
        elif choice == "0":
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
