# **alphacam‑primitive**

A modern, fully testable Python rewrite of the legacy *Primitive* Alphacam macro.

This project extracts the useful geometry and sequencing logic from the original VB6/VBA codebase:

> [https://github.com/grakh/alphacam](https://github.com/grakh/alphacam)

The goal is simple:

- preserve the valuable logic  
- remove the dependency on Alphacam  
- expose everything as a clean, portable Python library  
- provide a CLI and optional API  
- support visual debugging through DXF/SVG exporters  

The rewrite isolates the core algorithms and removes all Alphacam‑specific UI, COM, and macro packaging.

---

## **Features**

### Geometry model  
A minimal `PathBBox` structure representing each geometry by:

- `min_x`, `min_y`  
- `max_x`, `max_y`  
- `length`  

This mirrors how the original VB macro reasoned about geometry.

---

### Grouping & ordering  
Deterministic grouping and ordering of geometry into X/Y bands.  
The behavior matches the original macro and is fully covered by tests.

---

### In/out point calculation  
A simplified and predictable version of the VB `IntersectWithLine` logic.  
The original macro used bounding boxes — this rewrite does the same.

---

### Measurement points  
Placement of measurement points along diagonal intersections, following the same rules as the VB macro.

---

### Exporters  
Two export formats:

- **DXF** — rectangles and measurement points  
- **Unified SVG** — rectangles, in/out points, measurement points, measurement lines, optional band overlays  

The unified SVG exporter is ideal for debugging and visualization.

---

### CLI  
A command‑line interface mirroring the structure of the original macro:

- `order`  
- `inout`  
- `measure`  
- `export-dxf`  
- `export-svg`  
- `serve` (API server)

---

### API (optional)  
A FastAPI server exposing the same functionality over HTTP.

---

### Viewer  
A lightweight browser viewer (in `viewer/`) for inspecting exported SVG files.  
Includes pan/zoom and optional overlays.

Viewer tests are manual and live under `viewer/tests/`.

---

## **What’s intentionally *not* included**

This project does **not** attempt to recreate Alphacam’s UI or COM integration:

- VB6 forms  
- Alphacam COM calls (`Drw`, `Geo`, `MD`, `App`)  
- tool selection  
- layer visibility  
- operation creation  
- `.amb` / `.amp` macro packaging  

These were tightly coupled to Alphacam and not portable.

---

## **Installation**

### CLI only
```
pip install alphacam-primitive # not yet published to PyPI
```

### CLI + API
```
pip install "alphacam-primitive[api]"
```

### Development install
```
pip install -e .[api]
```

---

## **CLI usage**

### Order geometry
```
alphacam-primitive order --input paths.json
```

### Compute in/out points
```
alphacam-primitive inout --input paths.json --in-dx 1 --in-dy 2
```

### Compute measurement points
```
alphacam-primitive measure --input paths.json --geo-min 0 --geo-max 60
```

### Export DXF
```
alphacam-primitive export-dxf --input paths.json --output rects.dxf
```

### Export unified SVG
```
alphacam-primitive export-svg --input paths.json --output out.svg
```

### Export measurement overlays to SVG
```
alphacam-primitive export-svg --input paths.json --measure --geo-min 0 --geo-max 60 --output meas.svg
```

---

## **API usage**

Start the server:

```
alphacam-primitive serve --reload
```

Or manually:

```
uvicorn alphacam_primitive.api:app --reload
```

Interactive docs:

- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

## **API endpoints**

| Method | Path | Description |
|--------|------|-------------|
| **GET** | `/health` | Health check |
| **POST** | `/order` | Order geometry by X/Y bands |
| **POST** | `/inout` | Compute in/out points |
| **POST** | `/measure` | Compute measurement points |
| **POST** | `/export/dxf` | Export rectangles or measurement points to DXF |
| **POST** | `/export/svg` | Export unified SVG (rectangles, in/out, measurement points/lines) |

---

## **Example request formats**

### `/order`
```json
[
  {"name": 1, "min_x": 0, "min_y": 0, "max_x": 10, "max_y": 5, "length": 30},
  {"name": 2, "min_x": 20, "min_y": 0, "max_x": 30, "max_y": 5, "length": 30}
]
```

### `/inout`
```json
{
  "path": {"name": 1, "min_x": 0, "min_y": 0, "max_x": 10, "max_y": 5, "length": 30},
  "in_dx": 1,
  "in_dy": 2,
  "out_dx": 3,
  "out_dy": 4
}
```

### `/measure`
```json
{
  "paths": [...],
  "geo_min": 0,
  "geo_max": 40,
  "count_per_band": 2,
  "measure_dx": 1.0,
  "measure_dy": 0.5
}
```

### `/export/svg`
```json
{
  "paths": [...],
  "measure": true,
  "geo_min": 0,
  "geo_max": 40,
  "count_per_band": 2
}
```

---

## **Viewer**

The `viewer/` folder contains:

- `index.html` — the viewer  
- `viewer.js` — pan/zoom + file loading  
- `overlays.js` — optional overlays (bands, order, in/out, measurement)  
- `overlays.css` — overlay styling  
- manual tests under `viewer/tests/`

Open `viewer/index.html` in a browser and load any exported SVG.

---

## **Tests**

Run the full Python test suite:

```
pytest
```

All core modules — geometry, grouping, ordering, in/out, measurement, exporters, CLI, and API — are covered by tests.
