from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class ChassisPillarParameters:
    """Parameters for a single chassis pillar."""

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
            title="Chassis pillars",
            description="Parameters for the pillars that support the LED panels PCBs",
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
