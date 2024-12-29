from dataclasses import dataclass
import logging
from typing import Literal, Callable

from build123d import (
    CenterOf,
    Compound,
    RigidJoint,
    Sketch,
    Pos,
    Rectangle,
    Align,
    extrude,
    Location,
    Vector,
)

from led_matrix_enclosure.parameters.lid_grid import LidGridParameters
from led_matrix_enclosure.sides import Side


LOGGER = logging.getLogger(__name__)


Orientation = Literal["horizontal", "vertical"]


def _get_oriented_sides(orientation: Orientation) -> tuple[Side, Side]:
    match orientation:
        case "horizontal":
            return Side.FRONT, Side.BACK
        case "vertical":
            return Side.LEFT, Side.RIGHT


@dataclass(frozen=True)
class LidGridBuilder:
    """A grid."""

    #: Parameters of the grid
    parameters: LidGridParameters

    def _compute_range_bounds(self, orientation: Orientation) -> tuple[int, int, int]:
        is_horizontal = orientation == "horizontal"
        start_side, end_side = _get_oriented_sides(orientation)
        has_border_start = self.parameters.borders[start_side]
        has_border_end = self.parameters.borders[end_side]
        shape_size = int(
            self.parameters.shape.width
            if is_horizontal
            else self.parameters.shape.length
        )
        range_start = 0 if has_border_start else 1
        range_end = shape_size + (1 if has_border_end else 0)
        range_end_max = range_end - 1
        return range_start, range_end, range_end_max

    def _build_line_template(self, orientation: Orientation) -> Rectangle:
        is_horizontal = orientation == "horizontal"
        width = (
            (self.parameters.shape.length * self.parameters.cell_size)
            if is_horizontal
            else self.parameters.gap
        )
        height = (
            self.parameters.gap
            if is_horizontal
            else (self.parameters.shape.width * self.parameters.cell_size)
        )
        return Rectangle(width, height, align=(Align.MIN, Align.MIN))

    def _build_lines(self, orientation: Orientation) -> Compound:
        # Pre-calculate constants
        is_horizontal = orientation == "horizontal"
        cell_size = self.parameters.cell_size
        half_gap = self.parameters.gap / 2
        range_start, range_end, range_end_max = self._compute_range_bounds(orientation)
        start_side, end_side = _get_oriented_sides(orientation)
        height = (
            self.parameters.horizontal_lines_height
            if is_horizontal
            else self.parameters.vertical_lines_height
        )
        line_template = self._build_line_template(orientation)
        axis = "Y" if is_horizontal else "X"

        # Helpers (for readability)
        compute_offset: Callable[[int], float] = (  # noqa: E731
            lambda index: index * cell_size
            - half_gap
            # Start border line (min X or Y axis)
            + (half_gap if self.parameters.borders[start_side] and index == 0 else 0)
            # End border line (max X or Y axis)
            - (
                half_gap
                if self.parameters.borders[end_side] and index == range_end_max
                else 0
            )
        )

        # Build lines using list comprehension with pre-calculated values
        lines = Sketch(
            [
                line_template.moved(Pos(**{axis: compute_offset(index)}))
                for index in range(range_start, range_end)
            ]
        )

        # Extrude the lines
        extruded = extrude(lines, amount=height)

        # If the lines are vertical, move them up by the difference in height between horizontal and vertical lines
        if is_horizontal:
            return extruded
        else:
            z_offset = (
                self.parameters.horizontal_lines_height
                - self.parameters.vertical_lines_height
            )
            return extruded.move(Location(Vector(X=0, Y=0, Z=z_offset)))

    def _add_diffuser_joint(self, grid: Compound) -> None:
        # Position the joint at the center above the grid
        center_x, center_y, _ = grid.center(CenterOf.BOUNDING_BOX).to_tuple()
        center_above = Vector(center_x, center_y, grid.bounding_box().max.Z)
        _ = RigidJoint("diffuser", grid, Location(center_above))

    def build(self) -> Compound:
        LOGGER.info("Building grid")

        grid = self._build_lines("horizontal") + self._build_lines("vertical")
        grid.color = self.parameters.color
        grid.label = "grid"

        self._add_diffuser_joint(grid)

        return grid
