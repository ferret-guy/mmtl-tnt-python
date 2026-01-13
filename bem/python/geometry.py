"""Geometry helpers for TNT/BEM cross-section files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional
import shutil
import subprocess
import tempfile


@dataclass(frozen=True)
class GroundPlane:
    name: str

    def to_tcl(self) -> str:
        return f"GroundPlane {self.name}"


@dataclass(frozen=True)
class DielectricLayer:
    name: str
    thickness: float
    loss_tangent: float
    permittivity: float

    def to_tcl(self) -> str:
        return (
            f"DielectricLayer {self.name}  \\\n\t -thickness {self.thickness} \\\n\t -lossTangent {self.loss_tangent} \\\n\t -permittivity {self.permittivity}"
        )


@dataclass(frozen=True)
class RectangleConductors:
    name: str
    width: float
    pitch: float
    conductivity: str
    height: float
    number: int
    y_offset: float
    x_offset: float

    def to_tcl(self) -> str:
        return (
            f"RectangleConductors {self.name}  \\\n\t -width {self.width} \\\n\t -pitch {self.pitch} \\\n\t -conductivity {self.conductivity} \\\n\t -height {self.height} \\\n\t -number {self.number} \\\n\t -yOffset {self.y_offset} \\\n\t -xOffset {self.x_offset}"
        )


@dataclass(frozen=True)
class Geometry:
    title: str
    coupling_length: str
    rise_time: str
    frequency: str
    default_length_units: str
    cseg: int
    dseg: int
    ground_planes: List[GroundPlane] = field(default_factory=list)
    dielectric_layers: List[DielectricLayer] = field(default_factory=list)
    rectangle_conductors: List[RectangleConductors] = field(default_factory=list)

    def to_xsctn(self) -> str:
        lines = [
            "package require csdl",
            "",
            f"set _title \"{self.title}\"",
            f"set ::Stackup::couplingLength \"{self.coupling_length}\"",
            f"set ::Stackup::riseTime \"{self.rise_time}\"",
            f"set ::Stackup::frequency \"{self.frequency}\"",
            f"set ::Stackup::defaultLengthUnits \"{self.default_length_units}\"",
            f"set CSEG {self.cseg}",
            f"set DSEG {self.dseg}",
            "",
        ]

        for plane in self.ground_planes:
            lines.append(plane.to_tcl())
        for layer in self.dielectric_layers:
            lines.append(layer.to_tcl())
        for rect in self.rectangle_conductors:
            lines.append(rect.to_tcl())

        return "\n".join(lines) + "\n"

    def write_xsctn(self, path: Path) -> None:
        path.write_text(self.to_xsctn(), encoding="utf-8")

    def run_simulation(
        self,
        xsctn_path: Path,
        *,
        cseg: Optional[int] = None,
        dseg: Optional[int] = None,
        wish_path: Optional[str] = None,
        working_dir: Optional[Path] = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run BEM simulation by invoking wish with a short Tcl driver.

        This requires the BEM Tcl package available in the runtime environment.
        """
        if wish_path is None:
            wish_path = shutil.which("wish")
        if wish_path is None:
            raise RuntimeError("wish binary not found in PATH")

        cseg_value = self.cseg if cseg is None else cseg
        dseg_value = self.dseg if dseg is None else dseg

        driver = """
package require bem
namespace import ::bem::*

bemDeleteAll
source {xsctn_file}
bemRunSimulationCS {node_name} {cseg_value} {dseg_value}
"""
        driver = driver.format(
            xsctn_file=xsctn_path.as_posix(),
            node_name=xsctn_path.stem,
            cseg_value=cseg_value,
            dseg_value=dseg_value,
        )

        with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False) as handle:
            handle.write(driver)
            driver_path = Path(handle.name)

        try:
            return subprocess.run(
                [wish_path, driver_path.as_posix()],
                check=False,
                text=True,
                capture_output=True,
                cwd=working_dir,
            )
        finally:
            driver_path.unlink(missing_ok=True)


def build_test1_geometry() -> Geometry:
    return Geometry(
        title="Duplicate of test1.xsctn",
        coupling_length="0.02540 meters",
        rise_time="25",
        frequency="1e9",
        default_length_units="mils",
        cseg=45,
        dseg=45,
        ground_planes=[GroundPlane(name="G9")],
        dielectric_layers=[
            DielectricLayer(
                name="D7",
                thickness=10,
                loss_tangent=0.012,
                permittivity=4,
            )
        ],
        rectangle_conductors=[
            RectangleConductors(
                name="Rect8",
                width=18,
                pitch=50,
                conductivity="3e+07siemens/meter",
                height=1.4,
                number=2,
                y_offset=0,
                x_offset=0,
            )
        ],
    )


def iter_test1_lines() -> Iterable[str]:
    geometry = build_test1_geometry()
    return geometry.to_xsctn().splitlines()
