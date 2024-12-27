from typing import final, override, cast

from build123d import Compound

from led_matrix_enclosure.cli.cli_tool import CliTool
from led_matrix_enclosure.exporter import Exporter
from led_matrix_enclosure.parts.enclosure import Enclosure
from led_matrix_enclosure.helpers import get_compound_child


@final
class EnclosureCliTool(CliTool):
    builder = Enclosure

    @override
    def export(self, exporter: Exporter, part: Compound) -> None:
        for enclosure in cast(tuple[Compound, ...], part.children):
            exporter.export(
                get_compound_child(enclosure, "chassis"),
                f"{self.builder.name}.{enclosure.label}.chassis",
                "stl",
            )
            exporter.export(
                get_compound_child(enclosure, "lid"),
                f"{self.builder.name}.{enclosure.label}.lid",
                "step",
            )


main = EnclosureCliTool()
