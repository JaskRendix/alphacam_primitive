import json
import subprocess
from pathlib import Path


def write_paths(tmp_path: Path):
    data = [
        {"name": 1, "min_x": 0, "min_y": 0, "max_x": 10, "max_y": 5, "length": 30},
        {"name": 2, "min_x": 20, "min_y": 0, "max_x": 30, "max_y": 5, "length": 30},
    ]
    p = tmp_path / "paths.json"
    p.write_text(json.dumps(data))
    return p


def test_cli_order(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        ["alphacam-primitive", "order", "--input", str(paths)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["ordered_indices"] == [1, 2]


def test_cli_inout(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        [
            "alphacam-primitive",
            "inout",
            "--input",
            str(paths),
            "--in-dx",
            "1",
            "--in-dy",
            "2",
            "--out-dx",
            "3",
            "--out-dy",
            "4",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)

    # Path 1: min_x=0, min_y=0, max_x=10, max_y=5
    # in-point is computed from the MAX corner
    assert out["in"]["x"] == 9.0
    assert out["in"]["y"] == 3.0


def test_cli_measure(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        [
            "alphacam-primitive",
            "measure",
            "--input",
            str(paths),
            "--geo-min",
            "0",
            "--geo-max",
            "40",
            "--count-per-band",
            "2",
            "--measure-dx",
            "1.0",
            "--measure-dy",
            "0.5",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)

    assert "measurement_points" in out
    mp = out["measurement_points"]

    # Should have 2 measurement points
    assert len(mp) == 2

    # Check first point coordinates
    assert mp["1"]["x"] == 1.0
    assert mp["1"]["y"] == 0.5

    # Check band assignment
    assert mp["1"]["band"] == 1
    assert mp["2"]["band"] == 2


def test_cli_inout_with_index(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        [
            "alphacam-primitive",
            "inout",
            "--input",
            str(paths),
            "--index",
            "2",
            "--in-dx",
            "1",
            "--in-dy",
            "1",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)

    # Path 2: min_x=20, max_x=30, min_y=0, max_y=5
    assert out["path_name"] == 2
    assert out["in"]["x"] == 29.0
    assert out["in"]["y"] == 4.0


def test_cli_order_prefer_y(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        ["alphacam-primitive", "order", "--input", str(paths), "--prefer-y"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)

    # Both paths have same min_y, so order should remain stable
    assert out["ordered_indices"] == [1, 2]


def test_cli_measure_prefer_y(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        [
            "alphacam-primitive",
            "measure",
            "--input",
            str(paths),
            "--geo-min",
            "0",
            "--geo-max",
            "10",
            "--count-per-band",
            "1",
            "--prefer-y",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)
    mp = out["measurement_points"]

    # Both paths have min_y = 0, so both fall into band 1
    assert mp["1"]["band"] == 1
    assert mp["2"]["band"] == 1


def test_cli_measure_missing_args(tmp_path):
    paths = write_paths(tmp_path)
    result = subprocess.run(
        ["alphacam-primitive", "measure", "--input", str(paths)],
        capture_output=True,
        text=True,
    )

    # argparse should fail before running the command
    assert result.returncode != 0
    assert "--geo-min" in result.stderr or "--geo-max" in result.stderr


def test_cli_export_dxf_rectangles(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.dxf"

    result = subprocess.run(
        [
            "alphacam-primitive",
            "export-dxf",
            "--input",
            str(paths),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    text = out.read_text()
    assert "LINE" in text


def test_cli_export_dxf_measure(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.dxf"

    result = subprocess.run(
        [
            "alphacam-primitive",
            "export-dxf",
            "--input",
            str(paths),
            "--output",
            str(out),
            "--measure",
            "--geo-min",
            "0",
            "--geo-max",
            "40",
            "--count-per-band",
            "2",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    text = out.read_text()
    assert "POINT" in text


def test_cli_export_svg_rectangles(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.svg"

    result = subprocess.run(
        [
            "alphacam-primitive",
            "export-svg",
            "--input",
            str(paths),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    text = out.read_text()
    assert "<rect" in text


def test_cli_export_svg_measure(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.svg"

    result = subprocess.run(
        [
            "alphacam-primitive",
            "export-svg",
            "--input",
            str(paths),
            "--output",
            str(out),
            "--measure",
            "--geo-min",
            "0",
            "--geo-max",
            "40",
            "--count-per-band",
            "2",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    text = out.read_text()
    assert "<circle" in text
