from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity_ui.group.variable_group.variable_container import VariableContainer
    from entity_ui.group.variable_group.variable_group_container import VariableGroupContainer
    from models.command_models.full_model import FullModel
    from root_container.panel_container.command_block.full_container import FullContainer


from root_container.panel_container.command_block.interfaces import ICommandInserter

from entity_base.entity import Entity
from entity_base.listeners.hover_listener import HoverLambda
from entity_base.listeners.click_listener import ClickLambda
from entity_base.listeners.select_listener import SelectLambda, SelectorType

from root_container.panel_container.command_block.command_block_entity import CommandBlockEntity

from entity_handler.interactor import Interactor

from root_container.panel_container.command_block.command_block_constants import CommandBlockConstants as Constants

from common.dimensions import Dimensions
from data_structures.linked_list import LinkedListNode
from common.reference_frame import PointRef, Ref
from common.draw_order import DrawOrder

from utility.math_functions import isInsideBox2

import pygame

"""
Appears between each command
A "plus" button that, when clicked, inserts a custom command there
"""

class CommandInserter(Entity, ICommandInserter):

    def __init__(self, parent: VariableContainer, fullModel: FullModel, onInsert = lambda: None, isFirst: bool = False):
        

        super().__init__(
            parent = parent,
            hover = HoverLambda(self, FonHoverOn = self.onHoverOn, FonHoverOff = self.onHoverOff),
            click = ClickLambda(self, FonLeftClick = lambda mouse: onInsert()),
            select = SelectLambda(self, "inserter", type = SelectorType.SOLO),
            drawOrder = DrawOrder.COMMAND_INSERTER,
            recomputeWhenInvisible = True,
            thisUpdatesParent=True
            )
        
        self.container = parent
        self.fullModel = fullModel
        self.isFirst = isFirst
        
        self.HEIGHT_MIN = 6
        self.HEIGHT_MAX = 12

        # shaded area specs
        self.X_MARGIN_LEFT = 6
        self.X_MARGIN_RIGHT = 18
        self.Y_MARGIN = 3
        self.MOUSE_MARGIN = 0

        # cross specs
        self.RADIUS = 6
        self.HOVER_RADIUS = 8
        self.THICK = 3 # cross thick radius
        self.THIN = 1 # cross thin radius


    def defineCenterX(self) -> tuple:
        return self._px(0.5)

    def defineWidth(self) -> float:
        return self._pwidth(1)
    
    def defineHeight(self) -> float:

        if not self.isVisible():
            return 0

        return self._aheight(self.HEIGHT_MAX if self.hover.isHovering else self.HEIGHT_MIN)

    def onHoverOn(self):
        self.recomputeEntity()

    def onHoverOff(self):
        self.recomputeEntity()

    def draw(self, screen: pygame.Surface, isActive: bool, isHovered: bool) -> bool:

        Y_MARGIN = 2
        try:
            rect = [self.LEFT_X, self.TOP_Y + Y_MARGIN, self.WIDTH, self.HEIGHT - Y_MARGIN*2]
        except:
            raise Exception("error", self)
        color = [68, 208, 96]

        if self.hover.isHovering:

            # draw shaded area
            pygame.draw.rect(screen, color, rect, border_radius = Constants.CORNER_RADIUS)

            # draw cross
            x,y = self.CENTER_X, self.CENTER_Y
            pygame.draw.rect(screen, [255,255,255], [x - self.THICK, y - self.THIN, self.THICK*2, self.THIN*2])
            pygame.draw.rect(screen, [255,255,255], [x - self.THIN, y - self.THICK, self.THIN*2, self.THICK*2])
        else:
            fc: FullContainer = self.fullModel.ui
            if fc.ip.getClosestInserter() is self:
                pygame.draw.rect(screen, color, rect, border_radius = Constants.CORNER_RADIUS)
            