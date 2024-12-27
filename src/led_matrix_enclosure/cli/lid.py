from typing import final

from led_matrix_enclosure.cli.cli_tool import CliTool
from led_matrix_enclosure.parts.lid import Lid


@final
class LidCliTool(CliTool):
    builder = Lid


main = LidCliTool()
