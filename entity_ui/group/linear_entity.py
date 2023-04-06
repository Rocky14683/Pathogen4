from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entity_ui.group.linear_group_entity import LinearGroupEntity

from entity_base.entity import Entity

"""
A single option object for a RadioGroup
"""
class LinearEntity(Entity):

    # id is used to distinguish between radio entities
    def __init__(self, group: LinearGroupEntity, id: str):
        super().__init__(group)

        self.group = group
        self.id = id
        self.i = group.add(self)

    def defineCenter(self) -> tuple:
        if self.group.isHorizontal:
            return self._px(1) / self.group.N, self._py(0.5)
        else:
            return self._px(0.5), self._py(1) / self.group.N