def test_list_sightings_empty(client):
    response = client.get("/api/v1/sightings")

    assert response.status_code == 200
    assert response.json() == []


def test_create_sighting(client):
    payload = {
        "species": "Mediterranean monk seal",
        "latitude": 37.75,
        "longitude": 26.98,
        "observed_at": "2026-10-01T15:30:00Z",
        "photo_url": "https://example.com/monk-seal.jpg",
        "notes": "Observed swimming near the coastline.",
    }

    response = client.post("/api/v1/sightings", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["species"] == "Mediterranean monk seal"
    assert data["latitude"] == 37.75
    assert data["longitude"] == 26.98
    assert data["observed_at"] == "2026-10-01T15:30:00Z"
    assert data["photo_url"] == "https://example.com/monk-seal.jpg"
    assert data["notes"] == "Observed swimming near the coastline."

    assert "id" in data
    assert "created_at" in data

def test_get_sighting_by_id(client):
    payload = {
        "species": "European hedgehog",
        "latitude": 37.98,
        "longitude": 23.72,
        "observed_at": "2026-10-02T20:00:00Z",
        "photo_url": "https://example.com/hedgehog.jpg",
        "notes": "Observed near a garden.",
    }

    create_response = client.post(
        "/api/v1/sightings",
        json=payload,
    )

    assert create_response.status_code == 201

    sighting_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/sightings/{sighting_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sighting_id
    assert data["species"] == "European hedgehog"
    assert data["latitude"] == 37.98
    assert data["longitude"] == 23.72


def test_get_nonexistent_sighting(client):
    response = client.get("/api/v1/sightings/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Sighting not found"
    }

def test_invalid_latitude(client):
    payload = {
        "species": "European hedgehog",
        "latitude": 95.0,  # invalid: must be <= 90
        "longitude": 23.72,
        "observed_at": "2026-10-02T20:00:00Z",
        "photo_url": "https://example.com/hedgehog.jpg",
        "notes": "Test sighting.",
    }

    response = client.post("/api/v1/sightings", json=payload)

    assert response.status_code == 422


def test_missing_observed_at(client):
    payload = {
        "species": "European hedgehog",
        "latitude": 37.98,
        "longitude": 23.72,
        "photo_url": "https://example.com/hedgehog.jpg",
        "notes": "Test sighting.",
    }

    response = client.post("/api/v1/sightings", json=payload)

    assert response.status_code == 422


def test_invalid_photo_url(client):
    payload = {
        "species": "European hedgehog",
        "latitude": 37.98,
        "longitude": 23.72,
        "observed_at": "2026-10-02T20:00:00Z",
        "photo_url": "this-is-not-a-url",
        "notes": "Test sighting.",
    }

    response = client.post("/api/v1/sightings", json=payload)

    assert response.status_code == 422

def test_healthz(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}