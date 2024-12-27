from led_matrix_enclosure.dimensions import Dimension2D, Object2D, Position2D
from led_matrix_enclosure.models.led_matrix import LedMatrix


LED_MATRIX_PROFILES: dict[str, LedMatrix] = {
    "8x8": LedMatrix(
        layout=Dimension2D(8, 8),
        pixel_size=10,
        min_height=1.15,
        connectors=(
            # Input connector
            Object2D(
                Dimension2D(15, 50),
                Position2D(12, 15),
            ),
            # Power connector
            Object2D(
                Dimension2D(15, 50),
                Position2D(32, 15),
            ),
            # Output connector
            Object2D(
                Dimension2D(15, 50),
                Position2D(52, 15),
            ),
        ),
    ),
    "16x16": LedMatrix(
        layout=Dimension2D(16, 16),
        pixel_size=10,
        min_height=1.25,
        connectors=(
            # Input connector
            Object2D(
                Dimension2D(20, 100),
                Position2D(30, 30),
            ),
            # Power connector
            Object2D(
                Dimension2D(20, 100),
                Position2D(70, 30),
            ),
            # Output connector
            Object2D(
                Dimension2D(20, 100),
                Position2D(110, 30),
            ),
        ),
    ),
    "32x8": LedMatrix(
        layout=Dimension2D(32, 8),
        pixel_size=10,
        min_height=1.15,
        connectors=(
            # Input connector
            Object2D(
                Dimension2D(20, 50),
                Position2D(30, 15),
            ),
            # Power connector
            Object2D(
                Dimension2D(20, 50),
                Position2D(150, 15),
            ),
            # Output connector
            Object2D(
                Dimension2D(20, 50),
                Position2D(280, 15),
            ),
        ),
    ),
}
