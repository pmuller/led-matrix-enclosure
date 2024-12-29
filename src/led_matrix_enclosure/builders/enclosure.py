from dataclasses import dataclass
import logging
from pprint import pformat

from build123d import Compound

from led_matrix_enclosure.builders.module import ModuleBuilder
from led_matrix_enclosure.dimensions import Position2D
from led_matrix_enclosure.parameters.enclosure import EnclosureParameters
from led_matrix_enclosure.parameters.module import (
    ModuleParameters,
    TemplateModuleParameters,
)
from led_matrix_enclosure.sides import SideDict


LOGGER = logging.getLogger(__name__)


ModulePosition = tuple[int, int]
ModuleDict = dict[ModulePosition, Compound]


def _connect_modules(modules: ModuleDict, length_step: int, width_step: int) -> None:
    for module_position, module in modules.items():
        x, y = module_position

        if x > 0:
            left_module_position: ModulePosition = (x - length_step, y)
            LOGGER.info(
                "Connecting module %s:right to %s:left",
                left_module_position,
                module_position,
            )
            left_module = modules[left_module_position]
            left_module.joints["right"].connect_to(module.joints["left"])  # pyright: ignore[reportUnknownMemberType]

        if y > 0:
            front_module_position: ModulePosition = (x, y - width_step)
            LOGGER.info(
                "Connecting module %s:back to %s:front",
                front_module_position,
                module_position,
            )
            front_module = modules[front_module_position]
            front_module.joints["back"].connect_to(module.joints["front"])  # pyright: ignore[reportUnknownMemberType]


@dataclass(frozen=True)
class EnclosureBuilder:
    """A LED panel enclosure.

    This is responsible for creating both the :class:`.Chassis` and the :class:`.Grid`.
    """

    parameters: EnclosureParameters
    name: str = "enclosure"

    def build(self) -> Compound:
        # Prepare parameters for the modules
        LOGGER.info("Building enclosure")
        LOGGER.debug(pformat(self.parameters))

        template_module_parameters = TemplateModuleParameters(self.parameters)
        led_matrix = self.parameters.led_matrix
        pixel_size = self.parameters.led_matrix.pixel_size
        length = int(led_matrix.shape.length * pixel_size)
        length_step = int(template_module_parameters.shape.length * pixel_size)
        width = int(led_matrix.shape.width * pixel_size)
        width_step = int(template_module_parameters.shape.width * pixel_size)
        modules: ModuleDict = {
            (length_index, width_index): ModuleBuilder(
                ModuleParameters.from_template(
                    template_module_parameters,
                    position=Position2D(length_index, width_index),
                    is_back_row=width_index + width_step == width,
                    border_presence=SideDict(
                        left=length_index == 0,
                        right=length_index + length_step == length,
                        front=width_index == 0,
                        back=width_index + width_step == width,
                    ),
                )
            ).build()
            for length_index in range(0, length, length_step)
            for width_index in range(0, width, width_step)
        }

        _connect_modules(modules, length_step, width_step)

        return Compound(children=modules.values(), label="enclosure")  # pyright: ignore[reportCallIssue]
