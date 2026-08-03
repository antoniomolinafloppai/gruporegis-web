#!/usr/bin/env python3
"""
Descarga imágenes de un sitio web (p. ej. menhirrecycling.com).

Extrae URLs de:
  - etiquetas <img> (src, srcset, data-src)
  - CSS inline (background-image)
  - JSON embebido en el HTML (galerías Webnode/Wizard)

Uso:
  python scrape_images.py
  python scrape_images.py --url https://www.menhirrecycling.com/ --output scraped-images
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".bmp")
RESIZE_SEGMENT = re.compile(r"/(?:450|700)/")


def fetch_url(url: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    data = fetch_url(url, timeout=timeout)
    charset = "utf-8"
    return data.decode(charset, errors="replace")


def is_image_url(url: str) -> bool:
    path = urllib.parse.urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in IMAGE_EXTENSIONS)


def clean_raw_url(raw_url: str) -> str:
    raw_url = html.unescape(raw_url.strip().strip("\"'"))
    # Cortar basura JSON/HTML escapado pegada a la URL
    raw_url = re.split(r'["\'\\<>]', raw_url, maxsplit=1)[0]
    return raw_url.split()[0] if raw_url else ""


def normalize_url(base_url: str, raw_url: str) -> str | None:
    raw_url = clean_raw_url(raw_url)
    if not raw_url or raw_url.startswith("data:"):
        return None
    if len(raw_url) > 512:
        return None

    absolute = urllib.parse.urljoin(base_url, raw_url)
    parsed = urllib.parse.urlparse(absolute)
    if parsed.scheme not in ("http", "https"):
        return None
    if not parsed.netloc or not is_image_url(absolute):
        return None

    return absolute


def extract_from_srcset(value: str) -> list[str]:
    urls: list[str] = []
    for part in value.split(","):
        token = part.strip().split()[0] if part.strip() else ""
        if token:
            urls.append(token)
    return urls


def extract_image_urls(page_url: str, page_html: str) -> set[str]:
    found: set[str] = set()
    decoded_html = html.unescape(page_html)

    tag_patterns = [
        r"<img[^>]+(?:src|data-src)=['\"]([^'\"]+)['\"]",
        r"<img[^>]+srcset=['\"]([^'\"]+)['\"]",
        r"<source[^>]+srcset=['\"]([^'\"]+)['\"]",
        r"background-image\s*:\s*url\(\s*['\"]?([^'\"\)]+)['\"]?\s*\)",
    ]

    json_patterns = [
        r'"src"\s*:\s*"(https?://[^"\\]+)"',
        r'&quot;src&quot;\s*:\s*&quot;(https?://[^&]+?)&quot;',
    ]

    for pattern in tag_patterns:
        for match in re.finditer(pattern, decoded_html, flags=re.IGNORECASE):
            value = match.group(1)
            candidates = extract_from_srcset(value) if "srcset" in pattern else [value]
            for candidate in candidates:
                normalized = normalize_url(page_url, candidate)
                if normalized:
                    found.add(normalized)

    for pattern in json_patterns:
        for match in re.finditer(pattern, decoded_html, flags=re.IGNORECASE):
            normalized = normalize_url(page_url, match.group(1))
            if normalized:
                found.add(normalized)

    return found


def image_identity(url: str) -> str:
    """Agrupa variantes (450w, 700w, webp) de la misma imagen."""
    parsed = urllib.parse.urlparse(url)
    filename = Path(urllib.parse.unquote(parsed.path)).name
    stem = Path(filename).stem.lower()
    return f"{parsed.netloc}:{stem}"


def image_quality_score(url: str) -> tuple[int, int, int]:
    """Mayor puntuación = mejor candidato para descargar."""
    path = urllib.parse.urlparse(url).path.lower()
    penalty_resize = 1 if RESIZE_SEGMENT.search(path) else 0
    penalty_webp = 1 if path.endswith(".webp") else 0
    penalty_svg = 1 if path.endswith(".svg") else 0
    # Preferir PNG/JPEG completos
    bonus = 0
    if path.endswith((".jpg", ".jpeg", ".png")):
        bonus = 1
    length = len(path)
    return (bonus, -penalty_resize, -penalty_webp, -penalty_svg, length)


def select_best_urls(urls: set[str], skip_favicons: bool) -> list[str]:
    grouped: dict[str, list[str]] = {}
    for url in urls:
        if skip_favicons and "favicon" in url.lower():
            continue
        key = image_identity(url)
        grouped.setdefault(key, []).append(url)

    selected: list[str] = []
    for group_urls in grouped.values():
        best = max(group_urls, key=image_quality_score)
        selected.append(best)

    return sorted(selected)


def safe_filename(url: str, index: int) -> str:
    parsed = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parsed.path)).name
    if not name or name in (".", ".."):
        name = f"image_{index}"

    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    if "?" in name:
        name = name.split("?", 1)[0]

    stem = Path(name).stem[:80] or f"image_{index}"
    suffix = Path(name).suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        suffix = ".jpg"

    return f"{index:03d}_{stem}{suffix}"


def download_images(urls: list[str], output_dir: Path, delay: float) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    for index, url in enumerate(urls, start=1):
        filename = safe_filename(url, index)
        destination = output_dir / filename

        try:
            data = fetch_url(url)
            destination.write_bytes(data)
            entry = {
                "file": filename,
                "url": url,
                "bytes": len(data),
                "status": "ok",
            }
            print(f"[{index}/{len(urls)}] OK  {filename} ({len(data):,} bytes)")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            entry = {
                "file": filename,
                "url": url,
                "bytes": 0,
                "status": "error",
                "error": str(exc),
            }
            print(f"[{index}/{len(urls)}] ERR {filename}: {exc}", file=sys.stderr)

        manifest.append(entry)
        if delay > 0 and index < len(urls):
            time.sleep(delay)

    return manifest


def save_manifest(manifest: list[dict], output_dir: Path) -> None:
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nManifiesto guardado en: {manifest_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descarga imágenes de un sitio web."
    )
    parser.add_argument(
        "--url",
        default="https://www.menhirrecycling.com/",
        help="URL de la página a analizar (por defecto: menhirrecycling.com)",
    )
    parser.add_argument(
        "--output",
        default="scraped-images",
        help="Carpeta de destino (por defecto: scraped-images)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Segundos entre descargas (por defecto: 0.3)",
    )
    parser.add_argument(
        "--include-favicons",
        action="store_true",
        help="Incluir favicons del sitio",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo listar URLs sin descargar",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    page_url = args.url.rstrip("/") + "/" if not args.url.endswith("/") else args.url
    output_dir = Path(args.output)

    print(f"Analizando: {page_url}")
    try:
        page_html = fetch_text(page_url)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"No se pudo acceder al sitio: {exc}", file=sys.stderr)
        return 1

    raw_urls = extract_image_urls(page_url, page_html)
    selected_urls = select_best_urls(raw_urls, skip_favicons=not args.include_favicons)

    print(f"URLs encontradas: {len(raw_urls)}")
    print(f"Imágenes únicas a descargar: {len(selected_urls)}")

    if args.dry_run:
        for url in selected_urls:
            print(url)
        return 0

    if not selected_urls:
        print("No se encontraron imágenes.")
        return 0

    manifest = download_images(selected_urls, output_dir, delay=args.delay)
    save_manifest(manifest, output_dir)

    ok = sum(1 for item in manifest if item["status"] == "ok")
    print(f"\nDescarga completada: {ok}/{len(manifest)} imágenes en {output_dir.resolve()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
