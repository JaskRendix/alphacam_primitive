from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .exporters.dxf import export_measurement_points, export_rectangles
from .exporters.svg import export_svg_unified
from .geometry import PathBBox
from .grouping import order_geo
from .inout import InOutOffsets, compute_inout_points
from .measurement import MeasurementOffsets, compute_measurement_points

app = FastAPI(
    title="Alphacam Primitive API",
    description="HTTP interface for ordering, in/out logic, measurement routines, and DXF/SVG export.",
    version="1.0.0",
)


class PathBBoxModel(BaseModel):
    name: str | int
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    length: float

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": 1,
                "min_x": 0,
                "min_y": 0,
                "max_x": 10,
                "max_y": 5,
                "length": 30,
            }
        }
    }


class InOutRequest(BaseModel):
    path: PathBBoxModel
    in_dx: float = 0.0
    in_dy: float = 0.0
    out_dx: float = 0.0
    out_dy: float = 0.0


class MeasureRequest(BaseModel):
    paths: list[PathBBoxModel]
    geo_min: float
    geo_max: float
    count_per_band: int = 1
    measure_dx: float = 0.0
    measure_dy: float = 0.0
    prefer_y: bool = False


class ExportRequest(BaseModel):
    paths: list[PathBBoxModel]
    measure: bool = False
    geo_min: float | None = None
    geo_max: float | None = None
    count_per_band: int = 1
    measure_dx: float = 0.0
    measure_dy: float = 0.0
    prefer_y: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/order")
def api_order(paths: list[PathBBoxModel], prefer_y: bool = False) -> dict[str, Any]:
    """Order geometries based on bounding boxes."""
    bboxes = [PathBBox(**p.model_dump()) for p in paths]
    ordered, bands = order_geo(bboxes, prefer_y=prefer_y)
    return {"ordered_indices": ordered, "path_band_lengths": bands}


@app.post("/inout")
def api_inout(req: InOutRequest) -> dict[str, Any]:
    """Compute in/out points for a single path."""
    offsets = InOutOffsets(
        in_dx=req.in_dx,
        in_dy=req.in_dy,
        out_dx=req.out_dx,
        out_dy=req.out_dy,
    )
    in_x, in_y, out_x, out_y = compute_inout_points(
        PathBBox(**req.path.model_dump()), offsets
    )
    return {
        "path_name": req.path.name,
        "in": {"x": in_x, "y": in_y},
        "out": {"x": out_x, "y": out_y},
    }


@app.post("/measure")
def api_measure(req: MeasureRequest) -> dict[str, dict[str, dict[str, Any]]]:
    """Compute measurement points along ordered geometries."""
    if not req.paths:
        raise HTTPException(status_code=400, detail="No paths provided")

    bboxes = [PathBBox(**p.model_dump()) for p in req.paths]
    ordered, _ = order_geo(bboxes, prefer_y=req.prefer_y)

    measurement = compute_measurement_points(
        paths=bboxes,
        ordered_indices=ordered,
        geo_min=req.geo_min,
        geo_max=req.geo_max,
        count_per_band=req.count_per_band,
        offsets=MeasurementOffsets(dx=req.measure_dx, dy=req.measure_dy),
        prefer_y=req.prefer_y,
    )

    return {
        "measurement_points": {
            str(k): {"x": v.x, "y": v.y, "band": v.band} for k, v in measurement.items()
        }
    }


@app.post("/export/dxf")
def api_export_dxf(req: ExportRequest) -> FileResponse:
    """Export rectangles or measurement points to DXF."""
    bboxes = [PathBBox(**p.model_dump()) for p in req.paths]
    out_path = "export.dxf"

    if req.measure:
        if req.geo_min is None or req.geo_max is None:
            raise HTTPException(status_code=400, detail="geo_min and geo_max required")

        ordered, _ = order_geo(bboxes, prefer_y=req.prefer_y)
        measurement = compute_measurement_points(
            paths=bboxes,
            ordered_indices=ordered,
            geo_min=req.geo_min,
            geo_max=req.geo_max,
            count_per_band=req.count_per_band,
            offsets=MeasurementOffsets(dx=req.measure_dx, dy=req.measure_dy),
            prefer_y=req.prefer_y,
        )
        export_measurement_points(measurement, Path(out_path))
    else:
        export_rectangles(bboxes, Path(out_path))

    return FileResponse(out_path, media_type="application/dxf")


@app.post("/export/svg")
def api_export_svg(req: ExportRequest) -> FileResponse:
    """Export rectangles or measurement points to SVG."""
    bboxes = [PathBBox(**p.model_dump()) for p in req.paths]
    out_path = "export.svg"

    measurement_points = None
    measurement_lines = None

    if req.measure:
        if req.geo_min is None or req.geo_max is None:
            raise HTTPException(status_code=400, detail="geo_min and geo_max required")

        ordered, _ = order_geo(bboxes, prefer_y=req.prefer_y)

        measurement_points = compute_measurement_points(
            paths=bboxes,
            ordered_indices=ordered,
            geo_min=req.geo_min,
            geo_max=req.geo_max,
            count_per_band=req.count_per_band,
            offsets=MeasurementOffsets(dx=req.measure_dx, dy=req.measure_dy),
            prefer_y=req.prefer_y,
        )

        # Optional measurement diagonals
        measurement_lines = [
            (p.x, p.y, q.x, q.y)
            for p, q in zip(
                list(measurement_points.values())[:-1],
                list(measurement_points.values())[1:],
            )
        ]

    export_svg_unified(
        paths=bboxes,
        out_path=Path(out_path),
        measurement_points=measurement_points,
        measurement_lines=measurement_lines,
    )

    return FileResponse(out_path, media_type="image/svg+xml")
