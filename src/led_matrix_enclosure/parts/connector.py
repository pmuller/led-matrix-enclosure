from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self

from build123d import Box, Color, Cylinder, Part, Pos, chamfer

from led_matrix_enclosure.dimensions import Dimension3D


LOGGER = logging.getLogger(__name__)


@dataclass
class ConnectorParameters:
    #: Hole diameter, in mm
    hole_diameter: float
    #: Hole tolerance, in mm
    hole_tolerance: float
    #: Thickness of the wall, in mm
    wall_thickness: float
    #: Chamfer length, in mm
    chamfer_length: float
    #: Chamfer tolerance, in mm
    chamfer_tolerance: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Connector")
        _ = group.add_argument(
            "--connector-hole-diameter",
            metavar="N",
            type=float,
            default=3,
            help="Connector screw hole diameter (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-hole-tolerance",
            metavar="N",
            type=float,
            default=0.1,
            help="Connector screw hole tolerance (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-wall-thickness",
            metavar="N",
            type=float,
            default=2,
            help="Connector wall thickness (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-chamfer-length",
            metavar="N",
            type=float,
            default=2,
            help="Connector chamfer length (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-chamfer-tolerance",
            metavar="N",
            type=float,
            default=0.1,
            help="Connector chamfer tolerance (unit: mm, default: %(default)s)",
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            hole_diameter=arguments.connector_hole_diameter,  # pyright: ignore[reportAny]
            hole_tolerance=arguments.connector_hole_tolerance,  # pyright: ignore[reportAny]
            wall_thickness=arguments.connector_wall_thickness,  # pyright: ignore[reportAny]
            chamfer_length=arguments.connector_chamfer_length,  # pyright: ignore[reportAny]
            chamfer_tolerance=arguments.connector_chamfer_tolerance,  # pyright: ignore[reportAny]
        )


@dataclass
class Connector(ConnectorParameters):
    #: Size of the connector, in mm
    size: float

    @classmethod
    def from_parameters(cls, parameters: ConnectorParameters, size: float) -> Self:
        return cls(
            hole_diameter=parameters.hole_diameter,
            hole_tolerance=parameters.hole_tolerance,
            wall_thickness=parameters.wall_thickness,
            chamfer_length=parameters.chamfer_length,
            chamfer_tolerance=parameters.chamfer_tolerance,
            size=size,
        )

    def compute_outer_dimensions(self) -> Dimension3D:
        return Dimension3D(
            self.size,
            self.size,
            self.wall_thickness + self.chamfer_length,
        )

    def build(self) -> Part:
        LOGGER.info("Building connector")
        LOGGER.debug("%s", pformat(self))

        hole_radius = (self.hole_diameter + self.hole_tolerance) / 2
        LOGGER.debug("Hole radius: %s", hole_radius)

        dimensions = self.compute_outer_dimensions()
        connector = Box(dimensions.length, dimensions.width, dimensions.height)
        connector -= Cylinder(hole_radius, dimensions.height)

        # Build support (inverted part that will be subtracted from the connector)
        support_height = self.chamfer_length + self.chamfer_tolerance
        support = Box(dimensions.length, dimensions.width, support_height)

        # Align connector and support bottom
        support = support.move(
            Pos(Z=connector.bounding_box().min.Z - support.bounding_box().min.Z)
        )

        # Chamfer the support
        support_chamfered_edges = support.edges().filter_by(
            lambda shape: shape.center().Z == support.bounding_box().max.Z
        )

        # Subtract the chamfered support
        connector -= chamfer(support_chamfered_edges, self.chamfer_length)

        # Set color and label
        connector.color = Color("black")
        connector.label = "connector"

        return connector
