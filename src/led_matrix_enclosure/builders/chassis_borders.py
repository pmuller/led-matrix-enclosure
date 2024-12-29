from dataclasses import dataclass
import logging

from build123d import Compound, Color, Box

from led_matrix_enclosure.builders.chassis_border_support_ledge import (
    ChassisBorderSupportLedgeBuilder,
)
from led_matrix_enclosure.builders.chassis_border_wire_slot import (
    ChassisBorderWireSlotsBuilder,
)
from led_matrix_enclosure.parameters.chassis import ChassisParameters
from led_matrix_enclosure.sides import Side


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisBordersBuilder:
    """Chassis borders."""

    parameters: ChassisParameters

    def _build_border(self, side: Side) -> Compound:
        LOGGER.debug("Building shell border: %s", side)

        match side:
            case Side.FRONT | Side.BACK:
                border_length = side_length = self.parameters.outer_dimensions.length
                border_width = self.parameters.borders.thickness
            case Side.LEFT | Side.RIGHT:
                border_length = self.parameters.borders.thickness
                border_width = side_length = self.parameters.outer_dimensions.width

        border = Box(
            border_length,
            border_width,
            self.parameters.inner_dimensions.height,
        )
        border += ChassisBorderSupportLedgeBuilder(
            side=side,
            size=self.parameters.borders.support_ledge_size,
            length=side_length,
            border_thickness=self.parameters.borders.thickness,
            border_presence=self.parameters.module.border_presence,
            inner_dimensions=self.parameters.inner_dimensions,
            z_offset=self.parameters.pillar.height
            - self.parameters.module.inner_dimensions.height / 2,
        ).build()

        if side == Side.BACK:
            border -= ChassisBorderWireSlotsBuilder(
                border_thickness=self.parameters.borders.thickness,
                border_length=side_length,
                slots=self.parameters.module.back_wire_slots,
                has_left_border=self.parameters.module.border_presence[Side.LEFT],
                border_height=self.parameters.inner_dimensions.height,
                ledge_size=self.parameters.borders.support_ledge_size,
            ).build()

        border.color = Color("black")
        border.label = f"border:{side}"

        return border.move(self.parameters.module.border_positions[side])

    def build(self) -> Compound | None:
        LOGGER.info("Building chassis borders")

        borders = [
            self._build_border(side)
            for side in self.parameters.module.border_presence.keys()
            if self.parameters.module.border_presence[side]
        ]

        if borders:
            compound = Compound(borders, label="borders")
            compound.color = Color("black")
            return compound
