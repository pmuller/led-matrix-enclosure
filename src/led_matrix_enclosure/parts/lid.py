from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self

from build123d import Compound, Part, RigidJoint, Location

from led_matrix_enclosure.parts.grid import Grid, GridParameters, PartialGridParameters
from led_matrix_enclosure.parts.diffuser import (
    Diffuser,
    DiffuserParameters,
    PartialDiffuserParameters,
)
from led_matrix_enclosure.sides import SideDict


LOGGER = logging.getLogger(__name__)


@dataclass
class PartialLidParameters:
    grid: PartialGridParameters
    diffuser: PartialDiffuserParameters

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        _ = PartialGridParameters.add_cli_arguments(parser)
        _ = PartialDiffuserParameters.add_cli_arguments(parser)

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            grid=PartialGridParameters.from_cli_arguments(arguments),
            diffuser=PartialDiffuserParameters.from_cli_arguments(arguments),
        )


@dataclass
class LidParameters:
    grid: GridParameters
    diffuser: DiffuserParameters

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        _ = GridParameters.add_cli_arguments(parser)
        _ = DiffuserParameters.add_cli_arguments(parser)

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            grid=GridParameters.from_cli_arguments(arguments),
            diffuser=DiffuserParameters.from_cli_arguments(arguments),
        )


@dataclass
class Lid:
    grid: Grid
    diffuser: Diffuser
    name: str = "lid"

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        _ = Grid.add_cli_arguments(parser)
        _ = Diffuser.add_cli_arguments(parser)

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        # Remove diffuser margins if grid borders are present
        grid_borders: SideDict = arguments.grid_borders  # pyright: ignore[reportAny]
        arguments.diffuser_margins = ~grid_borders
        return cls(
            grid=Grid.from_cli_arguments(arguments),
            diffuser=Diffuser.from_cli_arguments(arguments),
        )

    def _add_chassis_joint(self, lid: Compound, diffuser: Part) -> None:
        # Add chassis joint to the bottom top left corner of the diffuser
        _ = RigidJoint("chassis", lid, Location(diffuser.bounding_box().min))

    def build(self) -> Compound:
        LOGGER.info("Building lid")
        LOGGER.debug("%s", pformat(self))

        diffuser = self.diffuser.build()
        grid = self.grid.build()
        diffuser.joints["grid"].connect_to(grid.joints["diffuser"])  # pyright: ignore[reportUnknownMemberType]
        lid = Compound(children=[diffuser, grid], label="lid")  # pyright: ignore[reportCallIssue]
        self._add_chassis_joint(lid, diffuser)
        return lid
