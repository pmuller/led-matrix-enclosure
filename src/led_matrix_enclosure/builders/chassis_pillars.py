from dataclasses import dataclass
import logging

from build123d import CenterOf, Color, Compound, Part, Pos

from led_matrix_enclosure.builders.chassis_pillar import ChassisPillarBuilder
from led_matrix_enclosure.dimensions import Dimension2D, Object2D, Position2D
from led_matrix_enclosure.parameters.chassis import ChassisParameters


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChassisPillarsBuilder:
    """Builds all the pillars of a chassis."""

    parameters: ChassisParameters

    def build(self) -> Compound | None:
        LOGGER.info("Building chassis pillars")

        parts: list[Part] = []
        template = ChassisPillarBuilder(self.parameters.pillar).build()
        z_position = (
            self.parameters.bottom.thickness + self.parameters.pillar.height
        ) / 2

        # XXX: Where should those checks be?
        assert self.parameters.inner_dimensions.length.is_integer()
        assert self.parameters.inner_dimensions.width.is_integer()
        assert self.parameters.pillar.spacing.is_integer()

        chassis_length = int(self.parameters.inner_dimensions.length)
        chassis_width = int(self.parameters.inner_dimensions.width)
        pillar_spacing = int(self.parameters.pillar.spacing)
        half_pillar_spacing = pillar_spacing // 2

        # Create pillars
        for x in range(
            half_pillar_spacing,
            chassis_length - half_pillar_spacing,
            pillar_spacing,
        ):
            for y in range(
                half_pillar_spacing,
                chassis_width - half_pillar_spacing,
                pillar_spacing,
            ):
                # Reference pillar shape to check for overlaps
                diameter = self.parameters.pillar.diameter
                pillar_2d = Object2D(
                    Dimension2D(diameter, diameter),
                    Position2D(x - diameter / 2, y - diameter / 2),
                )

                for connector in self.parameters.panel_connectors:
                    if pillar_2d.overlaps(connector):
                        LOGGER.debug(
                            "Skipping pillar at (%s, %s) because it overlaps with a panel connector %r",
                            x,
                            y,
                            connector,
                        )
                        break
                else:
                    LOGGER.debug("Adding pillar at (%s, %s)", x, y)
                    parts.append(template.moved(Pos(x, y, z_position)))

        # Do not create a compound if there are no pillars
        if not parts:
            return None

        # Create compound of pillars
        pillars = Compound(parts, label="pillars", color=Color("black"))

        # Align center of pillars to center of shell
        pillars_center = pillars.center(CenterOf.BOUNDING_BOX)
        pillars = pillars.move(
            Pos(
                X=-pillars_center.X,
                Y=-pillars_center.Y,
            )
        )

        return pillars
