from UIEntities.radio_group_entity import RadioGroupEntity
from dimensions import Dimensions

"""a group of radio_entities, where only one is selected at a time
If allowNoSelect is True, then no option being selected is allowed
Child of Panel Entity
"""
class TabGroupEntity(RadioGroupEntity):

    def getTopLeft(self) -> tuple:
        return self._px(0), self._py(0)

    def getWidth(self) -> float:
        return self._pwidth(0)
    def getHeight(self) -> float:
        return self._pheight(0.05)