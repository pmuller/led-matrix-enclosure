from dataclasses import dataclass

from led_matrix_enclosure.parameters.lid_diffuser import LidDiffuserParameters
from led_matrix_enclosure.parameters.lid_grid import LidGridParameters


@dataclass(frozen=True)
class LidParameters:
    grid: LidGridParameters
    diffuser: LidDiffuserParameters
