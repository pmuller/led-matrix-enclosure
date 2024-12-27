from dataclasses import dataclass

from build123d import Compound, Box, Location, Vector

from led_matrix_enclosure.dimensions import Object2D


@dataclass
class ChassisBorderWireSlots:
    """Chassis border wire slots."""

    #: Thickness of the border
    border_thickness: float
    #: Border length
    border_length: float
    #: Border height
    border_height: float
    #: Back wire slots
    slots: tuple[Object2D, ...]
    #: Account for the left border presence?
    has_left_border: bool
    #: Ledge size
    ledge_size: float
    #: Slot height, in mm
    #: Must account for size of female JST connector
    height: float = 9.5

    def build(self) -> list[Compound]:
        slots: list[Compound] = []

        for slot_data in self.slots:
            border_offset = self.border_thickness if self.has_left_border else 0
            position_x = (
                slot_data.position.x
                - (self.border_length - border_offset) / 2
                + border_offset
                + slot_data.dimensions.length / 2
            )

            slot = Box(
                slot_data.dimensions.length,
                self.border_thickness + self.ledge_size,
                self.height,
            )

            location = Location(
                Vector(
                    X=position_x,
                    Y=-self.ledge_size / 2,
                    Z=self.height / 2 - self.border_height / 2,
                ),
            )

            slots.append(slot.move(location))

        return slots
