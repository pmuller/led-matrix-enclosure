from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class ChassisBottomParameters:
    #: Chassis bottom thickness
    thickness: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Chassis bottom")
        _ = group.add_argument(
            "--bottom-thickness",
            metavar="N",
            type=float,
            default=2,
            help="Chassis bottom thickness (unit: mm, default: %(default)s)",
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(thickness=arguments.bottom_thickness)  # pyright: ignore[reportAny]
