from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
import logging
from typing import Self

from build123d import Compound, Text, Location, Color, VectorLike, Box
from ocp_vscode import show_object  # pyright: ignore[reportMissingTypeStubs,reportUnknownVariableType]


LOGGER = logging.getLogger(__name__)


@dataclass
class Visualizer:
    #: Show the object?
    enabled: bool
    #: Show side names?
    show_side_names: bool
    #: Show the object's bounding box?
    show_bounding_box: bool
    #: Show joints?
    show_joints: bool

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Visualizer")
        _ = group.add_argument(
            "--no-show",
            default=True,
            dest="visualization_enabled",
            action="store_false",
            help="Do not show the object",
        )
        _ = group.add_argument(
            "--show-side-names",
            default=False,
            dest="visualization_show_side_names",
            action="store_true",
            help="Show side names",
        )
        _ = group.add_argument(
            "--show-bounding-box",
            default=False,
            dest="visualization_show_bounding_box",
            action="store_true",
            help="Show the object's bounding box",
        )
        _ = group.add_argument(
            "--show-joints",
            default=False,
            dest="visualization_joints",
            action="store_true",
            help="Show the object's joints",
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            enabled=arguments.visualization_enabled,  # pyright: ignore[reportAny]
            show_side_names=arguments.visualization_show_side_names,  # pyright: ignore[reportAny]
            show_bounding_box=arguments.visualization_show_bounding_box,  # pyright: ignore[reportAny]
            show_joints=arguments.visualization_joints,  # pyright: ignore[reportAny]
        )

    def _build_side_name(
        self,
        name: str,
        position: VectorLike,
        font_size: float = 10,
        rotation: float = 0,
        color: Color | None = None,
    ) -> Text:
        text = Text(
            name,
            font_size=font_size,
            rotation=rotation,
        ).move(Location(position))
        text.color = color or Color("black")
        text.label = name
        return text

    def _show_side_names(
        self, part: Compound, font_size: float = 10, offset: float = 10
    ) -> None:
        # Get the bounding box
        bounding_box = part.bounding_box()
        center = bounding_box.center()
        show_object(
            [
                self._build_side_name(
                    "Back",
                    (center.X, bounding_box.max.Y + offset, 0),
                    font_size,
                ),
                self._build_side_name(
                    "Front",
                    (center.X, bounding_box.min.Y - offset, 0),
                    font_size,
                ),
                self._build_side_name(
                    "Left",
                    (bounding_box.min.X - offset, center.Y, 0),
                    font_size,
                    rotation=90,
                ),
                self._build_side_name(
                    "Right",
                    (bounding_box.max.X + offset, center.Y, 0),
                    font_size,
                    rotation=90,
                ),
            ],
            name="Side names",
        )

    def _show_bounding_box(self, part: Compound) -> None:
        bounding_box = part.bounding_box()
        show_object(
            Box(
                length=bounding_box.max.X - bounding_box.min.X,
                width=bounding_box.max.Y - bounding_box.min.Y,
                height=bounding_box.max.Z - bounding_box.min.Z,
            )
            .translate(bounding_box.center())
            .edges(),
            name="Bounding box",
        )

    def show(self, part: Compound, name: str | None = None) -> None:
        show_name = name or part.label or part

        if self.enabled:
            LOGGER.info(f"Showing {show_name}")
            show_object(part, name=show_name, render_joints=self.show_joints)

            if self.show_side_names:
                self._show_side_names(part)

            if self.show_bounding_box:
                self._show_bounding_box(part)

        else:
            LOGGER.info(f"Skipping show of {show_name}")
