from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self

from build123d import Color, Part, Cylinder, Cone, Pos

from led_matrix_enclosure.dimensions import Dimension3D


LOGGER = logging.getLogger(__name__)


@dataclass
class Pillar:
    #: Pillar diameter, in mm
    diameter: float
    #: Pillar height, in mm
    height: float
    #: Pillar base height, in mm
    base_height: float
    #: Pillar base diameter, in mm
    base_diameter: float
    #: Pillar spacing, in mm
    spacing: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(
            title="Pillar",
            description="Parameters for the pillars that support the LED matrices",
        )
        _ = group.add_argument(
            "--pillar-diameter",
            metavar="N",
            type=float,
            default=3,
            help="Pillar diameter (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--pillar-height",
            metavar="N",
            type=float,
            default=10,
            help="Pillar height (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--pillar-base-height",
            metavar="N",
            type=float,
            default=3,
            help="Pillar base height (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--pillar-base-diameter",
            metavar="N",
            type=float,
            default=10,
            help="Pillar base diameter (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--pillar-spacing",
            metavar="N",
            type=float,
            default=25,
            help="Pillar spacing (unit: mm, default: %(default)s)",
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            diameter=arguments.pillar_diameter,  # pyright: ignore[reportAny]
            height=arguments.pillar_height,  # pyright: ignore[reportAny]
            base_height=arguments.pillar_base_height,  # pyright: ignore[reportAny]
            base_diameter=arguments.pillar_base_diameter,  # pyright: ignore[reportAny]
            spacing=arguments.pillar_spacing,  # pyright: ignore[reportAny]
        )

    def compute_outer_dimensions(self) -> Dimension3D:
        return Dimension3D(self.diameter, self.diameter, self.height)

    def build(self) -> Part:
        LOGGER.info("Building pillar")
        LOGGER.debug("%s", pformat(self))

        base_position = Pos(Z=-self.height / 2 + self.base_height / 2)
        base = Cone(self.base_diameter / 2, self.diameter / 2, self.base_height)

        main = Cylinder(self.diameter / 2, self.height)

        pillar = main + base.move(base_position)
        pillar.color = Color("black")
        pillar.label = "pillar"

        return pillar
