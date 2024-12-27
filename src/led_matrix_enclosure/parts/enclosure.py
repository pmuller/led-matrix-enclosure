from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self

from build123d import Compound

from led_matrix_enclosure.dimensions import Dimension3D, Dimension2D, Object2D, Position2D
from led_matrix_enclosure.models.composite_led_matrix import CompositeLedMatrix
from led_matrix_enclosure.parts.chassis import ChassisParameters
from led_matrix_enclosure.parts.lid import PartialLidParameters
from led_matrix_enclosure.parts.module import Module, ModuleParameters
from led_matrix_enclosure.sides import SideDict


LOGGER = logging.getLogger(__name__)


ModuleDict = dict[tuple[int, int], Compound]


def _connect_modules(modules: ModuleDict, length_step: int, width_step: int) -> None:
    for module_id, module in modules.items():
        x, y = module_id

        if x > 0:
            left_module_id = (x - length_step, y)
            LOGGER.info(
                "Connecting module %s:right to %s:left",
                left_module_id,
                module_id,
            )
            left_module = modules[left_module_id]
            left_module.joints["right"].connect_to(module.joints["left"])  # pyright: ignore[reportUnknownMemberType]

        if y > 0:
            front_module_id = (x, y - width_step)
            LOGGER.info(
                "Connecting module %s:back to %s:front",
                front_module_id,
                module_id,
            )
            front_module = modules[front_module_id]
            front_module.joints["back"].connect_to(module.joints["front"])  # pyright: ignore[reportUnknownMemberType]


@dataclass(kw_only=True)
class Enclosure:
    """A LED panel enclosure.

    This is responsible for creating both the :class:`.Chassis` and the :class:`.Grid`.
    """

    #: Description of the compositeLED matrices in the enclosure
    led_matrix: CompositeLedMatrix
    #: Layout of the enclosure
    enclosure_layout: Dimension2D
    #: Chassis parameters
    chassis: ChassisParameters
    #: Lid parameters
    lid: PartialLidParameters
    #: Height tolerance for the enclosure, in mm
    height_tolerance: float
    #: Name of the part
    name: str = "enclosure"

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
            default=0.1,
            type=float,
            help="Tolerance for the height of the LED matrix, in mm (default: %(default)s)",
        )
        ChassisParameters.add_cli_arguments(parser)
        PartialLidParameters.add_cli_arguments(parser)

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            led_matrix=CompositeLedMatrix.from_cli_arguments(arguments),
            enclosure_layout=arguments.enclosure_layout,  # pyright: ignore[reportAny]
            chassis=ChassisParameters.from_cli_arguments(arguments),
            lid=PartialLidParameters.from_cli_arguments(arguments),
            height_tolerance=arguments.enclosure_height_tolerance,  # pyright: ignore[reportAny]
        )

    @property
    def module_shape(self) -> Dimension2D:
        """Shape of a single module, in pixels."""
        full_grid_shape = self.led_matrix.shape
        part_pixel_length = full_grid_shape.length / self.enclosure_layout.length
        part_pixel_width = full_grid_shape.width / self.enclosure_layout.width

        # XXX: This is a sanity check, but it is not obvious where to put it.
        assert part_pixel_length.is_integer(), "Part pixel length must be an integer"
        assert part_pixel_width.is_integer(), "Part pixel width must be an integer"

        return Dimension2D(length=part_pixel_length, width=part_pixel_width)

    @property
    def module_inner_dimensions(self) -> Dimension3D:
        shape = self.module_shape
        return Dimension3D(
            length=shape.length * self.led_matrix.pixel_size,
            width=shape.width * self.led_matrix.pixel_size,
            # Provision enough space for the pillars that support the panels,
            # the panel height and the grid height
            height=self.chassis.pillar.height
            + self.led_matrix.min_height
            + self.lid.grid.height
            + self.height_tolerance,
        )

    def build(self) -> Compound:
        # Prepare parameters for the modules
        inner_dimensions = self.module_inner_dimensions
        parameters = ModuleParameters(
            chassis=self.chassis,
            lid=self.lid,
            inner_dimensions=inner_dimensions,
            grid_cell_size=self.led_matrix.pixel_size,
            grid_shape=self.module_shape,
        )

        LOGGER.info("Building enclosure")
        LOGGER.debug("Enclosure layout: %r", self.enclosure_layout)
        LOGGER.debug("Composite matrix shape: %r", self.led_matrix.shape)
        LOGGER.debug("Composite matrix layout: %s", pformat(self.led_matrix.layout))
        LOGGER.debug("%s", pformat(parameters))
        LOGGER.debug("Back wire slots: %s", pformat(self.led_matrix.back_wire_slots))

        length = int(self.led_matrix.shape.length)
        length_step = int(self.module_shape.length)
        width = int(self.led_matrix.shape.width)
        width_step = int(self.module_shape.width)
        modules: ModuleDict = {}
        module_2d = Object2D(
            dimensions=inner_dimensions.to_2d(),
            position=Position2D(0, 0),
        )

        for length_index in range(0, length, length_step):
            has_left_border = length_index == 0
            has_right_border = length_index + length_step == length

            for width_index in range(0, width, width_step):
                has_front_border = width_index == 0
                has_back_border = width_index + width_step == width
                border_presence = SideDict(
                    left=has_left_border,
                    right=has_right_border,
                    front=has_front_border,
                    back=has_back_border,
                )
                is_back_row = width_index + width_step == width
                back_wire_slots = (
                    self.led_matrix.scoped_back_wire_slots(
                        offset=module_2d.position.x,
                        length=inner_dimensions.length,
                    )
                    if is_back_row
                    else ()
                )
                panel_connectors = self.led_matrix.scoped_connectors(module_2d)

                LOGGER.debug(
                    "Building enclosure length_index=%d, width_index=%d, border_presence=%s, is_back_row=%s, module_2d=%s, panel_connectors=%s",
                    length_index,
                    width_index,
                    border_presence,
                    is_back_row,
                    module_2d,
                    panel_connectors,
                )

                modules[(length_index, width_index)] = Module.from_parameters(
                    parameters,
                    border_presence=border_presence,
                    x=length_index,
                    y=width_index,
                    back_wire_slots=back_wire_slots,
                    panel_connectors=panel_connectors,
                ).build()

                module_2d.position.y += inner_dimensions.width

            module_2d.position.x += inner_dimensions.length
            module_2d.position.y = 0

        _connect_modules(modules, length_step, width_step)

        return Compound(children=modules.values(), label="enclosure")  # pyright: ignore[reportCallIssue]
