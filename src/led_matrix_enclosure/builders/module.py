from dataclasses import dataclass
import logging
from pprint import pformat
from typing import cast
from operator import gt, lt

from build123d import Axis, CenterOf, Compound, Location, RigidJoint, Face, Shape

from led_matrix_enclosure.builders.chassis import ChassisBuilder
from led_matrix_enclosure.builders.lid import LidBuilder
from led_matrix_enclosure.helpers import get_compound_child
from led_matrix_enclosure.parameters.module import ModuleParameters
from led_matrix_enclosure.sides import Side


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModuleBuilder:
    """An enclosure module.

    Enclosures are composed of 1 or more modules.
    """

    parameters: ModuleParameters

    def _add_joints(self, module: Compound) -> None:
        """Add joints to the enclosure."""
        bottom = get_compound_child(get_compound_child(module, "chassis"), "bottom")
        bottom_faces = bottom.faces()

        for side in Side:
            if not self.parameters.border_presence[side]:
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
        LOGGER.debug(pformat(self.parameters))

        chassis = ChassisBuilder(self.parameters.chassis).build()
        lid = LidBuilder(self.parameters.lid).build()

        # Connect the chassis to the lid
        chassis.joints["lid"].connect_to(lid.joints["chassis"])  # pyright: ignore[reportUnknownMemberType]

        # Create the enclosure compound
        module = Compound(  # pyright: ignore[reportCallIssue]
            children=[chassis, lid],
            label=f"module:x={self.parameters.position.x},y={self.parameters.position.y}",
        )

        self._add_joints(module)

        return module
