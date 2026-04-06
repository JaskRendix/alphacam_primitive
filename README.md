# **alphacam‑primitive**

A modern Python rewrite of the legacy *Primitive* Alphacam macro.

This project extracts the core geometry and sequencing logic from the original VB6/VBA codebase:

https://github.com/grakh/alphacam

The goal is to preserve the useful logic, remove the dependency on Alphacam, and provide a clean, testable, portable library.

The original macro was built around VB6 forms, Alphacam COM calls, and binary `.amb` packages. The logic was tightly coupled to the Alphacam environment and could not be reused or tested outside it.  
This rewrite isolates the parts that matter:

- geometry grouping  
- geometry ordering  
- in/out point calculation  
- measurement point placement  

Everything else (UI, COM, tool selection, layer visibility, operation management) is intentionally left out.

---

## **What this project contains**

### **Geometry model**
A minimal representation of a path as a bounding box:

- `min_x`, `min_y`  
- `max_x`, `max_y`  
- `length`  

This matches how the original VB code used geometry.

### **Grouping and ordering**
A faithful rewrite of the VB logic that sorted and grouped geometry by X or Y bands.  
The behavior is deterministic and covered by tests.

### **In/out point calculation**
A simplified version of the VB `IntersectWithLine` logic.  
The original macro used bounding boxes for these calculations, so the rewrite does the same.

### **Measurement points**
The VB macro placed measurement points along diagonal intersections.  
The rewrite follows the same rules and exposes the result as structured data.

### **Exporters**
DXF and SVG exporters for rectangles and measurement points.  
These allow inspection and downstream use without Alphacam.

### **CLI**
A command‑line interface that mirrors the structure of the original macro:

- `order`  
- `inout`  
- `measure`  
- `export-dxf`  
- `export-svg`  

### **API**
An optional FastAPI server that exposes the same functionality over HTTP.

---

## **What this project does not include**

The following parts of the original macro are not reproduced:

- VB6 forms (`frmMain.frm`)  
- menu registration (`Events.bas`)  
- Alphacam COM calls (`Drw`, `Geo`, `MD`, `App`)  
- tool selection  
- layer visibility  
- operation creation or deletion  
- `.amb` and `.amp` binary macro packages  

These elements were tied to the Alphacam runtime and had no standalone value.

---

## **Installation**

### CLI only
```
pip install alphacam-primitive
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

### Export rectangles to DXF
```
alphacam-primitive export-dxf --input paths.json --output rects.dxf
```

### Export measurement points to SVG
```
alphacam-primitive export-svg --input paths.json --measure --output meas.svg
```

---

## **API usage**

The project includes an optional FastAPI server that exposes the same functionality as the CLI.

Start the server:

```
alphacam-primitive serve --reload
```

Or manually:

```
uvicorn alphacam_primitive.api:app --reload
```

Interactive API docs:

- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

## **Endpoints**

| Method | Path | Description |
|--------|------|-------------|
| **GET** | `/health` | Health check |
| **POST** | `/order` | Order geometry by X/Y bands |
| **POST** | `/inout` | Compute in/out points for a single path |
| **POST** | `/measure` | Compute measurement points along ordered geometry |
| **POST** | `/export/dxf` | Export rectangles or measurement points to DXF |
| **POST** | `/export/svg` | Export rectangles or measurement points to SVG |

---

## **Request formats**

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

### `/export/dxf` and `/export/svg`
```json
{
  "paths": [...],
  "measure": true,
  "geo_min": 0,
  "geo_max": 40,
  "count_per_band": 2
}
```

Both endpoints return a downloadable file.

---

## **Examples**

### Order geometry
```
curl -X POST http://localhost:8000/order \
     -H "Content-Type: application/json" \
     -d @paths.json
```

### Compute in/out points
```
curl -X POST http://localhost:8000/inout \
     -H "Content-Type: application/json" \
     -d '{"path": {"name":1,"min_x":0,"min_y":0,"max_x":10,"max_y":5,"length":30}}'
```

### Export SVG
```
curl -X POST http://localhost:8000/export/svg \
     -H "Content-Type: application/json" \
     -d @paths.json \
     -o output.svg
```

---

## Tools

### Web viewer
A small static viewer lives in the `viewer/` folder.  
It loads exported SVG files and lets you pan and zoom in the browser.

### Viewer tests
The viewer has simple browser‑based tests under `viewer/tests/`.  
Open `test.html` in a browser to run them.

---

## **Tests**

```
pytest
```

All modules are covered by unit tests, including the CLI, API, geometry logic, and exporters.
