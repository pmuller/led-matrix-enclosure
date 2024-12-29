from typing import TYPE_CHECKING
from dataclasses import dataclass


from led_matrix_enclosure.dimensions import Dimension3D, Object2D
from led_matrix_enclosure.parameters.chassis_borders import ChassisBordersParameters
from led_matrix_enclosure.parameters.chassis_bottom import ChassisBottomParameters
from led_matrix_enclosure.parameters.chassis_module_connectors import (
    ChassisModuleConnectorsParameters,
)
from led_matrix_enclosure.parameters.chassis_pillar import ChassisPillarParameters


@dataclass(frozen=True)
class ChassisParameters:
    #: Inner dimensions of the chassis
    inner_dimensions: Dimension3D
    #: Outer dimensions of the chassis
    outer_dimensions: Dimension3D
    #: Panel connectors positions (optional)
    panel_connectors: tuple[Object2D, ...]
    #: Pillar parameters
    pillar: ChassisPillarParameters
    #: Module connectors parameters
    module_connectors: ChassisModuleConnectorsParameters
    #: Borders parameters
    borders: ChassisBordersParameters
    #: Bottom parameters
    bottom: ChassisBottomParameters
    #: Module parameters
    module: "ModuleParameters"


# Only import ModuleParameters for type checking
if TYPE_CHECKING:
    from led_matrix_enclosure.parameters.module import ModuleParameters
# pyright: reportImportCycles=false
