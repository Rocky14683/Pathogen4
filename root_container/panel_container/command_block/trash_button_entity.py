from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from root_container.panel_container.command_block.command_block_entity import CommandBlockEntity

from entity_base.container_entity import Container
from entity_base.listeners.click_listener import ClickLambda
from entity_base.listeners.hover_listener import HoverLambda

from entity_base.image.image_entity import ImageEntity

from common.image_manager import ImageManager, ImageID
from common.dimensions import Dimensions

from common.draw_order import DrawOrder
from common.reference_frame import PointRef, Ref
from utility.pygame_functions import drawSurface
from utility.math_functions import distance
import pygame

# trash button for custom commands
class TrashEntity(Container):

    def __init__(self, parentCommand: CommandBlockEntity, onDelete = lambda: None):
        
        super().__init__(parent = parentCommand)

        ImageEntity(self, imageID = ImageID.TRASH_OFF, imageIDHovered = ImageID.TRASH_ON, drawOrder = DrawOrder.WIDGET, onClick = onDelete)

    def defineCenter(self) -> tuple:
        return self._px(1) - self._ax(60), self._py(0.5)

    # must impl both of these if want to contain other entity
    def defineWidth(self) -> float:
        return self._pheight(0.8) # yes, this is height not width. square icon
    def defineHeight(self) -> float:
        return self._pheight(0.8)