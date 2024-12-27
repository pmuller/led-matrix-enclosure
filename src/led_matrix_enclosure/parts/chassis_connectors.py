from dataclasses import dataclass
import logging
from pprint import pformat

from build123d import Compound, Location, Part, RotationLike, Vector, Pos

from led_matrix_enclosure.parts.connector import Connector
from led_matrix_enclosure.sides import Side, SideDict
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


@dataclass
class ChassisConnectors:
    """Chassis connectors builder."""

    connector: Connector
    #: Chassis borders
    border_presence: SideDict
    #: Chassis border positions
    border_positions: dict[Side, Pos]
    #: Chassis dimensions
    chassis_dimensions: Dimension3D
    #: Chassis bottom thickness
    chassis_bottom_thickness: float
    #: Chassis border thickness
    chassis_border_thickness: float

    def _compute_connector_position(
        self,
        build_side: Side,
        opening_side: Side,
    ) -> Vector:
        connector_dimensions = self.connector.compute_outer_dimensions()

        # Determine main axis based on opening side
        is_horizontal = opening_side.is_horizontal
        is_building_on_opening_side = build_side == opening_side
        main_axis = "X" if is_horizontal else "Y"
        cross_axis = "Y" if is_horizontal else "X"

        # Calculate main axis position
        main_size = (
            self.chassis_dimensions.length
            if is_horizontal
            else self.chassis_dimensions.width
        )
        main_direction = -1 if opening_side.is_start else 1
        main_offset = main_size / 2 - connector_dimensions.height / (
            4 if self.border_presence.has_opposite(opening_side) else 2
        )
        main_base: float = (
            0
            if is_building_on_opening_side
            else getattr(
                self.border_positions[build_side].position,
                main_axis,
            )
        )
        main_value = main_base + main_direction * main_offset

        # Calculate cross axis position
        cross_direction = 1 if build_side.is_start else -1
        cross_offset = (
            0
            if is_building_on_opening_side
            else (self.chassis_border_thickness + connector_dimensions.width) / 2
        )
        cross_base: float = getattr(
            self.border_positions[build_side].position,
            cross_axis,
        )
        cross_value = cross_base + cross_direction * cross_offset

        # Calculate Z position
        z_value = (connector_dimensions.length + self.chassis_bottom_thickness) / 2

        return Vector(**{main_axis: main_value, cross_axis: cross_value, "Z": z_value})

    def _prepare_connector(
        self,
        template: Part,
        build_side: Side,
        opening_side: Side,
    ) -> Part:
        location = Location(
            self._compute_connector_position(build_side, opening_side),
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
        LOGGER.debug("%s", pformat(self))

        connectors: list[Part] = []
        template = self.connector.build()

        for border, has_border in self.border_presence.items():
            if not has_border:
                connectors.append(
                    self._prepare_connector(
                        template=template,
                        build_side=border,
                        opening_side=border,
                    )
                )

                for adjacent_border in self.border_presence.get_adjacents(border):
                    connectors.append(
                        self._prepare_connector(
                            template=template,
                            build_side=adjacent_border,
                            opening_side=border,
                        )
                    )

        if connectors:
            return Compound(children=connectors, label="connectors")  # pyright: ignore[reportCallIssue]
        else:
            LOGGER.debug("No connectors to build")
