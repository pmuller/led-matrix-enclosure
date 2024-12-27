from dataclasses import dataclass
import logging
from pprint import pformat
from build123d import Box, Color, Compound

from led_matrix_enclosure.dimensions import Dimension3D


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisBottom:
    #: Dimensions of the chassis
    dimensions: Dimension3D
    #: Bottom thickness
    thickness: float

    def build(self) -> Compound:
        LOGGER.info("Building chassis bottom")
        LOGGER.debug("%s", pformat(self))

        bottom = Box(
            length=self.dimensions.length,
            width=self.dimensions.width,
            height=self.thickness,
        )
        bottom.color = Color("black")
        bottom.label = "bottom"
        return bottom
