from dataclasses import dataclass

from led_matrix_enclosure.dimensions import Dimension2D, Object2D


@dataclass
class LedMatrix:
    """A LED matrix."""

    #: Layout of the LED matrix, in pixels
    layout: Dimension2D
    #: Dimensions of a single pixel, in mm
    pixel_size: float
    #: Minimum height of the LED matrix, in mm
    #: Includes the PCB height + a capacitor between the LEDs
    min_height: float
    #: Connector positions
    connectors: tuple[Object2D, ...]

    def dimensions(self) -> Dimension2D:
        return Dimension2D(
            self.layout.length * self.pixel_size,
            self.layout.width * self.pixel_size,
        )
