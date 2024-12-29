from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Self

from led_matrix_enclosure.dimensions import Dimension2D
from led_matrix_enclosure.models.composite_led_matrix import CompositeLedMatrix
from led_matrix_enclosure.parameters.chassis_borders import ChassisBordersParameters
from led_matrix_enclosure.parameters.chassis_bottom import ChassisBottomParameters
from led_matrix_enclosure.parameters.chassis_module_connectors import (
    ChassisModuleConnectorsParameters,
)
from led_matrix_enclosure.parameters.chassis_pillar import ChassisPillarParameters
from led_matrix_enclosure.parameters.lid_diffuser import LidDiffuserCliParameters
from led_matrix_enclosure.parameters.lid_grid import LidGridCliParameters


@dataclass(frozen=True)
class EnclosureParameters:
    """Enclosure parameters."""

    chassis_borders: ChassisBordersParameters
    chassis_module_connectors: ChassisModuleConnectorsParameters
    chassis_pillar: ChassisPillarParameters
    chassis_bottom: ChassisBottomParameters
    lid_grid: LidGridCliParameters
    lid_diffuser: LidDiffuserCliParameters
    #: Layout of the LED matrices in the enclosure
    led_matrix: CompositeLedMatrix
    #: Layout of the enclosure
    enclosure_layout: Dimension2D
    #: Height tolerance for the enclosure, in mm
    height_tolerance: float

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Enclosure")
        CompositeLedMatrix.add_cli_arguments(group)
        _ = group.add_argument(
            "--enclosure-layout",
            default=Dimension2D(1, 1),
            type=Dimension2D.parse,
            help="Enclosure layout (default: %(default)s)",
        )
        _ = group.add_argument(
            "--enclosure-height-tolerance",
            metavar="N",
            default=0.1,
            type=float,
            help="Tolerance for the height of the LED matrix, in mm (default: %(default)s)",
        )

        partial_build_group = group.add_mutually_exclusive_group()
        _ = partial_build_group.add_argument(
            "--no-lid",
            dest="build_enclosure_lid",
            default=True,
            action="store_false",
            help="Do not build the lid",
        )
        _ = partial_build_group.add_argument(
            "--no-chassis",
            dest="build_enclosure_chassis",
            default=True,
            action="store_false",
            help="Do not build the chassis",
        )

        ChassisBordersParameters.add_cli_arguments(parser)
        ChassisModuleConnectorsParameters.add_cli_arguments(parser)
        ChassisPillarParameters.add_cli_arguments(parser)
        ChassisBottomParameters.add_cli_arguments(parser)
        LidGridCliParameters.add_cli_arguments(parser)
        LidDiffuserCliParameters.add_cli_arguments(parser)

    @classmethod
    def from_cli_arguments(cls, namespace: Namespace) -> Self:
        chassis_borders = ChassisBordersParameters.from_cli_arguments(namespace)
        chassis_pillar = ChassisPillarParameters.from_cli_arguments(namespace)
        chassis_module_connectors = (
            ChassisModuleConnectorsParameters.from_cli_arguments(namespace)
        )
        chassis_bottom = ChassisBottomParameters.from_cli_arguments(namespace)
        lid_grid = LidGridCliParameters.from_cli_arguments(namespace)
        lid_diffuser = LidDiffuserCliParameters.from_cli_arguments(namespace)
        led_panels_layout = CompositeLedMatrix.from_cli_arguments(namespace)
        enclosure_layout: Dimension2D = namespace.enclosure_layout  # pyright: ignore[reportAny]
        height_tolerance: float = namespace.enclosure_height_tolerance  # pyright: ignore[reportAny]

        # TODO: Implement partial rendering
        assert namespace.build_enclosure_lid, "Not implemented"  # pyright: ignore[reportAny]
        assert namespace.build_enclosure_chassis, "Not implemented"  # pyright: ignore[reportAny]

        return cls(
            chassis_borders=chassis_borders,
            chassis_module_connectors=chassis_module_connectors,
            chassis_pillar=chassis_pillar,
            chassis_bottom=chassis_bottom,
            lid_grid=lid_grid,
            lid_diffuser=lid_diffuser,
            led_matrix=led_panels_layout,
            enclosure_layout=enclosure_layout,
            height_tolerance=height_tolerance,
        )
