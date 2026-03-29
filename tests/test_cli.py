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
    assert out["in"]["x"] == 9
    assert out["in"]["y"] == 3


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
            "--delta-measure",
            "1.0",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert "measurement_points" in out
