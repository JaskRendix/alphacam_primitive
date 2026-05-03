from alphacam_primitive.exporters.dxf import (
    export_measurement_points,
    export_rectangles,
)
from alphacam_primitive.exporters.svg import export_svg_unified
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


def test_export_svg_unified_basic(tmp_path):
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 20, 10, 30, 20, 30),
    ]

    out = tmp_path / "rects.svg"
    export_svg_unified(paths, out)

    text = out.read_text()

    assert "<svg" in text
    assert "<rect" in text
    assert 'x="0"' in text
    assert 'width="10"' in text


def test_export_svg_unified_y_flipped(tmp_path):
    paths = [PathBBox(1, 0, 0, 10, 5, 0)]
    out = tmp_path / "rect.svg"
    export_svg_unified(paths, out)

    text = out.read_text()
    assert 'y="-5"' in text


def test_export_svg_unified_viewbox(tmp_path):
    paths = [PathBBox(1, 10, 20, 30, 50, 0)]
    out = tmp_path / "rect.svg"
    export_svg_unified(paths, out)

    text = out.read_text()
    assert 'viewBox="10 -50 20 30"' in text


def test_export_svg_unified_inout_points(tmp_path):
    p = PathBBox(1, 0, 0, 10, 5, 0)
    p.in_point = MeasurementPoint(2, 3, band=1)
    p.out_point = MeasurementPoint(8, 4, band=1)

    out = tmp_path / "inout.svg"
    export_svg_unified([p], out)

    text = out.read_text()

    assert 'data-type="in"' in text
    assert 'data-type="out"' in text
    assert 'cx="2"' in text
    assert 'cy="-3"' in text


def test_export_svg_unified_measurement_points(tmp_path):
    paths = [PathBBox(1, 0, 0, 10, 5, 0)]
    points = {
        1: MeasurementPoint(1.0, 2.0, band=1),
        2: MeasurementPoint(5.0, 6.0, band=1),
    }

    out = tmp_path / "points.svg"
    export_svg_unified(paths, out, measurement_points=points)

    text = out.read_text()

    assert "<circle" in text
    assert 'data-measure="1"' in text
    assert 'cx="1.0"' in text
    assert 'cy="-2.0"' in text


def test_export_svg_unified_measurement_lines(tmp_path):
    paths = [PathBBox(1, 0, 0, 10, 5, 0)]
    lines = [(0.0, 0.0, 10.0, 10.0)]

    out = tmp_path / "lines.svg"
    export_svg_unified(paths, out, measurement_lines=lines)

    text = out.read_text()

    assert "<line" in text
    assert 'data-measure="1"' in text
    assert 'x1="0.0"' in text

    # Accept both 0.0 and -0.0 (float formatting)
    assert 'y1="0.0"' in text or 'y1="-0.0"' in text

    assert 'x2="10.0"' in text
    assert 'y2="-10.0"' in text


def test_export_svg_unified_empty_paths(tmp_path):
    out = tmp_path / "empty.svg"
    export_svg_unified([], out)

    assert out.read_text().strip() == "<svg></svg>"
