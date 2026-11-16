from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_similarity_status_is_honest_about_available_datasets() -> None:
    response = client.get("/api/similarity/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["production_comparisons_enabled"] is False
    assert payload["available_real_datasets"][0]["id"] == "mars_jezero_ctx_dtm"
    assert payload["comparison_capabilities"]["earth_mars"]["enabled"] is False
    assert payload["validated_comparisons"] == ["moon_mars"]


def test_similarity_methodology_and_features_are_exposed() -> None:
    assert client.get("/api/similarity/methodology").json()["name"] == "Terrain Morphology Similarity Index (TMSI)"
    assert {feature["id"] for feature in client.get("/api/similarity/features").json()} == {
        "slope",
        "local_relief",
        "terrain_ruggedness",
    }


def test_unavailable_earth_comparison_is_rejected() -> None:
    response = client.post(
        "/api/similarity/compare",
        json={"target_dataset_id": "mars_jezero_ctx_dtm", "candidate_dataset_id": "earth_nasadem_hgt_v001"},
    )

    assert response.status_code == 409
    assert "unavailable" in response.json()["detail"]


def test_results_endpoint_does_not_fabricate_rankings() -> None:
    response = client.get("/api/similarity/results")

    assert response.status_code == 200
    assert response.json()["ranking"] == []
    assert response.json()["results"][0]["similarity_index"] == 49.92285382858792


def test_raster_preview_uses_validated_dataset() -> None:
    response = client.get("/api/similarity/raster/moon_lola")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "Terrain elevation preview" in response.text


def test_raster_preview_supports_validated_feature_layers() -> None:
    for layer in ("elevation", "hillshade", "slope", "local_relief", "terrain_ruggedness"):
        response = client.get(f"/api/similarity/raster/moon_lola?layer={layer}")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")


def test_raster_preview_rejects_unknown_layer() -> None:
    response = client.get("/api/similarity/raster/moon_lola?layer=bogus")
    assert response.status_code == 409


def test_raster_preview_rejects_unavailable_dataset() -> None:
    response = client.get("/api/similarity/raster/earth_nasadem_hgt_v001")
    assert response.status_code == 409


def test_export_json_returns_real_experiment_package() -> None:
    response = client.get("/api/similarity/export/json")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload["experiment"] == "moon_mars_phase7_validation"
    assert payload["results"]["baseline"]["similarity_index"] == 49.92285382858792
    assert payload["results"]["baseline"]["confidence"] == "HIGH"
    assert {d["id"] for d in payload["datasets"]} == {"mars_jezero_ctx_dtm", "moon_lola"}
    assert payload["unavailable_datasets"][0]["id"] == "earth_nasadem_hgt_v001"
    assert payload["methodology"]["name"] == "Terrain Morphology Similarity Index (TMSI)"
    assert payload["methodology"]["score"] == "100 * exp(-weighted_normalized_distance)"


def test_export_csv_contains_actual_statistics() -> None:
    response = client.get("/api/similarity/export/csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    text = response.text
    assert "similarity_index,49.9229" in text
    assert "local_relief,m,4.5096" in text
    assert "slope,degrees,4.9988" in text
    assert "terrain_ruggedness,m,1.5624" in text
    assert "earth_nasadem_hgt_v001,Earth,PENDING" in text
    assert "NASA Earthdata authentication unavailable" in text


def test_export_pdf_is_valid_research_report() -> None:
    response = client.get("/api/similarity/export/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    body = response.content
    assert body.startswith(b"%PDF")
    assert b"%%EOF" in body
    assert b"Moon" in body and b"Mars" in body
