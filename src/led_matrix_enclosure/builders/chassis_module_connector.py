from dataclasses import dataclass
import logging

from build123d import Box, Color, Cylinder, Part, Pos, chamfer

from led_matrix_enclosure.dimensions import Dimension3D
from led_matrix_enclosure.parameters.chassis import ChassisParameters


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisModuleConnectorBuilder:
    """Builds a single chassis module connector."""

    parameters: ChassisParameters

    def compute_outer_dimensions(self) -> Dimension3D:
        size = self.parameters.pillar.height
        height = (
            self.parameters.module_connectors.wall_thickness
            + self.parameters.module_connectors.chamfer_length
        )
        return Dimension3D(size, size, height)

    def build(self) -> Part:
        LOGGER.info("Building chassis connector")
        parameters = self.parameters.module_connectors

        hole_radius = (parameters.hole_diameter + parameters.hole_tolerance) / 2
        LOGGER.debug("Hole radius: %s", hole_radius)

        dimensions = self.compute_outer_dimensions()
        connector = Box(dimensions.length, dimensions.width, dimensions.height)
        connector -= Cylinder(hole_radius, dimensions.height)

        # Build support (inverted part that will be subtracted from the connector)
        support_height = parameters.chamfer_length + parameters.chamfer_tolerance
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
        connector -= chamfer(support_chamfered_edges, parameters.chamfer_length)

        # Set color and label
        connector.color = Color("black")
        connector.label = "connector"

        return connector
