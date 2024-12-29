from dataclasses import dataclass
import logging

from build123d import Color, Part, Cylinder, Cone, Pos

from led_matrix_enclosure.parameters.chassis_pillar import ChassisPillarParameters
from led_matrix_enclosure.dimensions import Dimension3D


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChassisPillarBuilder:
    """Builder for a single chassis pillar."""

    #: Pillar parameters
    parameters: ChassisPillarParameters

    def compute_outer_dimensions(self) -> Dimension3D:
        return Dimension3D(
            length=self.parameters.diameter,
            width=self.parameters.diameter,
            height=self.parameters.height,
        )

    def build(self) -> Part:
        LOGGER.info("Building pillar")

        base_position = Pos(
            Z=-(self.parameters.height - self.parameters.base_height) / 2
        )
        base = Cone(
            self.parameters.base_diameter / 2,
            self.parameters.diameter / 2,
            self.parameters.base_height,
        )

        main = Cylinder(self.parameters.diameter / 2, self.parameters.height)

        pillar = main + base.move(base_position)
        pillar.color = Color("black")
        pillar.label = "pillar"

        return pillar
