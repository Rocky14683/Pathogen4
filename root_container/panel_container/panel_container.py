from abc import ABC, abstractmethod
from enum import Enum
from common.reference_frame import PointRef, Ref

import entity_base.entity as entity
from common.draw_order import DrawOrder

from utility.math_functions import distance
import pygame

"""
An entity for the panel on the right side. Holds other entities inside
"""

class PanelContainer(entity.Entity):

    # drawOrder is a number, in which the lowest number is drawn in the front (highest number is drawn first)
    def __init__(self, color) -> None:
        super().__init__(parent = entity.ROOT_CONTAINER, drawOrder = DrawOrder.PANEL_BACKGROUND)
        self.color = color
        self.recomputePosition()

    # override
    def draw(self, screen: pygame.Surface, isActive: bool, isHovered: bool) -> bool:
        pygame.draw.rect(screen, self.color, *self.RECT)


    def defineTopLeft(self) -> tuple:
        return self.dimensions.FIELD_WIDTH, 0

    # must impl both of these if want to contain other entity
    def defineWidth(self) -> float:
        return self.dimensions.PANEL_WIDTH
    def defineHeight(self) -> float:
        return self.dimensions.SCREEN_HEIGHT