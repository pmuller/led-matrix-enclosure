from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class ChassisModuleConnectorsParameters:
    #: Hole diameter, in mm
    hole_diameter: float
    #: Hole tolerance, in mm
    hole_tolerance: float
    #: Thickness of the wall, in mm
    wall_thickness: float
    #: Chamfer length, in mm
    chamfer_length: float
    #: Chamfer tolerance, in mm
    chamfer_tolerance: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(
            title="Chassis connectors",
            description="Parameters for the chassis module screw connectors",
        )
        _ = group.add_argument(
            "--connector-hole-diameter",
            metavar="N",
            type=float,
            default=3,
            help="Connector screw hole diameter (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-hole-tolerance",
            metavar="N",
            type=float,
            default=0.1,
            help="Connector screw hole tolerance (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-wall-thickness",
            metavar="N",
            type=float,
            default=2,
            help="Connector wall thickness (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-chamfer-length",
            metavar="N",
            type=float,
            default=2,
            help="Connector chamfer length (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--connector-chamfer-tolerance",
            metavar="N",
            type=float,
            default=0.1,
            help="Connector chamfer tolerance (unit: mm, default: %(default)s)",
        )

    @classmethod
    def from_cli_arguments(cls, namespace: Namespace) -> Self:
        return cls(
            hole_diameter=namespace.connector_hole_diameter,  # pyright: ignore[reportAny]
            hole_tolerance=namespace.connector_hole_tolerance,  # pyright: ignore[reportAny]
            wall_thickness=namespace.connector_wall_thickness,  # pyright: ignore[reportAny]
            chamfer_length=namespace.connector_chamfer_length,  # pyright: ignore[reportAny]
            chamfer_tolerance=namespace.connector_chamfer_tolerance,  # pyright: ignore[reportAny]
        )
