from dataclasses import dataclass
import logging

from build123d import Compound, RigidJoint, Location

from led_matrix_enclosure.builders.lid_grid import LidGridBuilder
from led_matrix_enclosure.builders.lid_diffuser import LidDiffuserBuilder
from led_matrix_enclosure.parameters.lid import LidParameters


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LidBuilder:
    parameters: LidParameters
    name: str = "lid"

    def _add_chassis_joint(self, lid: Compound, diffuser: Compound) -> None:
        # Add chassis joint to the bottom top left corner of the diffuser
        _ = RigidJoint("chassis", lid, Location(diffuser.bounding_box().min))

    def build(self) -> Compound:
        LOGGER.info("Building lid")

        diffuser = LidDiffuserBuilder(self.parameters.diffuser).build()
        grid = LidGridBuilder(self.parameters.grid).build()

        diffuser.joints["grid"].connect_to(grid.joints["diffuser"])  # pyright: ignore[reportUnknownMemberType]

        lid = Compound(children=[diffuser, grid], label="lid")  # pyright: ignore[reportCallIssue]

        self._add_chassis_joint(lid, diffuser)

        return lid
