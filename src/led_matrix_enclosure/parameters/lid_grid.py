from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Self

from build123d import Color

from led_matrix_enclosure.dimensions import Dimension2D
from led_matrix_enclosure.sides import SideDict


@dataclass(frozen=True)
class LidGridCliParameters:
    #: Height of the grid horizontal lines, in mm
    horizontal_lines_height: float
    #: Height of the grid vertical lines, in mm
    vertical_lines_height: float
    #: Gap between each cell, in mm
    gap: float
    #: Color of the grid lines
    color: Color

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
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
            default=3,
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

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            horizontal_lines_height=arguments.grid_horizontal_lines_height,  # pyright: ignore[reportAny]
            vertical_lines_height=arguments.grid_vertical_lines_height,  # pyright: ignore[reportAny]
            gap=arguments.grid_gap,  # pyright: ignore[reportAny]
            color=arguments.grid_color,  # pyright: ignore[reportAny]
        )

    @property
    def max_line_height(self) -> float:
        return max(self.horizontal_lines_height, self.vertical_lines_height)


@dataclass(frozen=True)
class LidGridParameters(LidGridCliParameters):
    #: Shape of the grid, in cells
    shape: Dimension2D
    #: Borders to add to the grid
    borders: SideDict
    #: Size of each cell, in mm
    cell_size: float

    @classmethod
    def from_parameters(
        cls,
        parameters: LidGridCliParameters,
        shape: Dimension2D,
        borders: SideDict,
        cell_size: float,
    ) -> Self:
        return cls(
            # CLI parameters
            horizontal_lines_height=parameters.horizontal_lines_height,
            vertical_lines_height=parameters.vertical_lines_height,
            gap=parameters.gap,
            color=parameters.color,
            # Own parameters
            cell_size=cell_size,
            shape=shape,
            borders=borders,
        )
