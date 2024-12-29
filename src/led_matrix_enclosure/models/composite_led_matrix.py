"""Composite LED matrix model.

This model represents a composite LED matrix, which is a grid of LED matrices.

It supports multiple rows and columns of LED matrices,
and can be used to create a grid of LED matrices.

Columns can be freely be organized horizontally.

Caveat: panels can't be stacked vertically within a row.

For example, the following layout is valid:

```
16x16 16x16
16x16 16x16
```

But the following layout is not supported:

```
16x16 8x8
      8x8
16x16 16x16
```

"""

from argparse import ArgumentParser, _ArgumentGroup, Namespace  # pyright: ignore[reportPrivateUsage]
from collections.abc import Generator
from dataclasses import dataclass
import logging
from typing import Self

from led_matrix_enclosure.dimensions import Dimension2D, Object2D
from led_matrix_enclosure.models.led_matrix import LedMatrix
from led_matrix_enclosure.profiles.led_matrix import LED_MATRIX_PROFILES


LOGGER = logging.getLogger(__name__)


LedMatrixLayoutRow = tuple[LedMatrix, ...]
LedMatrixLayoutGrid = tuple[LedMatrixLayoutRow, ...]
ConnectorLayoutRow = tuple[Object2D, ...]
ConnectorLayoutGrid = tuple[ConnectorLayoutRow, ...]


def _parse_led_matrix_layout_row(layout_row: str) -> LedMatrixLayoutRow:
    """Parse a string representation of a LED matrix layout.

    The layout is a string of the form "8x8,16x16,32x8",
    where each number is the width and height of the LED matrix, in pixels.
    """
    matrices: list[LedMatrix] = []

    for matrix in layout_row.split(","):
        if matrix not in LED_MATRIX_PROFILES:
            raise ValueError(f"Invalid LED matrix profile: {matrix}")

        matrices.append(LED_MATRIX_PROFILES[matrix])

    return tuple(matrices)


def _assert_consistent_layout(layout: LedMatrixLayoutGrid) -> None:
    assert len(layout) > 0, "Layout must have at least one row"
    for index, row in enumerate(layout):
        assert len(row) > 0, f"Layout must have at least one panel in row {index}"
    pixel_size = layout[0][0].pixel_size
    assert all(
        panel.pixel_size == pixel_size for row in layout for panel in row
    ), "All panels must have the same pixel size"


@dataclass
class CompositeLedMatrix:
    """A composite LED matrix."""

    #: LED matrices
    layout: LedMatrixLayoutGrid

    @classmethod
    def add_cli_arguments(
        cls,
        parser_or_group: ArgumentParser | _ArgumentGroup,
    ) -> None:
        _ = parser_or_group.add_argument(
            "led_matrix_layout",
            nargs="+",
            type=_parse_led_matrix_layout_row,
            metavar="LAYOUT_ROW",
            help="""\
    Layout of the LED matrices in the enclosure, as a comma-separated list of matrix profiles.
    Add 1 string per row.
    Example: '16x16,16x16 32x8' creates an enclosure for a 32x24 composite matrix,
    using 3 LED matrices.\
    """,
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        layout: LedMatrixLayoutGrid = tuple(arguments.led_matrix_layout)  # pyright: ignore[reportAny]
        _assert_consistent_layout(layout)
        return cls(layout=layout)

    @property
    def pixel_size(self) -> float:
        """Size of a single pixel, in mm."""
        # It is safe to use the first panel's pixel size,
        # because _assert_consistent_layout ensures all panels have the same pixel size
        return self.layout[0][0].pixel_size

    @property
    def min_height(self) -> float:
        """Minimum height of the composite LED matrix, in mm."""
        return max(panel.min_height for row in self.layout for panel in row)

    @property
    def shape(self) -> Dimension2D:
        """Shape of the composite LED matrix, in pixels."""
        length: int = 0
        width: int = 0

        for row in self.layout:
            row_length: int = 0
            row_max_width: int = 0

            for panel in row:
                row_length += int(panel.layout.length)
                row_max_width = max(row_max_width, int(panel.layout.width))

            length = max(length, row_length)
            width += row_max_width

        return Dimension2D(length, width)

    @property
    def back_wire_slots(self) -> ConnectorLayoutRow:
        """Back wire slots for the composite LED matrix enclosure."""
        first_row = next(self._connectors())
        # Discard the panel, only keep the connector
        return tuple(connector for _, connector in first_row)

    def scoped_back_wire_slots(
        self,
        offset: float,
        length: float,
    ) -> ConnectorLayoutRow:
        """Back wire slots scoped for a module."""
        return tuple(
            # Adjust connector position as module coordinates
            connector - (offset, 0)
            for connector in self.back_wire_slots
            # Start of the slot is within the module
            if (offset <= connector.position.x <= offset + length)
            # End of the slot is within the module
            or (
                offset
                <= connector.position.x + connector.dimensions.length
                <= offset + length
            )
        )

    @property
    def connectors(self) -> ConnectorLayoutGrid:
        """Connectors positions for the composite LED matrix enclosure."""
        connectors: list[tuple[Object2D, ...]] = []

        for row in self._connectors():
            # Discard the panel, only keep the connector
            x_connectors = tuple(item[1] for item in row)
            connectors.append(x_connectors)

        return tuple(connectors)

    def _connectors(self) -> Generator[list[tuple[LedMatrix, Object2D]], None, None]:
        y_offset = 0

        for row in self.layout:
            x_offset = 0
            max_width = 0
            row_connectors: list[tuple[LedMatrix, Object2D]] = []

            for panel in row:
                dimensions = panel.dimensions()
                max_width = max(max_width, dimensions.width)

                for connector in panel.connectors:
                    row_connectors.append(
                        (
                            panel,
                            # Adjust connector position as composite panel coordinates
                            connector + (x_offset, y_offset),
                        )
                    )

                x_offset += dimensions.length

            y_offset += max_width

            yield row_connectors

    def scoped_connectors(self, scope: Object2D) -> ConnectorLayoutRow:
        """Connectors scoped for a module."""
        connectors: list[Object2D] = []

        for row in self.connectors:
            for connector in row:
                if connector.overlaps(scope):
                    connectors.append(connector - scope.position)

        return tuple(connectors)
