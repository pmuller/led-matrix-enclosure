import pytest

from led_matrix_enclosure.dimensions import Dimension2D, Object2D, Position2D
from led_matrix_enclosure.models.composite_led_matrix import (
    CompositeLedMatrix,
    ConnectorLayoutGrid,
    ConnectorLayoutRow,
    LedMatrixLayoutGrid,
)
from led_matrix_enclosure.profiles.led_matrix import LED_MATRIX_PROFILES


@pytest.mark.parametrize(
    ("layout", "slots"),
    [
        (
            ((LED_MATRIX_PROFILES["8x8"],),),
            (
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(12, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(32, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(52, 15),
                ),
            ),
        ),
        (
            ((LED_MATRIX_PROFILES["8x8"], LED_MATRIX_PROFILES["8x8"]),),
            (
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(12, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(32, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(52, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(92, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(112, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(132, 15),
                ),
            ),
        ),
        (
            (
                (LED_MATRIX_PROFILES["8x8"], LED_MATRIX_PROFILES["8x8"]),
                (LED_MATRIX_PROFILES["8x8"], LED_MATRIX_PROFILES["8x8"]),
            ),
            (
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(12, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(32, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(52, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(92, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(112, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(132, 15),
                ),
            ),
        ),
    ],
)
def test_back_wire_slots(layout: LedMatrixLayoutGrid, slots: ConnectorLayoutRow):
    assert CompositeLedMatrix(layout).back_wire_slots == slots


@pytest.mark.parametrize(
    ("layout", "offset", "length", "slots"),
    [
        (
            (
                (LED_MATRIX_PROFILES["8x8"],),
                (LED_MATRIX_PROFILES["8x8"],),
            ),
            0,
            40,
            (
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(12, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(32, 15),
                ),
            ),
        ),
        (
            (
                (LED_MATRIX_PROFILES["8x8"],),
                (LED_MATRIX_PROFILES["8x8"],),
            ),
            40,
            40,
            (
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(-8, 15),
                ),
                Object2D(
                    Dimension2D(15, 50),
                    Position2D(12, 15),
                ),
            ),
        ),
    ],
)
def test_scoped_back_wire_slots(
    layout: LedMatrixLayoutGrid,
    offset: float,
    length: float,
    slots: ConnectorLayoutRow,
):
    assert CompositeLedMatrix(layout).scoped_back_wire_slots(offset, length) == slots


@pytest.mark.parametrize(
    ("layout", "connectors"),
    [
        (
            ((LED_MATRIX_PROFILES["8x8"],),),
            (
                (
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(12, 15),
                    ),
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(32, 15),
                    ),
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(52, 15),
                    ),
                ),
            ),
        ),
        (
            (
                (LED_MATRIX_PROFILES["8x8"],),
                (LED_MATRIX_PROFILES["8x8"],),
            ),
            (
                (
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(12, 15),
                    ),
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(32, 15),
                    ),
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(52, 15),
                    ),
                ),
                (
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(12, 95),
                    ),
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(32, 95),
                    ),
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(52, 95),
                    ),
                ),
            ),
        ),
        (
            (
                (LED_MATRIX_PROFILES["16x16"], LED_MATRIX_PROFILES["8x8"]),
                (LED_MATRIX_PROFILES["8x8"], LED_MATRIX_PROFILES["16x16"]),
                (LED_MATRIX_PROFILES["16x16"], LED_MATRIX_PROFILES["8x8"]),
            ),
            (
                (
                    # 16x16 Input connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(30, 30),
                    ),
                    # 16x16 Power connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(70, 30),
                    ),
                    # 16x16 Output connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(110, 30),
                    ),
                    # 8x8 Input connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(172, 15),
                    ),
                    # 8x8 Power connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(192, 15),
                    ),
                    # 8x8 Output connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(212, 15),
                    ),
                ),
                (
                    # 8x8 Input connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(12, 175),
                    ),
                    # 8x8 Power connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(32, 175),
                    ),
                    # 8x8 Output connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(52, 175),
                    ),
                    # 16x16 Input connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(110, 190),
                    ),
                    # 16x16 Power connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(150, 190),
                    ),
                    # 16x16 Output connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(190, 190),
                    ),
                ),
                (
                    # 16x16 Input connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(30, 350),
                    ),
                    # 16x16 Power connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(70, 350),
                    ),
                    # 16x16 Output connector
                    Object2D(
                        Dimension2D(20, 100),
                        Position2D(110, 350),
                    ),
                    # 8x8 Input connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(172, 335),
                    ),
                    # 8x8 Power connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(192, 335),
                    ),
                    # 8x8 Output connector
                    Object2D(
                        Dimension2D(15, 50),
                        Position2D(212, 335),
                    ),
                ),
            ),
        ),
    ],
)
def test_connectors(layout: LedMatrixLayoutGrid, connectors: ConnectorLayoutGrid):
    assert CompositeLedMatrix(layout).connectors == connectors
