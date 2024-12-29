from dataclasses import dataclass
import logging
from pprint import pformat

from build123d import (
    Axis,
    Compound,
    Shape,
    Vector,
    RigidJoint,
    Location,
    fillet,
    ShapePredicate,
)

from led_matrix_enclosure.builders.chassis_borders import ChassisBordersBuilder
from led_matrix_enclosure.builders.chassis_module_connectors import (
    ChassisModuleConnectorsBuilder,
)
from led_matrix_enclosure.dimensions import Dimension3D
from led_matrix_enclosure.parameters.chassis import ChassisParameters
from led_matrix_enclosure.builders.chassis_bottom import ChassisBottomBuilder
from led_matrix_enclosure.builders.chassis_pillars import ChassisPillarsBuilder
from led_matrix_enclosure.sides import Side, SideDict

LOGGER = logging.getLogger(__name__)


def _build_is_outer_edge_predicate(
    dimensions: Dimension3D,
    border_presence: SideDict,
) -> ShapePredicate:
    def is_outer_edge(shape: Shape) -> bool:
        half_outer_length = dimensions.length / 2
        half_outer_width = dimensions.width / 2
        center = shape.center()
        x_position = center.X
        y_position = center.Y
        is_corner = (  # Is it an outer corner?
            abs(abs(x_position) - half_outer_length) == 0
            and abs(abs(y_position) - half_outer_width) == 0
        )

        if not is_corner:
            return False

        # Check if both adjacent sides exist
        return (
            border_presence[Side.LEFT if x_position < 0 else Side.RIGHT]
            and border_presence[Side.FRONT if y_position < 0 else Side.BACK]
        )

    return is_outer_edge


@dataclass(frozen=True)
class ChassisBuilder:
    """A LED panel chassis.

    This is the bottom part of the LED panel enclosure.
    """

    #: Builder parameters
    parameters: ChassisParameters

    #: Name of the part
    name: str = "chassis"

    def _add_lid_joint(self, chassis: Compound, bottom: Compound) -> None:
        bounding_box = bottom.bounding_box()
        z_offset = (
            self.parameters.inner_dimensions.height
            + self.parameters.bottom.thickness / 2
        )
        vector = Vector(bounding_box.min.X, bounding_box.min.Y, z_offset)
        _ = RigidJoint("lid", chassis, Location(vector))

    def _fillet_outer_edges(self, compound: Compound) -> Compound:
        outer_vertical_edges = (
            compound.edges()
            .filter_by(Axis.Z)
            .filter_by(
                _build_is_outer_edge_predicate(
                    self.parameters.outer_dimensions,
                    self.parameters.module.border_presence,
                )
            )
        )

        if len(outer_vertical_edges) > 0:
            LOGGER.info("Filleting %d outer vertical edges", len(outer_vertical_edges))
            color = compound.color
            label = compound.label
            compound = fillet(
                outer_vertical_edges,
                self.parameters.borders.radius,
            )
            compound.color = color
            compound.label = label
            return compound
        else:
            LOGGER.info("No outer vertical edges to fillet")
            return compound

    def build(self) -> Compound:
        LOGGER.info("Building chassis")
        LOGGER.debug("%s", pformat(self.parameters))

        bottom = self._fillet_outer_edges(ChassisBottomBuilder(self.parameters).build())
        connectors = ChassisModuleConnectorsBuilder(self.parameters).build()
        borders = ChassisBordersBuilder(self.parameters).build()
        pillars = ChassisPillarsBuilder(self.parameters).build()

        children: list[Compound] = [bottom]

        if connectors is not None:
            children.append(connectors)

        if pillars is None:
            LOGGER.warning(
                "No pillars to add to the chassis. Is the chassis too small?"
            )
        else:
            children.append(pillars)

        if borders is not None:
            children.append(self._fillet_outer_edges(borders))

        chassis = Compound(children=children, label="chassis")  # pyright: ignore[reportCallIssue]
        self._add_lid_joint(chassis, bottom)

        return chassis
