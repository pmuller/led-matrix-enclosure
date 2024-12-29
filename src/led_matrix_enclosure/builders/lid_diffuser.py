from dataclasses import dataclass
import logging

from build123d import (
    Align,
    CenterOf,
    Compound,
    Edge,
    Part,
    Box,
    Color,
    Axis,
    ShapeList,
    fillet,
    RigidJoint,
    Location,
    Vector,
)


from led_matrix_enclosure.corners import Corner2DPredicate, TWO_DIMENSIONAL_CORNERS
from led_matrix_enclosure.parameters.lid_diffuser import LidDiffuserParameters
from led_matrix_enclosure.sides import Side


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LidDiffuserBuilder:
    """The LED light diffuser."""

    #: Parameters
    parameters: LidDiffuserParameters

    def _get_bottom_center(self, diffuser: Compound) -> Vector:
        center_x, center_y, _ = diffuser.center(CenterOf.BOUNDING_BOX).to_tuple()

        # Move the center according to the margins
        if not self.parameters.margins[Side.LEFT]:
            center_x -= self.parameters.margin_size / 2
        if not self.parameters.margins[Side.RIGHT]:
            center_x += self.parameters.margin_size / 2
        if not self.parameters.margins[Side.BACK]:
            center_y += self.parameters.margin_size / 2
        if not self.parameters.margins[Side.FRONT]:
            center_y -= self.parameters.margin_size / 2

        return Vector(center_x, center_y, diffuser.bounding_box().min.Z)

    def _add_grid_joint(self, diffuser: Compound) -> None:
        _ = RigidJoint("grid", diffuser, Location(self._get_bottom_center(diffuser)))

    def _fillet(self, diffuser: Part) -> Compound:
        z_edges = diffuser.edges().filter_by(Axis.Z)
        fillet_edges: ShapeList[Edge] = ShapeList()

        for corner in TWO_DIMENSIONAL_CORNERS:
            side_1, side_2 = corner

            if self.parameters.margins[side_1] and self.parameters.margins[side_2]:
                fillet_edges.extend(z_edges.filter_by(Corner2DPredicate(corner)))

        return (
            fillet(fillet_edges, self.parameters.margin_size)
            if fillet_edges
            else diffuser
        )

    def build(self) -> Compound:
        LOGGER.info("Building diffuser")

        length = (
            self.parameters.grid_dimensions.length
            + len(self.parameters.margins.horizontal) * self.parameters.margin_size
        )
        width = (
            self.parameters.grid_dimensions.width
            + len(self.parameters.margins.vertical) * self.parameters.margin_size
        )
        diffuser = Box(
            length,
            width,
            height=self.parameters.thickness,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
        diffuser = self._fillet(diffuser)
        diffuser.color = Color("White", alpha=0.5)
        diffuser.label = "diffuser"
        self._add_grid_joint(diffuser)
        return diffuser
