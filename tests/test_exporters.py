from pathlib import Path

from alphacam_primitive.exporters.dxf import (
    export_measurement_points,
    export_rectangles,
)
from alphacam_primitive.exporters.svg import (
    export_measurement_points_svg,
    export_rectangles_svg,
)
from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.measurement import MeasurementPoint


def test_export_rectangles_dxf(tmp_path):
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 20, 10, 30, 20, 30),
    ]

    out = tmp_path / "rects.dxf"
    export_rectangles(paths, out)

    text = out.read_text()

    # DXF must contain LINE entities
    assert "LINE" in text
    # Must contain coordinates of first rectangle
    assert "10\n0" in text  # x1
    assert "20\n5" in text  # y1


def test_export_measurement_points_dxf(tmp_path):
    points = {
        1: MeasurementPoint(1.0, 2.0),
        2: MeasurementPoint(5.0, 6.0),
    }

    out = tmp_path / "points.dxf"
    export_measurement_points(points, out)

    text = out.read_text()

    assert "POINT" in text
    assert "10\n1.0" in text
    assert "20\n2.0" in text


def test_export_rectangles_svg(tmp_path):
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 20, 10, 30, 20, 30),
    ]

    out = tmp_path / "rects.svg"
    export_rectangles_svg(paths, out)

    text = out.read_text()

    assert "<svg" in text
    assert "<rect" in text
    assert 'x="0"' in text
    assert 'width="10"' in text


def test_export_measurement_points_svg(tmp_path):
    points = {
        1: MeasurementPoint(1.0, 2.0),
        2: MeasurementPoint(5.0, 6.0),
    }

    out = tmp_path / "points.svg"
    export_measurement_points_svg(points, out)

    text = out.read_text()

    assert "<svg" in text
    assert "<circle" in text
    assert 'cx="1.0"' in text
    assert 'cy="-2.0"' in text
