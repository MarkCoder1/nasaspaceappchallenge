"""NASA CMR metadata lookup for the selected NASADEM ROI."""

import json
import ssl
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi


CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
COLLECTION_ID = "C2763264762-LPCLOUD"
ROI_BBOX = (-68.0, -24.0, -67.0, -23.0)


def search_nasadem_granules() -> list[dict[str, Any]]:
    params = urlencode({"collection_concept_id": COLLECTION_ID, "bounding_box": ",".join(map(str, ROI_BBOX)), "page_size": 10})
    request = Request(f"{CMR_URL}?{params}", headers={"User-Agent": "TerraTwin/0.1"})
    context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(request, context=context, timeout=30) as response:
        payload = json.load(response)
    granules = []
    for entry in payload.get("feed", {}).get("entry", []):
        data_links = [link["href"] for link in entry.get("links", []) if link.get("rel", "").endswith("/data#")]
        granules.append({
            "granule_id": entry.get("id"),
            "title": entry.get("title"),
            "boxes": entry.get("boxes", []),
            "data_links": data_links,
        })
    return granules


def write_cmr_manifest(output_path: Path) -> dict[str, Any]:
    granules = search_nasadem_granules()
    manifest = {
        "collection_id": COLLECTION_ID,
        "roi_bbox_west_south_east_north": ROI_BBOX,
        "granules": granules,
        "access": "Protected LP DAAC distribution; Earthdata authentication required",
    }
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest