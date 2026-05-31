import hashlib
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


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
        return 1

    try:
        df = pd.read_excel(excel_path)
    except Exception as exc:
        print(f"Failed to read Excel: {exc}")
        return 1

    if "ImagenURL" not in df.columns:
        print("Column ImagenURL not found in Excel.")
        return 1

    urls = []
    for raw in df["ImagenURL"].fillna("").astype(str).tolist():
        for part in raw.split(";"):
            url = part.strip()
            if url:
                urls.append(url)

    if not urls:
        print("No image URLs found.")
        return 0

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
        return 1

    return 0


def main():
    repo_dir = Path(__file__).resolve().parent
    raise SystemExit(download_images(repo_dir))


if __name__ == "__main__":
    main()