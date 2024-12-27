from dataclasses import dataclass
import logging
from pprint import pformat

from build123d import Compound, Color, Box, Pos

from led_matrix_enclosure.dimensions import Dimension3D, Object2D
from led_matrix_enclosure.parts.chassis_border_support_ledge import ChassisBorderSupportLedge
from led_matrix_enclosure.parts.chassis_border_wire_slot import ChassisBorderWireSlots
from led_matrix_enclosure.sides import Side, SideDict


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisBorders:
    """Chassis borders."""

    #: Inner dimensions of the chassis
    inner_dimensions: Dimension3D
    #: Outer dimensions of the chassis
    outer_dimensions: Dimension3D
    #: Thickness of the chassis borders
    border_thickness: float
    #: Radius of the chassis borders fillet
    border_radius: float
    #: Positions of the chassis borders
    border_positions: dict[Side, Pos]
    #: Presence of the chassis borders
    border_presence: SideDict
    #: Support ledge for LED matrices
    ledge_size: float
    #: Z-offset of the ledge
    ledge_z_offset: float
    #: Back wire slots
    back_wire_slots: tuple[Object2D, ...] = tuple()

    def _build_border(self, side: Side) -> Compound:
        LOGGER.debug("Building shell border: %s", side)

        match side:
            case Side.FRONT | Side.BACK:
                border_length = side_length = self.outer_dimensions.length
                border_width = self.border_thickness
            case Side.LEFT | Side.RIGHT:
                border_length = self.border_thickness
                border_width = side_length = self.outer_dimensions.width

        border = Box(border_length, border_width, self.inner_dimensions.height)
        border += ChassisBorderSupportLedge(
            side=side,
            size=self.ledge_size,
            length=side_length,
            border_thickness=self.border_thickness,
            border_presence=self.border_presence,
            inner_dimensions=self.inner_dimensions,
            z_offset=self.ledge_z_offset - self.inner_dimensions.height / 2,
        ).build()

        if side == Side.BACK:
            border -= ChassisBorderWireSlots(
                border_thickness=self.border_thickness,
                border_length=side_length,
                slots=self.back_wire_slots,
                has_left_border=self.border_presence[Side.LEFT],
                border_height=self.inner_dimensions.height,
                ledge_size=self.ledge_size,
            ).build()

        border.color = Color("black")
        border.label = f"border:{side}"

        return border.move(self.border_positions[side])

    def build(self) -> Compound | None:
        LOGGER.info("Building chassis borders")
        LOGGER.debug("%s", pformat(self))

        borders = [
            self._build_border(side)
            for side in self.border_presence.keys()
            if self.border_presence[side]
        ]

        if borders:
            compound = Compound(borders, label="borders")
            compound.color = Color("black")
            return compound
