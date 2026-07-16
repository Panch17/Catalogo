from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from threading import Lock

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "datos" / "productos.xlsx"
GENERAR_SCRIPT = BASE_DIR / "GenerarCatalogo.py"
DEPLOY_SCRIPT = BASE_DIR / "GuardarYDesplegar.py"

ADMIN_KEY = os.getenv("ADMIN_KEY", "Zombie2")
HOST = os.getenv("ADMIN_HOST", "0.0.0.0")
PORT = int(os.getenv("ADMIN_PORT", "8000"))

lock = Lock()
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Admin-Key"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


EXPECTED_COLUMNS = [
    "Estatus",
    "Nombre",
    "Descripción",
    "Precio",
    "PrecioRebaja",
    "Categoria",
    "ImagenURL",
    "LinkCompra",
    "Caja",
]


def _ensure_excel_exists() -> None:
    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EXCEL_PATH.exists():
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df.to_excel(EXCEL_PATH, index=False)


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if "Descripcion" in df.columns and "Descripción" not in df.columns:
        df = df.rename(columns={"Descripcion": "Descripción"})

    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df["Estatus"] = pd.to_numeric(df["Estatus"], errors="coerce").fillna(1).astype(int)
    return df[EXPECTED_COLUMNS]


def _read_products() -> pd.DataFrame:
    _ensure_excel_exists()
    df = pd.read_excel(EXCEL_PATH)
    return _normalize_df(df)


def _write_products(df: pd.DataFrame) -> None:
    df.to_excel(EXCEL_PATH, index=False)


def _to_payload_rows(df: pd.DataFrame) -> list[dict]:
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "Estatus": int(row.get("Estatus", 1)) if str(row.get("Estatus", "")).strip() else 1,
                "Nombre": str(row.get("Nombre", "") or ""),
                "Descripcion": str(row.get("Descripción", "") or ""),
                "Precio": str(row.get("Precio", "") or ""),
                "PrecioRebaja": str(row.get("PrecioRebaja", "") or ""),
                "Categoria": str(row.get("Categoria", "") or ""),
                "ImagenURL": str(row.get("ImagenURL", "") or ""),
                "LinkCompra": str(row.get("LinkCompra", "") or ""),
                "Caja": str(row.get("Caja", "") or ""),
            }
        )
    return rows


def _from_payload_rows(items: list[dict]) -> pd.DataFrame:
    def parse_status(value: object) -> int:
        if value is None:
            return 1
        text = str(value).strip()
        if text == "":
            return 1
        return 0 if int(float(text)) == 0 else 1

    normalized = []
    for item in items:
        normalized.append(
            {
                "Estatus": parse_status(item.get("Estatus", 1)),
                "Nombre": item.get("Nombre", ""),
                "Descripción": item.get("Descripcion", ""),
                "Precio": item.get("Precio", ""),
                "PrecioRebaja": item.get("PrecioRebaja", ""),
                "Categoria": item.get("Categoria", ""),
                "ImagenURL": item.get("ImagenURL", ""),
                "LinkCompra": item.get("LinkCompra", ""),
                "Caja": item.get("Caja", ""),
            }
        )
    df = pd.DataFrame(normalized)
    return _normalize_df(df)


def _run_python_script(script_path: Path) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["OPEN_BROWSER"] = "0"
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(BASE_DIR),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def _is_authorized(req: request) -> bool:
    provided_key = req.headers.get("X-Admin-Key", "")
    return bool(provided_key) and provided_key == ADMIN_KEY


@app.before_request
def authorize_api() -> tuple | None:
    if request.method == "OPTIONS" and request.path.startswith("/api/"):
        return ("", 204)
    if request.path.startswith("/api/") and not _is_authorized(request):
        return jsonify({"error": "No autorizado"}), 401
    return None


@app.route("/")
def root() -> tuple:
    return send_from_directory(str(BASE_DIR), "index.html")


@app.route("/actualizar.html")
def updater_page() -> tuple:
    return send_from_directory(str(BASE_DIR), "actualizar.html")


@app.route("/api/productos", methods=["GET"])
def get_products() -> tuple:
    with lock:
        df = _read_products()
    return jsonify({"items": _to_payload_rows(df)})


@app.route("/api/productos", methods=["PUT"])
def save_products() -> tuple:
    payload = request.get_json(silent=True) or {}
    items = payload.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "Formato invalido"}), 400

    with lock:
        df = _from_payload_rows(items)
        _write_products(df)

    return jsonify({"message": "Excel actualizado"})


@app.route("/api/productos/<int:index>", methods=["DELETE"])
def disable_product(index: int) -> tuple:
    with lock:
        df = _read_products()
        if index < 0 or index >= len(df.index):
            return jsonify({"error": "Indice fuera de rango"}), 404
        df.at[index, "Estatus"] = 0
        _write_products(df)

    return jsonify({"message": "Producto desactivado"})


def _generate_catalog() -> tuple[int, str, str]:
    code, out, err = _run_python_script(GENERAR_SCRIPT)
    return code, out, err


def _deploy_changes() -> tuple[int, str, str]:
    return _run_python_script(DEPLOY_SCRIPT)


@app.route("/api/generar", methods=["POST"])
def generate_catalog_route() -> tuple:
    code, out, err = _generate_catalog()
    if code != 0:
        return (
            jsonify({"error": "Fallo al generar catalogo", "stdout": out, "stderr": err}),
            500,
        )

    return jsonify({"message": "Catalogo regenerado correctamente", "stdout": out, "stderr": err})


@app.route("/api/implementar", methods=["POST"])
def implement_catalog() -> tuple:
    payload = request.get_json(silent=True) or {}
    deploy = bool(payload.get("deploy", True))

    code, out, err = _generate_catalog()
    if code != 0:
        return (
            jsonify({"error": "Fallo al generar catalogo", "stdout": out, "stderr": err}),
            500,
        )

    message = "Catalogo regenerado correctamente"
    deploy_stdout = ""
    deploy_stderr = ""

    if deploy:
        deploy_code, deploy_stdout, deploy_stderr = _deploy_changes()
        if deploy_code != 0:
            return (
                jsonify(
                    {
                        "error": "Catalogo generado, pero fallo el deploy",
                        "stdout": deploy_stdout,
                        "stderr": deploy_stderr,
                    }
                ),
                500,
            )
        message = "Catalogo regenerado y desplegado correctamente"

    return jsonify(
        {
            "message": message,
            "stdout": out,
            "stderr": err,
            "deploy_stdout": deploy_stdout,
            "deploy_stderr": deploy_stderr,
        }
    )


if __name__ == "__main__":
    print(f"Panel admin en: http://{HOST}:{PORT}/actualizar.html")
    app.run(host=HOST, port=PORT, debug=False)
