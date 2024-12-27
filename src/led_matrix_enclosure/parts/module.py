from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self, cast
from operator import gt, lt

from build123d import Axis, CenterOf, Compound, Location, RigidJoint, Face, Shape

from led_matrix_enclosure.dimensions import Dimension2D, Dimension3D, Object2D
from led_matrix_enclosure.helpers import get_compound_child
from led_matrix_enclosure.parts.chassis import Chassis, ChassisParameters
from led_matrix_enclosure.parts.diffuser import Diffuser
from led_matrix_enclosure.parts.grid import Grid
from led_matrix_enclosure.parts.lid import Lid, PartialLidParameters
from led_matrix_enclosure.sides import SideDict, Side


LOGGER = logging.getLogger(__name__)


@dataclass
class ModuleParameters:
    """Parameters for an enclosure module."""

    #: Chassis parameters
    chassis: ChassisParameters
    #: Lid parameters
    lid: PartialLidParameters
    #: Module inner dimensions
    inner_dimensions: Dimension3D
    #: Module grid cell size
    grid_cell_size: float
    #: Module grid shape
    grid_shape: Dimension2D


@dataclass
class Module(ModuleParameters):
    """An enclosure module.

    Enclosures are composed of 1 or more modules.
    """

    #: Module border presence
    border_presence: SideDict
    #: Enclosure X position
    x: int
    #: Enclosure Y position
    y: int
    #: Back wire slots
    back_wire_slots: tuple[Object2D, ...]
    #: Panel connectors positions
    panel_connectors: tuple[Object2D, ...]

    @classmethod
    def from_parameters(
        cls,
        parameters: ModuleParameters,
        border_presence: SideDict,
        x: int,
        y: int,
        back_wire_slots: tuple[Object2D, ...],
        panel_connectors: tuple[Object2D, ...],
    ) -> Self:
        return cls(
            chassis=parameters.chassis,
            lid=parameters.lid,
            inner_dimensions=parameters.inner_dimensions,
            grid_cell_size=parameters.grid_cell_size,
            grid_shape=parameters.grid_shape,
            border_presence=border_presence,
            x=x,
            y=y,
            back_wire_slots=back_wire_slots,
            panel_connectors=panel_connectors,
        )

    def _add_joints(self, module: Compound) -> None:
        """Add joints to the enclosure."""
        bottom = get_compound_child(get_compound_child(module, "chassis"), "bottom")
        bottom_faces = bottom.faces()

        for side in Side:
            if not self.border_presence[side]:
                axis = "X" if side.is_horizontal else "Y"
                faces = bottom_faces.filter_by(cast(Axis, getattr(Axis, axis)))
                operator = lt if side.is_start else gt

                def predicate(shape: Shape) -> bool:
                    face = cast(Face, shape)
                    value: float = getattr(face.normal_at(), axis)
                    return cast(bool, operator(value, 0))

                vector = faces.filter_by(predicate).first.center(CenterOf.BOUNDING_BOX)
                _ = RigidJoint(str(side), module, Location(vector))

    def build(self) -> Compound:
        LOGGER.info("Building module")
        LOGGER.debug("%s", pformat(self))

        chassis = Chassis.from_parameters(
            parameters=self.chassis,
            inner_dimensions=self.inner_dimensions,
            border_presence=self.border_presence,
            back_wire_slots=self.back_wire_slots,
            panel_connectors=self.panel_connectors,
        ).build()
        lid = Lid(
            Grid.from_parameters(
                parameters=self.lid.grid,
                shape=self.grid_shape,
                # Always add back and right borders to the grid,
                # to compensate for the absence of the left and front borders on neighboring modules
                borders=self.border_presence + Side.BACK + Side.RIGHT,
                cell_size=self.grid_cell_size,
            ),
            Diffuser.from_parameters(
                parameters=self.lid.diffuser,
                grid_dimensions=self.inner_dimensions.to_2d(),
                margins=self.border_presence,
                margin_size=self.chassis.border_thickness,
            ),
        ).build()

        # Connect the chassis to the lid
        chassis.joints["lid"].connect_to(lid.joints["chassis"])  # pyright: ignore[reportUnknownMemberType]

        # Create the enclosure compound
        module = Compound(  # pyright: ignore[reportCallIssue]
            children=[chassis, lid],
            label=f"module:x={self.x},y={self.y}",
        )

        self._add_joints(module)

        return module
