"""Python helpers for TNT/BEM workflows."""

from .geometry import (
    DielectricLayer,
    Geometry,
    GroundPlane,
    RectangleConductors,
    build_test1_geometry,
    iter_test1_lines,
)

__all__ = [
    "DielectricLayer",
    "Geometry",
    "GroundPlane",
    "RectangleConductors",
    "build_test1_geometry",
    "iter_test1_lines",
]
