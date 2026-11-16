"""Download bounded, catalogued source files without overwriting raw data."""

import argparse
import ssl
import shutil
import urllib.request
from pathlib import Path

import certifi

from .dataset_catalog import get_dataset
from .metadata import write_acquisition_metadata


def download_dataset(
    dataset_id: str,
    raw_dir: Path,
    metadata_dir: Path,
    max_bytes: int = 100_000_000,
) -> Path:
    dataset = get_dataset(dataset_id)
    if not dataset.download_url:
        raise ValueError(f"{dataset_id} has no verified direct download URL")

    filename = Path(dataset.download_url.split("?")[0]).name
    destination = raw_dir / filename
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing raw file: {destination}")

    raw_dir.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    if temporary.exists():
        raise FileExistsError(f"Refusing to reuse incomplete download: {temporary}")

    request = urllib.request.Request(dataset.download_url, headers={"User-Agent": "TerraMatch/0.1"})
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(request, context=ssl_context, timeout=60) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                raise ValueError(
                    f"Refusing {dataset_id}: advertised size {content_length} exceeds {max_bytes} bytes"
                )
            with temporary.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
        if temporary.stat().st_size > max_bytes:
            raise ValueError(f"Refusing {dataset_id}: downloaded file exceeds {max_bytes} bytes")
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    write_acquisition_metadata(dataset, destination, metadata_dir, dataset.download_url)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_id", help="ID from dataset_catalog.py")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--metadata-dir", type=Path, default=Path("data/metadata"))
    parser.add_argument("--max-bytes", type=int, default=100_000_000)
    args = parser.parse_args()
    path = download_dataset(args.dataset_id, args.raw_dir, args.metadata_dir, args.max_bytes)
    print(path)


if __name__ == "__main__":
    main()