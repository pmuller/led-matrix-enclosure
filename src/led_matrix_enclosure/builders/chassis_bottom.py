from dataclasses import dataclass
import logging
from build123d import Box, Color, Compound

from led_matrix_enclosure.parameters.chassis import ChassisParameters


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisBottomBuilder:
    """Chassis bottom."""

    parameters: ChassisParameters

    def build(self) -> Compound:
        LOGGER.info("Building chassis bottom")

        bottom = Box(
            length=self.parameters.outer_dimensions.length,
            width=self.parameters.outer_dimensions.width,
            height=self.parameters.bottom.thickness,
        )
        bottom.color = Color("black")
        bottom.label = "bottom"

        return bottom
