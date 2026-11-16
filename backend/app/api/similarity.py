from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.schemas.similarity import SimilarityCompareRequest, SimilarityResponse, SimilarityStatusResponse
from app.services.similarity import DatasetUnavailableError, compare_dataset_ids, feature_definitions, methodology, raster_preview_svg, similarity_status, stored_experiment, terrain_grid
from app.services.export import export_csv, export_json, export_pdf

router = APIRouter(prefix="/api/similarity", tags=["similarity"])

@router.get("/status", response_model=SimilarityStatusResponse)
def get_similarity_status() -> SimilarityStatusResponse:
    return SimilarityStatusResponse(**similarity_status())


@router.get("/features")
def get_features() -> list[dict[str, object]]:
    return feature_definitions()


@router.get("/methodology")
def get_methodology() -> dict[str, object]:
    return methodology()


@router.get("/results")
def get_results() -> dict[str, object]:
    experiment = stored_experiment()
    return {
        "results": [experiment["baseline_result"]],
        "experiment": experiment,
        "ranking": [],
        "message": "Moon-Mars experiment data only; no Earth ranking exists.",
    }


@router.get("/sampling-framework")
def get_sampling_framework() -> dict[str, object]:
    """Return the Phase 11 sampling-framework experiment output (real data only).

    Contains within-body, between-body, and overlap-bias comparisons derived
    from the validated Moon and Mars rasters. No Earth data is included.
    """
    from pathlib import Path

    import json

    repository_root = Path(__file__).resolve().parents[3]
    artifact = repository_root / "data/metadata/phase11_sampling_framework.json"
    if not artifact.is_file():
        raise HTTPException(status_code=404, detail="sampling framework artifact not found")
    return json.loads(artifact.read_text(encoding="utf-8"))


@router.get("/raster/{dataset_id}")
def get_raster_preview(dataset_id: str, layer: str = Query(default="elevation")) -> Response:
    try:
        return Response(content=raster_preview_svg(dataset_id, layer=layer), media_type="image/svg+xml")
    except DatasetUnavailableError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/terrain-grid/{dataset_id}")
def get_terrain_grid(
    dataset_id: str,
    layer: str = Query(default="elevation"),
    max_dim: int = Query(default=128, ge=16, le=256),
) -> dict:
    try:
        return terrain_grid(dataset_id, layer=layer, resampling="average", max_dim=max_dim)
    except DatasetUnavailableError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/export/json")
def export_json_endpoint() -> dict[str, object]:
    return export_json()


@router.get("/export/csv")
def export_csv_endpoint() -> Response:
    payload = export_csv()
    return Response(
        content=payload,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="terratwin_export.csv"'},
    )


@router.get("/export/pdf")
def export_pdf_endpoint() -> Response:
    payload = export_pdf()
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="terratwin_research_report.pdf"'},
    )


@router.post("/compare", response_model=SimilarityResponse)
def compare(request: SimilarityCompareRequest) -> SimilarityResponse:
    try:
        return SimilarityResponse(**compare_dataset_ids(request.target_dataset_id, request.candidate_dataset_id, request.weights))
    except DatasetUnavailableError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error