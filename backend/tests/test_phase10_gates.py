"""Phase 10 backend tests: Earth PENDING gates and comparison rejection behavior."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_earth_remains_pending_in_status() -> None:
    response = client.get("/api/similarity/status")
    assert response.status_code == 200
    payload = response.json()
    earth = [d for d in payload["unavailable_datasets"] if d["id"] == "earth_nasadem_hgt_v001"]
    assert len(earth) == 1
    assert earth[0]["body"] == "Earth"
    assert "not been acquired and validated" in earth[0]["reason"]
    assert payload["production_comparisons_enabled"] is False
    assert payload["validated_comparisons"] == ["moon_mars"]


def test_earth_comparison_capabilities_are_disabled() -> None:
    response = client.get("/api/similarity/status")
    capabilities = response.json()["comparison_capabilities"]
    assert capabilities["earth_mars"]["enabled"] is False
    assert capabilities["earth_moon"]["enabled"] is False
    assert capabilities["moon_mars"]["enabled"] is True


def test_earth_mars_compare_is_rejected() -> None:
    response = client.post(
        "/api/similarity/compare",
        json={"target_dataset_id": "mars_jezero_ctx_dtm", "candidate_dataset_id": "earth_nasadem_hgt_v001"},
    )
    assert response.status_code == 409
    assert "unavailable" in response.json()["detail"].lower()


def test_earth_moon_compare_is_rejected() -> None:
    response = client.post(
        "/api/similarity/compare",
        json={"target_dataset_id": "moon_lola", "candidate_dataset_id": "earth_nasadem_hgt_v001"},
    )
    assert response.status_code == 409
    assert "unavailable" in response.json()["detail"].lower()


def test_moon_mars_baseline_reproducible() -> None:
    response = client.get("/api/similarity/results")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ranking"] == []
    assert payload["results"][0]["similarity_index"] == 49.92285382858792
    assert payload["results"][0]["confidence"] == "HIGH"
