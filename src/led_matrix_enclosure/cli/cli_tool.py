from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
import logging
from pprint import pformat
from typing import Callable, Protocol, Self

from build123d import Compound

from led_matrix_enclosure.exporter import Exporter
from led_matrix_enclosure.visualizer import Visualizer


LOGGER = logging.getLogger(__name__)
PROJECT_NAME = "led_matrix_enclosure"


CliArgumentProvisioner = Callable[[ArgumentParser], None]


class Builder(Protocol):
    #: The name of the part to build
    name: str

    @classmethod
    def add_cli_arguments(cls, parser: ArgumentParser) -> None: ...

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self: ...

    def build(self) -> Compound: ...


class CliTool:
    builder: type[Builder]  # pyright: ignore[reportUninitializedInstanceVariable]

    def _setup_logging(self, *, debug: bool = False) -> None:
        # Only show warnings and errors from 3rd party libraries
        logging.basicConfig(level=logging.WARNING)
        # Set the verbosity of the project's logger
        logging.getLogger(PROJECT_NAME).setLevel(
            logging.DEBUG if debug else logging.INFO
        )

    def _parse_arguments(self, argv: Sequence[str] | None = None) -> Namespace:
        parser = ArgumentParser()

        self.builder.add_cli_arguments(parser)
        Exporter.add_cli_arguments(parser)
        Visualizer.add_cli_arguments(parser)

        logging_group = parser.add_argument_group("Logging")
        _ = logging_group.add_argument(
            "--debug",
            "-D",
            action="store_true",
            help="Enable debug logging",
        )

        arguments = parser.parse_args(argv)

        # Yes, it's weird to setup logging in _parse_arguments,
        # but we need to do it here cause we use Logger.debug() in the next statement.
        self._setup_logging(debug=arguments.debug)  # pyright: ignore[reportAny]

        LOGGER.debug("CLI arguments: %s", pformat(arguments))

        return arguments

    def export(
        self,
        exporter: Exporter,
        part: Compound,
    ) -> None:
        exporter.export(part, self.builder.name, format="step")

    def __call__(self) -> None:
        # Parse the CLI arguments
        arguments = self._parse_arguments()
        # Build the part
        part = self.builder.from_cli_arguments(arguments).build()
        # Log the part's topology
        LOGGER.debug("Topology:\n%s", part.show_topology())
        # Export the part, if requested
        self.export(Exporter.from_cli_arguments(arguments), part)
        # Show the part, if requested
        Visualizer.from_cli_arguments(arguments).show(part)
