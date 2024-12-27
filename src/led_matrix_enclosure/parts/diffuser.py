from argparse import Namespace, ArgumentParser, _ActionsContainer  # pyright: ignore[reportPrivateUsage]
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self, override, cast

from build123d import (
    Align,
    CenterOf,
    Edge,
    Part,
    Box,
    Color,
    Axis,
    ShapeList,
    fillet,
    RigidJoint,
    Location,
    Vector,
)


from led_matrix_enclosure.corners import Corner2DPredicate, TWO_DIMENSIONAL_CORNERS
from led_matrix_enclosure.dimensions import Dimension2D
from led_matrix_enclosure.sides import Side, SideDict


LOGGER = logging.getLogger(__name__)


@dataclass
class PartialDiffuserParameters:
    #: Thickness of the diffuser, in mm
    thickness: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> _ActionsContainer:
        group = parser.add_argument_group(title="Diffuser")
        _ = group.add_argument(
            "--diffuser-thickness",
            metavar="N",
            default=0.3,
            type=float,
            help="How thick the diffuser should be (unit: mm, default: %(default)s)",
        )
        return group

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            thickness=arguments.diffuser_thickness,  # pyright: ignore[reportAny]
        )


@dataclass
class DiffuserParameters(PartialDiffuserParameters):
    #: Diffuser margin around the grid, in mm
    margin_size: float

    @classmethod
    @override
    def add_cli_arguments(cls, parser: ArgumentParser) -> _ActionsContainer:
        group = super().add_cli_arguments(parser)
        _ = group.add_argument(
            "--diffuser-margin",
            metavar="N",
            default=1.0,
            type=float,
            help="How much space to leave around the grid (unit: mm, default: %(default)s)",
        )
        return group

    @classmethod
    @override
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            thickness=arguments.diffuser_thickness,  # pyright: ignore[reportAny]
            margin_size=arguments.diffuser_margin,  # pyright: ignore[reportAny]
        )


@dataclass
class Diffuser(DiffuserParameters):
    """A LED panel diffuser."""

    #: Dimensions of the underlying grid, in mm
    grid_dimensions: Dimension2D
    #: Margins to add to the diffuser
    margins: SideDict

    @classmethod
    @override
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            thickness=arguments.diffuser_thickness,  # pyright: ignore[reportAny]
            margin_size=arguments.diffuser_margin,  # pyright: ignore[reportAny]
            margins=arguments.diffuser_margins,  # pyright: ignore[reportAny]
            grid_dimensions=Dimension2D(
                length=arguments.grid_length * arguments.grid_cell_size,  # pyright: ignore[reportAny]
                width=arguments.grid_width * arguments.grid_cell_size,  # pyright: ignore[reportAny]
            ),
        )

    @classmethod
    def from_parameters(
        cls,
        parameters: PartialDiffuserParameters,
        grid_dimensions: Dimension2D,
        margins: SideDict,
        margin_size: float,
    ) -> Self:
        return cls(
            margin_size=margin_size,
            thickness=parameters.thickness,
            grid_dimensions=grid_dimensions,
            margins=margins,
        )

    def _get_bottom_center(self, diffuser: Part) -> Vector:
        center_x, center_y, _ = diffuser.center(CenterOf.BOUNDING_BOX).to_tuple()

        # Move the center according to the margins
        if not self.margins[Side.LEFT]:
            center_x -= self.margin_size / 2
        if not self.margins[Side.RIGHT]:
            center_x += self.margin_size / 2
        if not self.margins[Side.BACK]:
            center_y += self.margin_size / 2
        if not self.margins[Side.FRONT]:
            center_y -= self.margin_size / 2

        return Vector(center_x, center_y, diffuser.bounding_box().min.Z)

    def _add_grid_joint(self, diffuser: Part) -> None:
        _ = RigidJoint("grid", diffuser, Location(self._get_bottom_center(diffuser)))

    def _fillet(self, diffuser: Part) -> Part:
        z_edges = diffuser.edges().filter_by(Axis.Z)
        fillet_edges: ShapeList[Edge] = ShapeList()

        for corner in TWO_DIMENSIONAL_CORNERS:
            side_1, side_2 = corner

            if self.margins[side_1] and self.margins[side_2]:
                fillet_edges.extend(z_edges.filter_by(Corner2DPredicate(corner)))

        return (
            cast(Part, fillet(fillet_edges, self.margin_size))
            if fillet_edges
            else diffuser
        )

    def build(self) -> Part:
        LOGGER.info("Building diffuser")
        LOGGER.debug("%s", pformat(self))

        length = (
            self.grid_dimensions.length
            + len(self.margins.horizontal) * self.margin_size
        )
        width = (
            self.grid_dimensions.width + len(self.margins.vertical) * self.margin_size
        )
        diffuser = Box(
            length,
            width,
            height=self.thickness,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
        diffuser = self._fillet(diffuser)
        diffuser.color = Color("White", alpha=0.5)
        diffuser.label = "diffuser"
        self._add_grid_joint(diffuser)
        return diffuser
