from argparse import ArgumentParser, Namespace
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Self

from build123d import Compound
import build123d


LOGGER = logging.getLogger(__name__)

ExportFormat = Literal["stl", "step"]


def _get_exporter(format: ExportFormat) -> Callable[[Compound, str], None]:
    match format:
        case "stl":
            return build123d.export_stl  # pyright: ignore[reportUnknownMemberType,reportReturnType,reportUnknownVariableType]
        case "step":
            return build123d.export_step  # pyright: ignore[reportUnknownMemberType,reportReturnType,reportUnknownVariableType]

    raise ValueError(f"Unknown format: {format}")  # pyright: ignore[reportUnreachable]


@dataclass
class Exporter:
    #: Directory to put the build files in
    directory: Path
    #: Build name
    name: str | None = None
    #: Export the object?
    enable_export: bool = True

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None:
        group = parser.add_argument_group(title="Exporter")
        _ = group.add_argument(
            "--build-dir",
            metavar="DIR",
            default=Path("./build"),
            type=Path,
            help="Where to put the build files (default: %(default)s)",
        )
        _ = group.add_argument(
            "--build-name",
            metavar="NAME",
            type=str,
            help="Name of the build (optional)",
        )
        _ = group.add_argument(
            "--no-export",
            dest="enable_export",
            action="store_false",
            default=True,
            help="Don't export the object",
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            directory=arguments.build_dir,  # pyright: ignore[reportAny]
            name=arguments.build_name,  # pyright: ignore[reportAny]
            enable_export=arguments.enable_export,  # pyright: ignore[reportAny]
        )

    def _build_path(self, object_name: str, extension: str) -> str:
        return (
            f"{self.directory}/{object_name}.{self.name}.{extension}"
            if self.name
            else f"{self.directory}/{object_name}.{extension}"
        )

    def export(
        self,
        part: Compound,
        object_name: str,
        format: ExportFormat,
    ) -> None:
        if self.enable_export:
            path = self._build_path(object_name, format)
            LOGGER.info(f"Exporting {path}")
            _get_exporter(format)(part, path)
        else:
            LOGGER.info(f"Skipping export of {object_name}")
