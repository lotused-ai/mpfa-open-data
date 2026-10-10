#!/usr/bin/env python3
"""Download the MPFA open-data resources listed in config/datasets.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "datasets.json"
CURRENT_DIR = ROOT / "data" / "current"
DICTIONARY_DIR = ROOT / "data" / "dictionaries"
MANIFEST_PATH = ROOT / "data" / "manifest.json"
USER_AGENT = "mpfa-open-data-github-action/1.0 (+https://github.com/)"


def download(url: str, destination: Path) -> tuple[str, int]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def filename_from_url(url: str) -> str:
    name = url.rstrip("/").rsplit("/", 1)[-1]
    if not name:
        raise ValueError(f"Could not determine filename from {url}")
    return name.split("?", 1)[0]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    args = parser.parse_args()

    config = load_json(args.config)
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "source": config["source"],
        "provider": config["provider"],
        "fetched_at": fetched_at,
        "resources": [],
        "errors": [],
    }

    CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    DICTIONARY_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="mpfa-open-data-", dir=ROOT / "data") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        for dataset in config["datasets"]:
            for resource in dataset["resources"]:
                url = resource["url"]
                filename = filename_from_url(url)
                destination = CURRENT_DIR / dataset["slug"] / resource["language"] / filename
                temporary = temp_dir / filename
                record = {
                    "dataset": dataset["slug"],
                    "title": dataset["title"],
                    "language": resource["language"],
                    "format": resource["format"],
                    "url": url,
                    "path": destination.relative_to(ROOT).as_posix(),
                }
                try:
                    digest, size = download(url, temporary)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if not destination.exists() or not destination.samefile(temporary):
                        shutil.copyfile(temporary, destination)
                    record.update({"status": "ok", "sha256": digest, "bytes": size})
                    print(f"OK   {record['path']} ({size:,} bytes)")
                except (OSError, urllib.error.URLError, ValueError) as exc:
                    record.update({"status": "error", "error": str(exc)})
                    manifest["errors"].append(record)
                    print(f"ERROR {url}: {exc}", file=sys.stderr)
                manifest["resources"].append(record)

            dictionary_url = dataset["dictionary_url"]
            dictionary_name = filename_from_url(dictionary_url)
            dictionary_path = DICTIONARY_DIR / dictionary_name
            temporary = temp_dir / dictionary_name
            record = {
                "dataset": dataset["slug"],
                "title": dataset["title"],
                "format": "pdf",
                "url": dictionary_url,
                "path": dictionary_path.relative_to(ROOT).as_posix(),
            }
            try:
                digest, size = download(dictionary_url, temporary)
                shutil.copyfile(temporary, dictionary_path)
                record.update({"status": "ok", "sha256": digest, "bytes": size})
                print(f"OK   {record['path']} ({size:,} bytes)")
            except (OSError, urllib.error.URLError, ValueError) as exc:
                record.update({"status": "error", "error": str(exc)})
                manifest["errors"].append(record)
                print(f"ERROR {dictionary_url}: {exc}", file=sys.stderr)
            manifest["resources"].append(record)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")
    if manifest["errors"]:
        print(f"Completed with {len(manifest['errors'])} error(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
