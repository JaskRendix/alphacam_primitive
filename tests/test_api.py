from fastapi.testclient import TestClient

from alphacam_primitive.api import app

client = TestClient(app)


def sample_paths():
    return [
        {"name": 1, "min_x": 0, "min_y": 0, "max_x": 10, "max_y": 5, "length": 30},
        {"name": 2, "min_x": 20, "min_y": 0, "max_x": 30, "max_y": 5, "length": 30},
    ]


def test_api_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_api_order():
    resp = client.post("/order", json=sample_paths())
    assert resp.status_code == 200
    data = resp.json()
    assert data["ordered_indices"] == [1, 2]


def test_api_inout():
    resp = client.post(
        "/inout",
        json={
            "path": sample_paths()[0],
            "in_dx": 1,
            "in_dy": 2,
            "out_dx": 3,
            "out_dy": 4,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["in"]["x"] == 9.0
    assert data["in"]["y"] == 3.0


def test_api_measure():
    resp = client.post(
        "/measure",
        json={
            "paths": sample_paths(),
            "geo_min": 0,
            "geo_max": 40,
            "count_per_band": 2,
            "measure_dx": 1.0,
            "measure_dy": 0.5,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    mp = data["measurement_points"]
    assert len(mp) == 2
    assert mp["1"]["x"] == 1.0
    assert mp["1"]["y"] == 0.5


def test_api_measure_missing_paths():
    resp = client.post(
        "/measure",
        json={"paths": [], "geo_min": 0, "geo_max": 10},
    )
    assert resp.status_code == 400
    assert "No paths provided" in resp.text


def test_api_export_dxf_rectangles(tmp_path, monkeypatch):
    # Force export to a temp directory
    out_file = tmp_path / "export.dxf"

    monkeypatch.chdir(tmp_path)

    resp = client.post(
        "/export/dxf",
        json={"paths": sample_paths(), "measure": False},
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/dxf"

    assert out_file.exists()
    text = out_file.read_text()
    assert "LINE" in text  # rectangles produce LINE entities


def test_api_export_dxf_measure(tmp_path, monkeypatch):
    out_file = tmp_path / "export.dxf"
    monkeypatch.chdir(tmp_path)

    resp = client.post(
        "/export/dxf",
        json={
            "paths": sample_paths(),
            "measure": True,
            "geo_min": 0,
            "geo_max": 40,
            "count_per_band": 2,
        },
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/dxf"

    assert out_file.exists()
    text = out_file.read_text()
    assert "POINT" in text  # measurement points produce POINT entities


def test_api_export_svg_rectangles(tmp_path, monkeypatch):
    out_file = tmp_path / "export.svg"
    monkeypatch.chdir(tmp_path)

    resp = client.post(
        "/export/svg",
        json={"paths": sample_paths(), "measure": False},
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/svg+xml"

    assert out_file.exists()
    text = out_file.read_text()
    assert "<rect" in text


def test_api_export_svg_measure(tmp_path, monkeypatch):
    out_file = tmp_path / "export.svg"
    monkeypatch.chdir(tmp_path)

    resp = client.post(
        "/export/svg",
        json={
            "paths": sample_paths(),
            "measure": True,
            "geo_min": 0,
            "geo_max": 40,
            "count_per_band": 2,
        },
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/svg+xml"

    assert out_file.exists()
    text = out_file.read_text()
    assert "<circle" in text
