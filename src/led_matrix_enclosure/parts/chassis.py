from argparse import ArgumentParser, Namespace, _ArgumentGroup  # pyright: ignore[reportPrivateUsage]
from dataclasses import dataclass
import logging
from pprint import pformat
from typing import Self, cast, final, override

from build123d import Axis, Compound, Shape, Vector, RigidJoint, Location, Pos, fillet

from led_matrix_enclosure.dimensions import Dimension3D, Object2D
from led_matrix_enclosure.parts.chassis_bottom import ChassisBottom
from led_matrix_enclosure.parts.chassis_borders import ChassisBorders
from led_matrix_enclosure.parts.chassis_connectors import ChassisConnectors
from led_matrix_enclosure.parts.chassis_pillars import ChassisPillars
from led_matrix_enclosure.parts.connector import Connector, ConnectorParameters
from led_matrix_enclosure.parts.pillar import Pillar
from led_matrix_enclosure.sides import SideDict, Side

LOGGER = logging.getLogger(__name__)


def _compute_chassis_outer_dimensions(
    *,
    inner_dimensions: Dimension3D,
    border_presence: SideDict,
    border_thickness: float,
    bottom_thickness: float,
) -> Dimension3D:
    length = (
        inner_dimensions.length + len(border_presence.horizontal) * border_thickness
    )
    width = inner_dimensions.width + len(border_presence.vertical) * border_thickness
    height = inner_dimensions.height + bottom_thickness
    return Dimension3D(length, width, height)


def _compute_border_position(
    *,
    outer_dimensions: Dimension3D,
    inner_dimensions: Dimension3D,
    border_thickness: float,
    bottom_thickness: float,
    side: Side,
) -> Pos:
    half_border_thickness = border_thickness / 2
    half_outer_width = outer_dimensions.width / 2
    half_outer_length = outer_dimensions.length / 2
    position_x = 0
    position_y = 0
    position_z = inner_dimensions.height / 2 + bottom_thickness / 2

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


def _compute_border_positions(
    *,
    outer_dimensions: Dimension3D,
    inner_dimensions: Dimension3D,
    bottom_thickness: float,
    border_thickness: float,
) -> dict[Side, Pos]:
    return {
        side: _compute_border_position(
            outer_dimensions=outer_dimensions,
            inner_dimensions=inner_dimensions,
            bottom_thickness=bottom_thickness,
            border_thickness=border_thickness,
            side=side,
        )
        for side in Side
    }


@dataclass
class ChassisParameters:
    """Parameters for a chassis."""

    #: Connector builder
    connector: Connector
    #: Pillar builder
    pillar: Pillar
    #: Border radius
    border_radius: float
    #: Border thickness
    border_thickness: float
    #: Bottom thickness
    bottom_thickness: float
    #: LED matrix support ledge size, in mm
    support_ledge_size: float

    @classmethod
    def _create_cli_argument_group(cls, parser: ArgumentParser) -> _ArgumentGroup:
        return parser.add_argument_group(title="Chassis")

    @classmethod
    def _add_cli_arguments(cls, parser: ArgumentParser, group: _ArgumentGroup) -> None:
        _ = group.add_argument(
            "--chassis-border-radius",
            metavar="N",
            type=float,
            default=1.99,
            help="Radius of the fillets on the chassis borders (default: %(default)s)",
        )
        _ = group.add_argument(
            "--chassis-border-thickness",
            metavar="N",
            type=float,
            default=2,
            help="Thickness of the chassis borders (default: %(default)s)",
        )
        _ = group.add_argument(
            "--chassis-bottom-thickness",
            metavar="N",
            type=float,
            default=2,
            help="Chassis bottom thickness (unit: mm, default: %(default)s)",
        )
        _ = group.add_argument(
            "--chassis-support-ledge-size",
            metavar="N",
            type=float,
            default=2,
            help="Size of the LED matrix support ledge (default: %(default)s)",
        )

        Connector.add_cli_arguments(parser)
        Pillar.add_cli_arguments(parser)

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = cls._create_cli_argument_group(parser)
        cls._add_cli_arguments(parser, group)

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        pillar = Pillar.from_cli_arguments(arguments)
        connector_parameters = ConnectorParameters.from_cli_arguments(arguments)
        connector = Connector.from_parameters(connector_parameters, pillar.height)
        return cls(
            border_radius=arguments.chassis_border_radius,  # pyright: ignore[reportAny]
            border_thickness=arguments.chassis_border_thickness,  # pyright: ignore[reportAny]
            bottom_thickness=arguments.chassis_bottom_thickness,  # pyright: ignore[reportAny]
            support_ledge_size=arguments.chassis_support_ledge_size,  # pyright: ignore[reportAny]
            connector=connector,
            pillar=pillar,
        )


@dataclass
@final
class Chassis(ChassisParameters):
    """A LED panel chassis.

    This is the bottom part of the LED panel enclosure.
    """

    #: Chassis bottom builder
    bottom: ChassisBottom
    #: Chassis connectors builder
    connectors: ChassisConnectors
    #: Chassis pillars builder
    pillars: ChassisPillars
    #: Chassis borders builder
    borders: ChassisBorders
    #: Border positions
    border_positions: dict[Side, Pos]
    #: Which borders to add to the chassis
    border_presence: SideDict
    #: Inner dimensions of the chassis
    inner_dimensions: Dimension3D
    #: Outer dimensions of the chassis
    outer_dimensions: Dimension3D
    #: Panel connectors positions (optional)
    panel_connectors: tuple[Object2D, ...] = ()
    #: Name of the part
    name: str = "chassis"

    @classmethod
    @override
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = cls._create_cli_argument_group(parser)
        _ = group.add_argument(
            "chassis_inner_dimensions",
            metavar="LENGTHxWIDTHxHEIGHT",
            type=Dimension3D.parse,
            help="Inner dimensions of the chassis (unit: mm)",
        )
        SideDict.add_cli_argument(
            group,
            "--remove-chassis-border",
            dest="chassis_border_presence",
            default=True,
            help="Remove a border from the chassis (default: %(default)s)",
        )
        cls._add_cli_arguments(parser, group)

    @classmethod
    @override
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        inner_dimensions: Dimension3D = arguments.chassis_inner_dimensions  # pyright: ignore[reportAny]
        bottom_thickness: float = arguments.chassis_bottom_thickness  # pyright: ignore[reportAny]
        border_presence: SideDict = arguments.chassis_border_presence  # pyright: ignore[reportAny]
        border_thickness: float = arguments.chassis_border_thickness  # pyright: ignore[reportAny]
        border_radius: float = arguments.chassis_border_radius  # pyright: ignore[reportAny]
        support_ledge_size: float = arguments.chassis_support_ledge_size  # pyright: ignore[reportAny]

        LOGGER.debug("Building chassis from CLI arguments")
        LOGGER.debug("inner_dimensions=%s", pformat(inner_dimensions))
        LOGGER.debug("bottom_thickness=%s", pformat(bottom_thickness))
        LOGGER.debug("border_presence=%s", pformat(border_presence))
        LOGGER.debug("border_thickness=%s", pformat(border_thickness))
        LOGGER.debug("border_radius=%s", pformat(border_radius))
        LOGGER.debug("support_ledge_size=%s", pformat(support_ledge_size))

        outer_dimensions = _compute_chassis_outer_dimensions(
            inner_dimensions=inner_dimensions,
            bottom_thickness=bottom_thickness,
            border_presence=border_presence,
            border_thickness=border_thickness,
        )

        border_positions = _compute_border_positions(
            outer_dimensions=outer_dimensions,
            inner_dimensions=inner_dimensions,
            bottom_thickness=bottom_thickness,
            border_thickness=border_thickness,
        )

        pillar = Pillar.from_cli_arguments(arguments)
        pillars = ChassisPillars(
            pillar=pillar,
            chassis_dimensions=inner_dimensions,
            chassis_bottom_thickness=bottom_thickness,
        )

        connector_parameters = ConnectorParameters.from_cli_arguments(arguments)
        connectors = ChassisConnectors(
            connector=Connector.from_parameters(connector_parameters, pillar.height),
            border_presence=border_presence,
            chassis_dimensions=inner_dimensions,
            border_positions=border_positions,
            chassis_bottom_thickness=bottom_thickness,
            chassis_border_thickness=border_thickness,
        )

        borders = ChassisBorders(
            inner_dimensions=inner_dimensions,
            outer_dimensions=outer_dimensions,
            border_thickness=border_thickness,
            border_radius=border_radius,
            border_positions=border_positions,
            border_presence=border_presence,
            ledge_size=support_ledge_size,
            ledge_z_offset=pillar.height,
        )

        bottom = ChassisBottom(
            dimensions=outer_dimensions,
            thickness=bottom_thickness,
        )

        return cls(
            connector=connectors.connector,
            pillar=pillars.pillar,
            connectors=connectors,
            pillars=pillars,
            borders=borders,
            bottom=bottom,
            border_radius=border_radius,
            border_thickness=border_thickness,
            border_presence=border_presence,
            bottom_thickness=bottom_thickness,
            border_positions=border_positions,
            inner_dimensions=inner_dimensions,
            outer_dimensions=outer_dimensions,
            support_ledge_size=support_ledge_size,
        )

    @classmethod
    def from_parameters(
        cls,
        parameters: ChassisParameters,
        inner_dimensions: Dimension3D,
        border_presence: SideDict,
        back_wire_slots: tuple[Object2D, ...],
        panel_connectors: tuple[Object2D, ...],
    ) -> Self:
        LOGGER.debug("Building chassis from parameters")
        LOGGER.debug("parameters=%s", pformat(parameters))
        LOGGER.debug("inner_dimensions=%s", pformat(inner_dimensions))
        LOGGER.debug("border_presence=%s", pformat(border_presence))
        LOGGER.debug("back_wire_slots=%s", pformat(back_wire_slots))

        outer_dimensions = _compute_chassis_outer_dimensions(
            inner_dimensions=inner_dimensions,
            bottom_thickness=parameters.bottom_thickness,
            border_presence=border_presence,
            border_thickness=parameters.border_thickness,
        )

        border_positions = _compute_border_positions(
            outer_dimensions=outer_dimensions,
            inner_dimensions=inner_dimensions,
            bottom_thickness=parameters.bottom_thickness,
            border_thickness=parameters.border_thickness,
        )

        connectors = ChassisConnectors(
            connector=parameters.connector,
            border_presence=border_presence,
            chassis_dimensions=inner_dimensions,
            border_positions=border_positions,
            chassis_bottom_thickness=parameters.bottom_thickness,
            chassis_border_thickness=parameters.border_thickness,
        )

        pillars = ChassisPillars(
            pillar=parameters.pillar,
            chassis_dimensions=inner_dimensions,
            chassis_bottom_thickness=parameters.bottom_thickness,
            panel_connectors=panel_connectors,
        )

        borders = ChassisBorders(
            inner_dimensions=inner_dimensions,
            outer_dimensions=outer_dimensions,
            border_thickness=parameters.border_thickness,
            border_radius=parameters.border_radius,
            border_positions=border_positions,
            border_presence=border_presence,
            ledge_size=parameters.support_ledge_size,
            ledge_z_offset=pillars.pillar.height,
            back_wire_slots=back_wire_slots,
        )

        bottom = ChassisBottom(
            dimensions=outer_dimensions,
            thickness=parameters.bottom_thickness,
        )

        return cls(
            connector=parameters.connector,
            pillar=parameters.pillar,
            connectors=connectors,
            pillars=pillars,
            borders=borders,
            bottom=bottom,
            border_radius=parameters.border_radius,
            border_thickness=parameters.border_thickness,
            border_presence=border_presence,
            bottom_thickness=parameters.bottom_thickness,
            border_positions=border_positions,
            inner_dimensions=inner_dimensions,
            outer_dimensions=outer_dimensions,
            support_ledge_size=parameters.support_ledge_size,
        )

    def _add_lid_joint(self, chassis: Compound, bottom: Compound) -> None:
        bounding_box = bottom.bounding_box()
        z_offset = self.inner_dimensions.height + self.bottom_thickness / 2
        vector = Vector(bounding_box.min.X, bounding_box.min.Y, z_offset)
        _ = RigidJoint("lid", chassis, Location(vector))

    def _is_outer_edge(self, shape: Shape) -> bool:
        half_outer_length = self.outer_dimensions.length / 2
        half_outer_width = self.outer_dimensions.width / 2
        center = shape.center()
        x_position = center.X
        y_position = center.Y
        is_corner = (  # Is it an outer corner?
            abs(abs(x_position) - half_outer_length) == 0
            and abs(abs(y_position) - half_outer_width) == 0
        )

        if not is_corner:
            return False

        # Check if both adjacent sides exist
        return (
            self.border_presence[Side.LEFT if x_position < 0 else Side.RIGHT]
            and self.border_presence[Side.FRONT if y_position < 0 else Side.BACK]
        )

    def _fillet_outer_edges(self, compound: Compound) -> Compound:
        outer_vertical_edges = (
            compound.edges().filter_by(Axis.Z).filter_by(self._is_outer_edge)
        )

        if len(outer_vertical_edges) > 0:
            LOGGER.info("Filleting %d outer vertical edges", len(outer_vertical_edges))
            color = compound.color
            label = compound.label
            compound = cast(Compound, fillet(outer_vertical_edges, self.border_radius))
            compound.color = color
            compound.label = label
            return compound
        else:
            LOGGER.info("No outer vertical edges to fillet")
            return compound

    def build(self) -> Compound:
        LOGGER.info("Building chassis")
        LOGGER.debug("%s", pformat(self))

        bottom = self._fillet_outer_edges(self.bottom.build())
        connectors = self.connectors.build()
        borders = self.borders.build()
        pillars = self.pillars.build()

        children: list[Compound] = [bottom]

        if connectors is not None:
            children.append(connectors)

        if pillars is None:
            LOGGER.warning(
                "No pillars to add to the chassis. Is the chassis too small?"
            )
        else:
            children.append(pillars)

        if borders is not None:
            children.append(self._fillet_outer_edges(borders))

        chassis = Compound(children=children, label="chassis")  # pyright: ignore[reportCallIssue]
        self._add_lid_joint(chassis, bottom)

        return chassis
