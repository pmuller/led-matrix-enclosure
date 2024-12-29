from dataclasses import dataclass
import logging
from typing import Self

from build123d import Pos

from led_matrix_enclosure.dimensions import (
    Dimension2D,
    Dimension3D,
    Object2D,
    Position2D,
)
from led_matrix_enclosure.parameters.chassis import ChassisParameters
from led_matrix_enclosure.parameters.enclosure import EnclosureParameters
from led_matrix_enclosure.parameters.lid import LidParameters
from led_matrix_enclosure.parameters.lid_diffuser import LidDiffuserParameters
from led_matrix_enclosure.parameters.lid_grid import LidGridParameters
from led_matrix_enclosure.sides import Side, SideDict


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TemplateModuleParameters:
    """Template parameters for an enclosure module."""

    #: Enclosure parameters
    enclosure: EnclosureParameters

    @property
    def shape(self) -> Dimension2D:
        """Shape of a single module, in pixels."""
        shape = self.enclosure.led_matrix.shape
        layout = self.enclosure.enclosure_layout
        length = shape.length / layout.length
        width = shape.width / layout.width

        # XXX: This is a sanity check, but it is not obvious where to put it.
        assert length.is_integer(), "Part pixel length must be an integer"
        assert width.is_integer(), "Part pixel width must be an integer"

        return Dimension2D(length, width)

    @property
    def inner_dimensions(self) -> Dimension3D:
        shape = self.shape
        pixel_size = self.enclosure.led_matrix.pixel_size
        length = shape.length * pixel_size
        width = shape.width * pixel_size
        height = (
            # Provision enough space for the pillars that support the panels,
            # the panel height and the grid height
            self.enclosure.chassis_pillar.height
            + self.enclosure.led_matrix.min_height
            + self.enclosure.lid_grid.max_line_height
            + self.enclosure.height_tolerance
        )
        return Dimension3D(length, width, height)


@dataclass(frozen=True)
class ModuleParameters(TemplateModuleParameters):
    """Parameters for an enclosure module."""

    #: Position of the module in the enclosure
    position: Position2D
    #: Is the module a back row module
    is_back_row: bool
    #: Which borders are present
    border_presence: SideDict

    @classmethod
    def from_template(
        cls,
        template: TemplateModuleParameters,
        position: Position2D,
        is_back_row: bool,
        border_presence: SideDict,
    ) -> Self:
        return cls(
            enclosure=template.enclosure,
            position=position,
            is_back_row=is_back_row,
            border_presence=border_presence,
        )

    @property
    def inner_object_2d(self) -> Object2D:
        return Object2D(
            dimensions=self.inner_dimensions.to_2d(),
            position=self.position,
        )

    @property
    def back_wire_slots(self) -> tuple[Object2D, ...]:
        return (
            self.enclosure.led_matrix.scoped_back_wire_slots(
                offset=self.position.x,
                length=self.inner_dimensions.length,
            )
            if self.is_back_row
            else ()
        )

    @property
    def panel_connectors(self) -> tuple[Object2D, ...]:
        return self.enclosure.led_matrix.scoped_connectors(self.inner_object_2d)

    @property
    def chassis(self) -> ChassisParameters:
        return ChassisParameters(
            module=self,
            inner_dimensions=self.inner_dimensions,
            outer_dimensions=self.outer_dimensions,
            panel_connectors=self.panel_connectors,
            pillar=self.enclosure.chassis_pillar,
            module_connectors=self.enclosure.chassis_module_connectors,
            borders=self.enclosure.chassis_borders,
            bottom=self.enclosure.chassis_bottom,
        )

    @property
    def lid(self) -> LidParameters:
        grid = LidGridParameters.from_parameters(
            parameters=self.enclosure.lid_grid,
            shape=self.shape,
            # Always add back and right borders to the grid,
            # to compensate for the absence of the left and front borders on neighboring modules
            borders=self.border_presence + Side.BACK + Side.RIGHT,
            cell_size=self.enclosure.led_matrix.pixel_size,
        )
        diffuser = LidDiffuserParameters.from_parameters(
            parameters=self.enclosure.lid_diffuser,
            grid_dimensions=self.inner_dimensions.to_2d(),
            margins=self.border_presence,
            margin_size=self.enclosure.chassis_borders.thickness,
        )
        return LidParameters(grid, diffuser)

    @property
    def outer_dimensions(self) -> Dimension3D:
        length = (
            self.inner_dimensions.length
            + len(self.border_presence.horizontal)
            * self.enclosure.chassis_borders.thickness
        )
        width = (
            self.inner_dimensions.width
            + len(self.border_presence.vertical)
            * self.enclosure.chassis_borders.thickness
        )
        height = self.inner_dimensions.height + self.enclosure.chassis_bottom.thickness
        return Dimension3D(length, width, height)

    def _compute_border_position(self, side: Side) -> Pos:
        half_border_thickness = self.enclosure.chassis_borders.thickness / 2
        half_outer_width = self.outer_dimensions.width / 2
        half_outer_length = self.outer_dimensions.length / 2
        position_x = 0
        position_y = 0
        position_z = (
            self.inner_dimensions.height / 2
            + self.enclosure.chassis_bottom.thickness / 2
        )

        match side:
            case Side.BACK:
                position_y = half_outer_width - half_border_thickness
            case Side.FRONT:
                position_y = -half_outer_width + half_border_thickness
            case Side.LEFT:
                position_x = -half_outer_length + half_border_thickness
            case Side.RIGHT:
                position_x = half_outer_length - half_border_thickness

        return Pos(X=position_x, Y=position_y, Z=position_z)

    @property
    def border_positions(self) -> dict[Side, Pos]:
        return {side: self._compute_border_position(side) for side in Side}
