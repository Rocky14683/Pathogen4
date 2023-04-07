from __future__ import annotations
from typing import TYPE_CHECKING
from common.font_manager import FontID
if TYPE_CHECKING:
    from root_container.panel_container.command_block.command_block_entity import CommandBlockEntity

from entity_base.entity import Entity
from entity_base.text_entity import TextEntity


# trash button for custom commands
class FunctionNameEntity(Entity):

    def __init__(self, parentHeader, parentCommand: CommandBlockEntity):
        
        super().__init__(parent = parentHeader)
        self.recomputePosition()

        TextEntity(self, fontID = FontID.FONT_NORMAL, fontSize = 15, textFunction = parentCommand.getFunctionName, isAlignCenter = False)


    def defineLeftX(self) -> tuple:
        return self._ax(30)
    
    def defineCenterY(self) -> float:
        return self._py(0.5)

    # must impl both of these if want to contain other entity
    def defineWidth(self) -> float:
        return self._pheight(0.8) # yes, this is height not width. square icon
    def defineHeight(self) -> float:
        return self._pheight(0.8)