from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exporters.dxf import export_measurement_points, export_rectangles
from .exporters.svg import export_measurement_points_svg, export_rectangles_svg
from .geometry import PathBBox
from .grouping import order_geo
from .inout import InOutOffsets, compute_inout_points
from .measurement import MeasurementOffsets, compute_measurement_points


def _load_paths_from_json(path: Path) -> list[PathBBox]:
    """
    Expect a JSON array of objects:

    [
      {"name": 1, "min_x": 0, "min_y": 0, "max_x": 10, "max_y": 5, "length": 30},
      ...
    ]
    """
    data = json.loads(path.read_text())
    paths: list[PathBBox] = []
    for item in data:
        try:
            paths.append(
                PathBBox(
                    name=item["name"],
                    min_x=item["min_x"],
                    min_y=item["min_y"],
                    max_x=item["max_x"],
                    max_y=item["max_y"],
                    length=item["length"],
                )
            )
        except KeyError as e:
            raise SystemExit(f"Missing field {e} in path entry {item}") from None
    return paths


def cmd_order(args: argparse.Namespace) -> None:
    paths = _load_paths_from_json(args.input)
    ordered, bands = order_geo(paths, prefer_y=args.prefer_y)
    out = {
        "ordered_indices": ordered,
        "path_band_lengths": bands,
    }
    if args.output:
        args.output.write_text(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))


def cmd_inout(args: argparse.Namespace) -> None:
    paths = _load_paths_from_json(args.input)
    if not paths:
        raise SystemExit("No paths in input")

    p = paths[0] if args.index is None else paths[args.index - 1]
    offsets = InOutOffsets(
        in_dx=args.in_dx,
        in_dy=args.in_dy,
        out_dx=args.out_dx,
        out_dy=args.out_dy,
    )
    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)
    out = {
        "path_name": p.name,
        "in": {"x": in_x, "y": in_y},
        "out": {"x": out_x, "y": out_y},
    }
    if args.output:
        args.output.write_text(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))


def cmd_export_dxf(args: argparse.Namespace) -> None:
    paths = _load_paths_from_json(args.input)

    if args.measure:
        if args.geo_min is None or args.geo_max is None:
            raise SystemExit("--geo-min and --geo-max are required with --measure")

        ordered, _ = order_geo(paths, prefer_y=args.prefer_y)
        measurement = compute_measurement_points(
            paths=paths,
            ordered_indices=ordered,
            geo_min=args.geo_min,
            geo_max=args.geo_max,
            count_per_band=args.count_per_band,
            offsets=MeasurementOffsets(dx=args.measure_dx, dy=args.measure_dy),
            prefer_y=args.prefer_y,
        )
        export_measurement_points(measurement, args.output)
    else:
        export_rectangles(paths, args.output)


def cmd_export_svg(args: argparse.Namespace) -> None:
    paths = _load_paths_from_json(args.input)

    if args.measure:

        if args.geo_min is None or args.geo_max is None:
            raise SystemExit("--geo-min and --geo-max are required with --measure")

        ordered, _ = order_geo(paths, prefer_y=args.prefer_y)
        measurement = compute_measurement_points(
            paths=paths,
            ordered_indices=ordered,
            geo_min=args.geo_min,
            geo_max=args.geo_max,
            count_per_band=args.count_per_band,
            offsets=MeasurementOffsets(dx=args.measure_dx, dy=args.measure_dy),
            prefer_y=args.prefer_y,
        )
        export_measurement_points_svg(measurement, args.output)
    else:
        export_rectangles_svg(paths, args.output)


def cmd_measure(args: argparse.Namespace) -> None:
    paths = _load_paths_from_json(args.input)
    ordered, _ = order_geo(paths, prefer_y=args.prefer_y)

    measurement = compute_measurement_points(
        paths=paths,
        ordered_indices=ordered,
        geo_min=args.geo_min,
        geo_max=args.geo_max,
        count_per_band=args.count_per_band,
        offsets=MeasurementOffsets(dx=args.measure_dx, dy=args.measure_dy),
        prefer_y=args.prefer_y,
    )

    out = {
        "measurement_points": {
            str(k): {"x": v.x, "y": v.y, "band": v.band} for k, v in measurement.items()
        },
    }
    if args.output:
        args.output.write_text(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alphacam-primitive",
        description="Modern rewrite of Alphacam Primitive macro logic (grouping, ordering, in/out, measurement).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # order
    p_order = sub.add_parser("order", help="Order geometries based on bounding boxes.")
    p_order.add_argument(
        "--input", type=Path, required=True, help="JSON file with path bounding boxes."
    )
    p_order.add_argument("--output", type=Path, help="Optional JSON output file.")
    p_order.add_argument(
        "--prefer-y", action="store_true", help="Group primarily along Y instead of X."
    )
    p_order.set_defaults(func=cmd_order)

    # inout
    p_inout = sub.add_parser("inout", help="Compute in/out points for a single path.")
    p_inout.add_argument("--input", type=Path, required=True)
    p_inout.add_argument("--output", type=Path)
    p_inout.add_argument(
        "--index", type=int, help="1-based index of path in input array."
    )
    p_inout.add_argument("--in-dx", type=float, default=0.0)
    p_inout.add_argument("--in-dy", type=float, default=0.0)
    p_inout.add_argument("--out-dx", type=float, default=0.0)
    p_inout.add_argument("--out-dy", type=float, default=0.0)
    p_inout.set_defaults(func=cmd_inout)

    # measure
    p_meas = sub.add_parser(
        "measure", help="Compute measurement points along ordered geometries."
    )
    p_meas.add_argument("--input", type=Path, required=True)
    p_meas.add_argument("--output", type=Path)
    p_meas.add_argument("--prefer-y", action="store_true")
    p_meas.add_argument("--geo-min", type=float, required=True)
    p_meas.add_argument("--geo-max", type=float, required=True)
    p_meas.add_argument("--count-per-band", type=int, default=1)
    p_meas.add_argument("--measure-dx", type=float, default=0.0)
    p_meas.add_argument("--measure-dy", type=float, default=0.0)
    p_meas.set_defaults(func=cmd_measure)

    # export-dxf
    p_dxf = sub.add_parser(
        "export-dxf", help="Export rectangles or measurement points to DXF."
    )
    p_dxf.add_argument("--input", type=Path, required=True)
    p_dxf.add_argument("--output", type=Path, required=True)
    p_dxf.add_argument(
        "--measure",
        action="store_true",
        help="Export measurement points instead of rectangles.",
    )
    p_dxf.add_argument("--prefer-y", action="store_true")
    p_dxf.add_argument("--geo-min", type=float)
    p_dxf.add_argument("--geo-max", type=float)
    p_dxf.add_argument("--count-per-band", type=int, default=1)
    p_dxf.add_argument("--measure-dx", type=float, default=0.0)
    p_dxf.add_argument("--measure-dy", type=float, default=0.0)
    p_dxf.set_defaults(func=cmd_export_dxf)

    # export-svg
    p_svg = sub.add_parser(
        "export-svg", help="Export rectangles or measurement points to SVG."
    )
    p_svg.add_argument("--input", type=Path, required=True)
    p_svg.add_argument("--output", type=Path, required=True)
    p_svg.add_argument("--measure", action="store_true")
    p_svg.add_argument("--prefer-y", action="store_true")
    p_svg.add_argument("--geo-min", type=float)
    p_svg.add_argument("--geo-max", type=float)
    p_svg.add_argument("--count-per-band", type=int, default=1)
    p_svg.add_argument("--measure-dx", type=float, default=0.0)
    p_svg.add_argument("--measure-dy", type=float, default=0.0)
    p_svg.set_defaults(func=cmd_export_svg)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
