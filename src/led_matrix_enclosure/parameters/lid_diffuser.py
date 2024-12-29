from argparse import Namespace, ArgumentParser
from dataclasses import dataclass
from typing import Self

from led_matrix_enclosure.dimensions import Dimension2D
from led_matrix_enclosure.sides import SideDict


@dataclass(frozen=True)
class LidDiffuserCliParameters:
    #: Thickness of the diffuser, in mm
    thickness: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Diffuser")
        _ = group.add_argument(
            "--diffuser-thickness",
            metavar="N",
            default=0.3,
            type=float,
            help="How thick the diffuser should be (unit: mm, default: %(default)s)",
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            thickness=arguments.diffuser_thickness,  # pyright: ignore[reportAny]
        )


@dataclass(frozen=True)
class LidDiffuserParameters(LidDiffuserCliParameters):
    #: Dimensions of the underlying grid, in mm
    grid_dimensions: Dimension2D
    #: Margins to add to the diffuser
    margins: SideDict
    #: Diffuser margin around the grid, in mm
    margin_size: float

    @classmethod
    def from_parameters(
        cls,
        parameters: LidDiffuserCliParameters,
        grid_dimensions: Dimension2D,
        margins: SideDict,
        margin_size: float,
    ) -> Self:
        return cls(
            thickness=parameters.thickness,
            margin_size=margin_size,
            grid_dimensions=grid_dimensions,
            margins=margins,
        )
