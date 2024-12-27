from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Literal, cast

from build123d import (
    Align,
    Axis,
    Compound,
    Plane,
    Pos,
    Rectangle,
    Triangle,
    Vector,
    extrude,
    Location,
)

from led_matrix_enclosure.dimensions import Dimension3D
from led_matrix_enclosure.sides import Side, SideDict


Direction = Literal[-1, 1]


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisBorderSupportLedge:
    """Chassis border support ledge."""

    #: Size of the ledge, in mm (sides next to the right angle)
    size: float
    #: Length of the ledge, in mm (matching the border length)
    length: float
    #: Thickness of the border
    border_thickness: float
    #: Presence of the borders
    border_presence: SideDict
    #: Side of the border
    side: Side
    #: Inner dimensions of the chassis
    inner_dimensions: Dimension3D
    #: Z-offset of the ledge
    z_offset: float
    #: Ratio of the ledge to the cut shape
    ledge_border_ratio: float = 0.5

    def _create_base_triangle(self, plane: Plane, rotation: float) -> Triangle:
        return cast(
            Triangle,
            plane
            * Triangle(
                a=self.size * (1 + self.ledge_border_ratio),
                b=self.size,
                C=90,
                align=(Align.MAX, Align.MIN),
                rotation=rotation,
            ),
        )

    def _create_cut_shape(
        self,
        plane: Plane,
        size: float,
        rotation: float,
    ) -> Rectangle:
        rectangle = cast(
            Rectangle,
            plane
            * Rectangle(
                size,
                size,
                align=(Align.MAX, Align.MIN),
                rotation=rotation,
            ),
        )
        # Move the cut shape to the right of the triangle
        direction = 1 if self.side.is_start else -1
        offset = 0 if self.side.is_horizontal else (size * 2)
        _ = rectangle.move(
            Pos(
                X=direction * (self.size - offset),
                Y=direction * offset,
            )
        )
        return rectangle

    def _compute_move_x_offset(self, direction: Direction) -> float:
        return direction * self.border_thickness / 2 + (
            0
            if self.side.is_horizontal
            else (
                (-self.length / 2 - self.border_thickness / 2)
                + (0 if self.side.is_start else self.length)
            )
        )

    def _compute_move_y_offset(self, direction: Direction) -> float:
        adjacent_sides_count = len(self.border_presence.get_adjacents(self.side))
        is_horizontal = self.side.is_horizontal
        return direction * (
            (self.inner_dimensions.width if is_horizontal else 0)
            + adjacent_sides_count * self.border_thickness
        ) / 2 + (
            0
            if is_horizontal
            else (
                (self.border_thickness - adjacent_sides_count * self.border_thickness)
                / 2
                - (0 if self.side.is_start else self.border_thickness)
            )
        )

    def _compute_move_location(self, direction: Direction) -> Location:
        return Location(
            Vector(
                X=self._compute_move_x_offset(direction),
                Y=self._compute_move_y_offset(direction),
                Z=self.z_offset,
            ),
        )

    def build(self) -> Compound:
        LOGGER.debug("Building chassis border support ledge: %s", self.side)
        LOGGER.debug("%s", pformat(self))

        is_start = self.side.is_start
        is_horizontal = self.side.is_horizontal
        rotation = 180 if is_start else 90
        plane = (
            (Plane.XZ if is_start else Plane.ZX)
            if is_horizontal
            else (Plane.YZ if is_start else Plane.ZY)
        )
        cut_size = self.size * self.ledge_border_ratio

        base_triangle = self._create_base_triangle(plane, rotation)
        cut_shape = self._create_cut_shape(plane, cut_size, rotation)
        ledge = base_triangle - cut_shape

        direction = (1 if is_start else -1) if is_horizontal else 1
        _ = ledge.move(self._compute_move_location(direction))
        _ = ledge.rotate(Axis.Z, 0 if is_start else 180)

        return extrude(ledge, amount=self.length)
