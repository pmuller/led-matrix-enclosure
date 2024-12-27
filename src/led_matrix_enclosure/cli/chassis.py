from typing import final

from led_matrix_enclosure.cli.cli_tool import CliTool
from led_matrix_enclosure.parts.chassis import Chassis


@final
class SupportCliTool(CliTool):
    builder = Chassis


main = SupportCliTool()
