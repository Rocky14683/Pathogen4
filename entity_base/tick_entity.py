import entity_base.entity as entity
from entity_base.listeners.tick_listener import TickLambda
from common.draw_order import DrawOrder

"""
Used when you want to run some function every tick at some specific order
"""

class TickEntity(entity.Entity):

    def __init__(self, onTickStart = lambda: None, onTickEnd = lambda: None, drawOrder: DrawOrder = DrawOrder.BACK):

        super().__init__(parent = entity.ROOT_CONTAINER,
                         tick = TickLambda(self, FonTickStart = onTickEnd, FonTickEnd = onTickEnd),
                         drawOrder = drawOrder, initiallyVisible = False,
                         recomputeWhenInvisible = True
                         )