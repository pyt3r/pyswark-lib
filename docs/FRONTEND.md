# Frontend & Visualization

## Overview

pyswark is primarily a backend/library project with no traditional web frontend.
Its "frontend" layer is the visualization and interactive exploration surface
provided by the HoloViews/Panel/Bokeh stack.

## Visualization stack

| Technology | Role | Module |
|-----------|------|--------|
| HoloViews | Declarative data visualization | Used in examples, GlueDb analytics |
| Panel | Interactive dashboards and apps | Serves HoloViews objects as web apps |
| Bokeh | Rendering backend for HoloViews/Panel | Runtime dependency |
| jupyter_bokeh | Jupyter notebook integration | Enables in-notebook interactivity |

## How visualization fits the architecture

Visualization is an **application-layer concern**. It depends on:
- `core.io` for loading data via URIs
- `gluedb` for catalog access
- `ts` / `tensor` for time series and array data
- `query` for filtering before display

Visualization code should never be imported by `core/` or `lib/`.

## Example: GlueDb + SMA visualization

The canonical example (`examples/gluedb/sma.py`) demonstrates:
1. Loading financial data via `api.read()`
2. Storing artifacts in a GlueDb catalog
3. Computing simple moving averages
4. Visualizing with HoloViews curves

This is rendered as a sphinx-gallery example in the built docs.

## Panel applications

Panel enables serving interactive dashboards:

```python
import panel as pn
import holoviews as hv

hv.extension('bokeh')
# Build HoloViews objects from pyswark data
# pn.serve(dashboard)
```

## Guidelines for visualization code

1. Keep data loading and visualization separate — load via `api.read()`, visualize
   in a distinct function or cell.
2. Use HoloViews' declarative API over raw Bokeh when possible.
3. Visualization examples should be sphinx-gallery compatible (`.py` with `# %%` cells).
4. Do not embed large datasets in example scripts — use URIs or `pyswark://` assets.
