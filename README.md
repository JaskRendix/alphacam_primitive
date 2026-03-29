# **alphacam‑primitive**

A modern Python rewrite of the legacy *Primitive* Alphacam macro.

This project extracts the core geometry and sequencing logic from the original VB6/VBA codebase:

https://github.com/grakh/alphacam

The goal is simple: preserve the useful logic, remove the dependency on Alphacam, and provide a clean, testable, portable library.

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

## **Why this modernization exists**

The original macro contained useful geometry logic, but it was locked inside:

- VB6 modules  
- binary macro packages  
- an environment that cannot be tested or reused  

This rewrite extracts the logic into a clean Python package with:

- explicit data structures  
- deterministic behavior  
- full test coverage  
- no external dependencies  
- a simple CLI  
- DXF/SVG output for inspection  

The result is a small, focused library that preserves the functional core of the original macro without the constraints of the Alphacam environment.

---

## **Installation**

```
pip install -e .
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

## **Tests**

```
pytest
```

All modules are covered by unit tests, including the CLI and exporters.
