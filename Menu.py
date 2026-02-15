import subprocess
from pathlib import Path


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
        elif choice == "0":
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
