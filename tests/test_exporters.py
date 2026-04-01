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


def test_export_rectangles_dxf_basic(tmp_path):
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 20, 10, 30, 20, 30),
    ]

    out = tmp_path / "rects.dxf"
    export_rectangles(paths, out)

    text = out.read_text()

    assert "LINE" in text
    assert "10\n0" in text  # x1 of first rectangle
    assert "20\n5" in text  # y2 of first rectangle


def test_export_rectangles_dxf_four_lines(tmp_path):
    paths = [PathBBox(1, 0, 0, 10, 5, 0)]
    out = tmp_path / "rects.dxf"
    export_rectangles(paths, out)

    text = out.read_text()
    assert text.count("0\nLINE") == 4


def test_export_dxf_header_footer(tmp_path):
    paths = [PathBBox(1, 0, 0, 1, 1, 0)]
    out = tmp_path / "rects.dxf"
    export_rectangles(paths, out)

    text = out.read_text()
    assert text.startswith("0\nSECTION")
    assert text.strip().endswith("0\nEOF")


def test_export_measurement_points_dxf(tmp_path):
    points = {
        1: MeasurementPoint(1.0, 2.0, band=1),
        2: MeasurementPoint(5.0, 6.0, band=1),
    }

    out = tmp_path / "points.dxf"
    export_measurement_points(points, out)

    text = out.read_text()

    assert "POINT" in text
    assert "10\n1.0" in text
    assert "20\n2.0" in text


def test_export_measurement_points_dxf_multiple(tmp_path):
    points = {
        1: MeasurementPoint(1, 2, band=1),
        2: MeasurementPoint(5, 6, band=1),
    }

    out = tmp_path / "pts.dxf"
    export_measurement_points(points, out)

    text = out.read_text()
    assert text.count("0\nPOINT") == 2


def test_export_rectangles_svg_basic(tmp_path):
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


def test_export_rectangles_svg_y_flipped(tmp_path):
    paths = [PathBBox(1, 0, 0, 10, 5, 0)]
    out = tmp_path / "rect.svg"
    export_rectangles_svg(paths, out)

    text = out.read_text()
    assert 'y="-5"' in text


def test_export_rectangles_svg_viewbox(tmp_path):
    paths = [PathBBox(1, 10, 20, 30, 50, 0)]
    out = tmp_path / "rect.svg"
    export_rectangles_svg(paths, out)

    text = out.read_text()
    assert 'viewBox="10 -50 20 30"' in text


def test_export_measurement_points_svg_basic(tmp_path):
    points = {
        1: MeasurementPoint(1.0, 2.0, band=1),
        2: MeasurementPoint(5.0, 6.0, band=1),
    }

    out = tmp_path / "points.svg"
    export_measurement_points_svg(points, out)

    text = out.read_text()

    assert "<svg" in text
    assert "<circle" in text
    assert 'cx="1.0"' in text
    assert 'cy="-2.0"' in text


def test_export_measurement_points_svg_y_flipped(tmp_path):
    points = {1: MeasurementPoint(3, 7, band=1)}
    out = tmp_path / "p.svg"
    export_measurement_points_svg(points, out)

    text = out.read_text()
    assert 'cx="3"' in text
    assert 'cy="-7"' in text


def test_export_measurement_points_svg_empty(tmp_path):
    out = tmp_path / "empty.svg"
    export_measurement_points_svg({}, out)

    assert out.read_text().strip() == "<svg></svg>"
