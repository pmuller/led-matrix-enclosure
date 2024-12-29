from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
import logging
from typing import cast

from build123d import Compound

from led_matrix_enclosure.builders.enclosure import EnclosureBuilder
from led_matrix_enclosure.exporter import Exporter
from led_matrix_enclosure.helpers import get_compound_child
from led_matrix_enclosure.parameters.enclosure import EnclosureParameters
from led_matrix_enclosure.visualizer import Visualizer

LOGGER = logging.getLogger(__name__)
PROJECT_NAME = "led_matrix_enclosure"


def _parse_arguments(argv: Sequence[str] | None = None) -> Namespace:
    parser = ArgumentParser()

    EnclosureParameters.add_cli_arguments(parser)
    Exporter.add_cli_arguments(parser)
    Visualizer.add_cli_arguments(parser)

    logging_group = parser.add_argument_group("Logging")
    _ = logging_group.add_argument(
        "--debug",
        "-D",
        action="store_true",
        help="Enable debug logging",
    )

    return parser.parse_args(argv)


def _setup_logging(*, debug: bool = False) -> None:
    # Only show warnings and errors from 3rd party libraries
    logging.basicConfig(level=logging.WARNING)
    # Set the verbosity of the project's logger
    logging.getLogger(PROJECT_NAME).setLevel(logging.DEBUG if debug else logging.INFO)


def _export(exporter: Exporter, enclosure: Compound) -> None:
    for module in cast(tuple[Compound, ...], enclosure.children):
        exporter.export(
            get_compound_child(module, "chassis"),
            f"{module.label}.chassis",
            "stl",
        )
        exporter.export(
            get_compound_child(module, "lid"),
            f"{module.label}.lid",
            # Export the lid as STEP because we need to colorize its parts in the slicer
            "step",
        )


def main(argv: Sequence[str] | None = None) -> None:
    # Parse the CLI arguments
    namespace = _parse_arguments(argv)
    # Setup logging
    _setup_logging(debug=namespace.debug)  # pyright: ignore[reportAny]
    LOGGER.debug("CLI arguments: %s", namespace)
    # Build the part
    enclosure = EnclosureBuilder(
        EnclosureParameters.from_cli_arguments(namespace)
    ).build()
    # Log the part's topology
    LOGGER.debug("Topology:\n%s", enclosure.show_topology())
    # Export the part, if requested
    _export(Exporter.from_cli_arguments(namespace), enclosure)
    # Show the part, if requested
    Visualizer.from_cli_arguments(namespace).show(enclosure)
