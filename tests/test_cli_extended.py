import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from alphacam_primitive.cli import (
    _load_paths_from_json,
    build_parser,
    cmd_export_dxf,
    cmd_export_svg,
    cmd_inout,
    cmd_serve,
)


def write_bad_paths(tmp_path: Path):
    """Write a JSON missing required fields."""
    p = tmp_path / "bad.json"
    p.write_text(json.dumps([{"name": 1, "min_x": 0}]))  # missing fields
    return p


def write_paths(tmp_path: Path):
    p = tmp_path / "paths.json"
    p.write_text(
        json.dumps(
            [
                {
                    "name": 1,
                    "min_x": 0,
                    "min_y": 0,
                    "max_x": 10,
                    "max_y": 5,
                    "length": 30,
                },
                {
                    "name": 2,
                    "min_x": 20,
                    "min_y": 0,
                    "max_x": 30,
                    "max_y": 5,
                    "length": 30,
                },
            ]
        )
    )
    return p


def test_load_paths_missing_fields(tmp_path):
    bad = write_bad_paths(tmp_path)
    with pytest.raises(SystemExit) as e:
        _load_paths_from_json(bad)
    assert "Missing field" in str(e.value)


def test_cmd_inout_no_paths(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text("[]")

    parser = build_parser()
    args = parser.parse_args(["inout", "--input", str(empty)])

    with pytest.raises(SystemExit) as e:
        cmd_inout(args)

    assert "No paths in input" in str(e.value)


def test_export_dxf_missing_geo_args(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.dxf"

    parser = build_parser()
    args = parser.parse_args(
        [
            "export-dxf",
            "--input",
            str(paths),
            "--output",
            str(out),
            "--measure",
        ]
    )

    with pytest.raises(SystemExit) as e:
        cmd_export_dxf(args)

    assert "--geo-min" in str(e.value)


def test_export_svg_missing_geo_args(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.svg"

    parser = build_parser()
    args = parser.parse_args(
        [
            "export-svg",
            "--input",
            str(paths),
            "--output",
            str(out),
            "--measure",
        ]
    )

    with pytest.raises(SystemExit) as e:
        cmd_export_svg(args)

    assert "--geo-min" in str(e.value)


def test_cmd_serve_missing_uvicorn(monkeypatch):
    monkeypatch.setattr("alphacam_primitive.cli.uvicorn", None)

    parser = build_parser()
    args = parser.parse_args(["serve"])

    with pytest.raises(SystemExit) as e:
        cmd_serve(args)

    assert "FastAPI/uvicorn not installed" in str(e.value)


def test_cmd_serve_runs(monkeypatch):
    fake_uvicorn = Mock()
    fake_uvicorn.run = Mock()

    monkeypatch.setattr("alphacam_primitive.cli.uvicorn", fake_uvicorn)

    parser = build_parser()
    args = parser.parse_args(["serve"])

    cmd_serve(args)

    fake_uvicorn.run.assert_called_once()


def test_main_dispatch(monkeypatch, tmp_path):
    paths = write_paths(tmp_path)

    # Capture printed output
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a))

    # Run CLI via subprocess
    result = subprocess.run(
        ["alphacam-primitive", "order", "--input", str(paths)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ordered_indices" in result.stdout


def test_cmd_order_writes_output_file(tmp_path):
    paths = write_paths(tmp_path)
    out = tmp_path / "out.json"

    parser = build_parser()
    args = parser.parse_args(
        [
            "order",
            "--input",
            str(paths),
            "--output",
            str(out),
        ]
    )

    args.func(args)

    assert out.exists()
    data = json.loads(out.read_text())
    assert "ordered_indices" in data
