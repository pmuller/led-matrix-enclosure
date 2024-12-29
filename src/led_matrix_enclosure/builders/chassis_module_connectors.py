from dataclasses import dataclass
import logging

from build123d import Compound, Location, Part, RotationLike, Vector

from led_matrix_enclosure.builders.chassis_module_connector import (
    ChassisModuleConnectorBuilder,
)
from led_matrix_enclosure.parameters.chassis import ChassisParameters
from led_matrix_enclosure.sides import Side
from led_matrix_enclosure.dimensions import Dimension3D

LOGGER = logging.getLogger(__name__)

CONNECTOR_ROTATIONS: dict[
    tuple[
        Side,  # Build side
        Side,  # Opening side
    ],
    RotationLike,
] = {
    # Connectors mounted on the opening side
    (Side.LEFT, Side.LEFT): (90, 270, 0),
    (Side.RIGHT, Side.RIGHT): (90, 90, 0),
    (Side.BACK, Side.BACK): (270, 0, 180),
    (Side.FRONT, Side.FRONT): (90, 0, 0),
    # Connectors mounted on an adjacent border
    (Side.LEFT, Side.BACK): (270, 0, 270),
    (Side.LEFT, Side.FRONT): (90, 0, 270),
    (Side.RIGHT, Side.FRONT): (90, 0, 90),
    (Side.RIGHT, Side.BACK): (270, 0, 90),
    (Side.BACK, Side.RIGHT): (0, 90, 180),
    (Side.BACK, Side.LEFT): (0, 270, 180),
    (Side.FRONT, Side.LEFT): (0, 270, 0),
    (Side.FRONT, Side.RIGHT): (0, 90, 0),
}


def _get_rotation(build_side: Side, opening_side: Side) -> RotationLike:
    try:
        return CONNECTOR_ROTATIONS[(build_side, opening_side)]
    except KeyError:
        raise ValueError(
            f"A connector cannot be mounted on {build_side} with an opening on {opening_side}"
        )


@dataclass(frozen=True)
class ChassisModuleConnectorsBuilder:
    """Builds all the module connectors for a chassis module."""

    #: Module connector parameters
    parameters: ChassisParameters

    def _compute_connector_position(
        self,
        connector_dimensions: Dimension3D,
        build_side: Side,
        opening_side: Side,
    ) -> Vector:
        # Determine main axis based on opening side
        is_horizontal = opening_side.is_horizontal
        is_building_on_opening_side = build_side == opening_side
        main_axis = "X" if is_horizontal else "Y"
        cross_axis = "Y" if is_horizontal else "X"

        # Calculate main axis position
        main_size = (
            self.parameters.outer_dimensions.length
            if is_horizontal
            else self.parameters.outer_dimensions.width
        )
        main_direction = -1 if opening_side.is_start else 1
        main_offset = (main_size - connector_dimensions.height) / 2
        main_base: float = (
            0
            if is_building_on_opening_side
            else getattr(
                self.parameters.module.border_positions[build_side].position,
                main_axis,
            )
        )
        main_value = main_base + main_direction * main_offset

        # Calculate cross axis position
        cross_direction = 1 if build_side.is_start else -1
        cross_offset = (
            0
            if is_building_on_opening_side
            else (self.parameters.borders.thickness + connector_dimensions.width) / 2
        )
        cross_base: float = getattr(
            self.parameters.module.border_positions[build_side].position,
            cross_axis,
        )
        cross_value = cross_base + cross_direction * cross_offset

        # Calculate Z position
        z_value = (connector_dimensions.length + self.parameters.bottom.thickness) / 2

        return Vector(**{main_axis: main_value, cross_axis: cross_value, "Z": z_value})

    def _prepare_connector(
        self,
        connector_dimensions: Dimension3D,
        template: Part,
        build_side: Side,
        opening_side: Side,
    ) -> Part:
        location = Location(
            self._compute_connector_position(
                connector_dimensions,
                build_side,
                opening_side,
            ),
            _get_rotation(build_side, opening_side),
        )
        LOGGER.debug(
            "Connector build_side=%s opening_side=%s location=%r",
            build_side,
            opening_side,
            location,
        )
        connector = template.moved(location)
        connector.label = f"connector:build={build_side},opening={opening_side}"
        return connector

    def build(self) -> Compound | None:
        LOGGER.info("Building chassis connectors")

        connectors: list[Part] = []
        connector_builder = ChassisModuleConnectorBuilder(self.parameters)
        connector_dimensions = connector_builder.compute_outer_dimensions()
        template = connector_builder.build()

        for border, has_border in self.parameters.module.border_presence.items():
            if not has_border:
                connectors.append(
                    self._prepare_connector(
                        connector_dimensions=connector_dimensions,
                        template=template,
                        build_side=border,
                        opening_side=border,
                    )
                )

                for (
                    adjacent_border
                ) in self.parameters.module.border_presence.get_adjacents(border):
                    connectors.append(
                        self._prepare_connector(
                            connector_dimensions=connector_dimensions,
                            template=template,
                            build_side=adjacent_border,
                            opening_side=border,
                        )
                    )

        if connectors:
            return Compound(children=connectors, label="connectors")  # pyright: ignore[reportCallIssue]
        else:
            LOGGER.debug("No connectors to build")
