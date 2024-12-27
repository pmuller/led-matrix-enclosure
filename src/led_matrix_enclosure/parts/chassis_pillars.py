from dataclasses import dataclass
import logging
from pprint import pformat

from build123d import CenterOf, Color, Compound, Part, Pos

from led_matrix_enclosure.parts.pillar import Pillar
from led_matrix_enclosure.dimensions import Dimension2D, Dimension3D, Object2D, Position2D


LOGGER = logging.getLogger(__name__)


@dataclass
class ChassisPillars:
    """Chassis pillars builder."""

    #: Pillar builder
    pillar: Pillar
    #: Chassis (inner) dimensions
    chassis_dimensions: Dimension3D
    #: Chassis bottom thickness
    chassis_bottom_thickness: float
    #: Panel connectors positions(optional)
    panel_connectors: tuple[Object2D, ...] = ()

    def build(self) -> Compound | None:
        LOGGER.info("Building chassis pillars")
        LOGGER.debug("%s", pformat(self))

        parts: list[Part] = []
        template = self.pillar.build()
        pillar_dimensions = self.pillar.compute_outer_dimensions()
        z_position = (self.chassis_bottom_thickness + pillar_dimensions.height) / 2
        shell_length = int(self.chassis_dimensions.length)
        shell_width = int(self.chassis_dimensions.width)
        pillar_spacing = int(self.pillar.spacing)
        half_pillar_spacing = pillar_spacing // 2

        # Create pillars
        for x in range(
            half_pillar_spacing,
            shell_length - half_pillar_spacing,
            pillar_spacing,
        ):
            for y in range(
                half_pillar_spacing,
                shell_width - half_pillar_spacing,
                pillar_spacing,
            ):
                # Reference pillar shape to check for overlaps
                pillar_2d = Object2D(
                    Dimension2D(
                        self.pillar.diameter,
                        self.pillar.diameter,
                    ),
                    Position2D(
                        x - self.pillar.diameter / 2,
                        y - self.pillar.diameter / 2,
                    ),
                )

                for connector in self.panel_connectors:
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
