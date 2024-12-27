from argparse import Namespace, ArgumentParser, _ActionsContainer  # pyright: ignore[reportPrivateUsage]
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Literal, Self, override, Callable

from build123d import (
    CenterOf,
    RigidJoint,
    Sketch,
    Pos,
    Rectangle,
    Align,
    Part,
    extrude,
    Color,
    Location,
    Vector,
)

from led_matrix_enclosure.dimensions import Dimension2D
from led_matrix_enclosure.sides import SideDict, Side


LOGGER = logging.getLogger(__name__)


Orientation = Literal["horizontal", "vertical"]


@dataclass
class PartialGridParameters:
    #: Height of the grid horizontal lines, in mm
    horizontal_lines_height: float
    #: Height of the grid vertical lines, in mm
    vertical_lines_height: float
    #: Gap between each cell, in mm
    gap: float
    #: Color of the grid lines
    color: Color

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> _ActionsContainer:
        group = parser.add_argument_group(title="Grid")
        _ = group.add_argument(
            "--grid-horizontal-lines-height",
            metavar="N",
            default=5,
            type=float,
            help="How tall the grid horizontal lines should be (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--grid-vertical-lines-height",
            metavar="N",
            default=3,  # XXX: This must be computed as grid_horizontal_lines_height - LedMatrix.min_height
            type=float,
            help="How tall the grid vertical lines should be (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--grid-gap",
            metavar="N",
            default=0.6,
            type=float,
            help="How much space between each cell should be (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--grid-color",
            metavar="COLOR",
            default=Color("black"),
            type=Color,
            help="Color of the grid lines (default: %(default)s)",
        )
        return group

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            horizontal_lines_height=arguments.grid_horizontal_lines_height,  # pyright: ignore[reportAny]
            vertical_lines_height=arguments.grid_vertical_lines_height,  # pyright: ignore[reportAny]
            gap=arguments.grid_gap,  # pyright: ignore[reportAny]
            color=arguments.grid_color,  # pyright: ignore[reportAny]
        )

    @property
    def height(self) -> float:
        return max(self.horizontal_lines_height, self.vertical_lines_height)


def _get_oriented_sides(orientation: Orientation) -> tuple[Side, Side]:
    match orientation:
        case "horizontal":
            return Side.FRONT, Side.BACK
        case "vertical":
            return Side.LEFT, Side.RIGHT


@dataclass
class GridParameters(PartialGridParameters):
    #: Size of each cell, in mm
    cell_size: float

    @classmethod
    @override
    def add_cli_arguments(cls, parser: ArgumentParser) -> _ActionsContainer:
        group = super().add_cli_arguments(parser)
        _ = group.add_argument(
            "--grid-cell-size",
            metavar="N",
            default=10.0,
            type=float,
            help="How big each cell should be (unit: mm, default: %(default)s)",
        )
        return group

    @classmethod
    @override
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            horizontal_lines_height=arguments.grid_horizontal_lines_height,  # pyright: ignore[reportAny]
            vertical_lines_height=arguments.grid_vertical_lines_height,  # pyright: ignore[reportAny]
            cell_size=arguments.grid_cell_size,  # pyright: ignore[reportAny]
            gap=arguments.grid_gap,  # pyright: ignore[reportAny]
            color=arguments.grid_color,  # pyright: ignore[reportAny]
        )


@dataclass
class Grid(GridParameters):
    """A grid."""

    #: Shape of the grid, in cells
    shape: Dimension2D
    #: Borders to add to the grid
    borders: SideDict

    @classmethod
    @override
    def add_cli_arguments(cls, parser: ArgumentParser) -> _ActionsContainer:
        group = super().add_cli_arguments(parser)
        _ = group.add_argument(
            "--grid-length",
            metavar="N",
            required=True,
            type=int,
            help="How many cells wide the grid should be (mandatory)",
        )
        _ = group.add_argument(
            "--grid-width",
            metavar="N",
            required=True,
            type=int,
            help="How many cells high the grid should be (mandatory)",
        )
        SideDict.add_cli_argument(
            group,
            "--add-grid-border",
            dest="grid_borders",
            default=False,
            help="Add a border to the grid (default: %(default)s)",
        )
        return group

    @classmethod
    @override
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            shape=Dimension2D(
                length=arguments.grid_length,  # pyright: ignore[reportAny]
                width=arguments.grid_width,  # pyright: ignore[reportAny]
            ),
            horizontal_lines_height=arguments.grid_horizontal_lines_height,  # pyright: ignore[reportAny]
            vertical_lines_height=arguments.grid_vertical_lines_height,  # pyright: ignore[reportAny]
            cell_size=arguments.grid_cell_size,  # pyright: ignore[reportAny]
            gap=arguments.grid_gap,  # pyright: ignore[reportAny]
            borders=arguments.grid_borders,  # pyright: ignore[reportAny]
            color=arguments.grid_color,  # pyright: ignore[reportAny]
        )

    @classmethod
    def from_parameters(
        cls,
        parameters: PartialGridParameters,
        shape: Dimension2D,
        borders: SideDict,
        cell_size: float,
    ) -> Self:
        return cls(
            horizontal_lines_height=parameters.horizontal_lines_height,
            vertical_lines_height=parameters.vertical_lines_height,
            cell_size=cell_size,
            gap=parameters.gap,
            color=parameters.color,
            shape=shape,
            borders=borders,
        )

    def _compute_range_bounds(self, orientation: Orientation) -> tuple[int, int, int]:
        is_horizontal = orientation == "horizontal"
        start_side, end_side = _get_oriented_sides(orientation)
        has_border_start = self.borders[start_side]
        has_border_end = self.borders[end_side]
        shape_size = int(self.shape.width if is_horizontal else self.shape.length)
        range_start = 0 if has_border_start else 1
        range_end = shape_size + (1 if has_border_end else 0)
        range_end_max = range_end - 1
        return range_start, range_end, range_end_max

    def _build_line_template(self, orientation: Orientation) -> Rectangle:
        is_horizontal = orientation == "horizontal"
        width = (self.shape.length * self.cell_size) if is_horizontal else self.gap
        height = self.gap if is_horizontal else (self.shape.width * self.cell_size)
        return Rectangle(width, height, align=(Align.MIN, Align.MIN))

    def _build_lines(self, orientation: Orientation) -> Part:
        # Pre-calculate constants
        is_horizontal = orientation == "horizontal"
        cell_size = self.cell_size
        half_gap = self.gap / 2
        range_start, range_end, range_end_max = self._compute_range_bounds(orientation)
        start_side, end_side = _get_oriented_sides(orientation)
        height = (
            self.horizontal_lines_height
            if is_horizontal
            else self.vertical_lines_height
        )
        line_template = self._build_line_template(orientation)
        axis = "Y" if is_horizontal else "X"

        # Helpers (for readability)
        compute_offset: Callable[[int], float] = (  # noqa: E731
            lambda index: index * cell_size
            - half_gap
            # Start border line (min X or Y axis)
            + (half_gap if self.borders[start_side] and index == 0 else 0)
            # End border line (max X or Y axis)
            - (half_gap if self.borders[end_side] and index == range_end_max else 0)
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
            z_offset = self.horizontal_lines_height - self.vertical_lines_height
            return extruded.move(Location(Vector(X=0, Y=0, Z=z_offset)))

    def _add_diffuser_joint(self, grid: Part) -> None:
        # Position the joint at the center above the grid
        center_x, center_y, _ = grid.center(CenterOf.BOUNDING_BOX).to_tuple()
        center_above = Vector(center_x, center_y, grid.bounding_box().max.Z)
        _ = RigidJoint("diffuser", grid, Location(center_above))

    def build(self) -> Part:
        LOGGER.info("Building grid")
        LOGGER.debug("%s", pformat(self))

        grid = self._build_lines("horizontal") + self._build_lines("vertical")
        grid.color = self.color
        grid.label = "grid"
        self._add_diffuser_joint(grid)
        return grid
