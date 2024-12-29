from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class ChassisBordersParameters:
    #: Border radius
    radius: float
    #: Border thickness
    thickness: float
    #: LED matrix support ledge size, in mm
    support_ledge_size: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Chassis borders")
        _ = group.add_argument(
            "--border-radius",
            metavar="N",
            type=float,
            default=1.99,
            help="Radius of the fillets on the chassis borders (default: %(default)s)",
        )
        _ = group.add_argument(
            "--border-thickness",
            metavar="N",
            type=float,
            default=2,
            help="Thickness of the chassis borders (default: %(default)s)",
        )
        _ = group.add_argument(
            "--border-support-ledge-size",
            metavar="N",
            type=float,
            default=2,
            help="Size of the LED matrix support ledge (default: %(default)s)",
        )

    @classmethod
    def from_cli_arguments(cls, namespace: Namespace) -> Self:
        return cls(
            radius=namespace.border_radius,  # pyright: ignore[reportAny]
            thickness=namespace.border_thickness,  # pyright: ignore[reportAny]
            support_ledge_size=namespace.border_support_ledge_size,  # pyright: ignore[reportAny]
        )
