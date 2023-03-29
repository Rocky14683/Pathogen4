from NodeEntities.circle_mixin import CircleMixin
from BaseEntity.independent_entity import IndependentEntity
from reference_frame import PointRef, VectorRef
from BaseEntity.EntityFunctions.drag_function import DragLambda
from BaseEntity.EntityFunctions.click_function import ClickLambda
from BaseEntity.EntityFunctions.select_function import Select, SelectLambda
from SegmentEntities.path_segment_entity import PathSegmentEntity
from draw_order import DrawOrder

from Adapters.adapter import AdapterInterface
from Adapters.turn_adapter import TurnAdapter

from math_functions import isInsideBox
from pygame_functions import shade

"""
Interactable path nodes
PathSegmentEntities connect two PathNodeEntities
Referenced in PathSection
"""

class PathNodeEntity(IndependentEntity, CircleMixin, AdapterInterface):

    BLUE_COLOR = (102, 153, 255)
    FIRST_BLUE_COLOR = (40, 40, 255)

    def __init__(self, section, position: PointRef, prevSegment: PathSegmentEntity = None, nextSegment: PathSegmentEntity = None):
        super().__init__(
            position = position,
            drag = DragLambda(
                self,
                FcanDragOffset = lambda offset: isInsideBox(*(self.getPosition()+offset).fieldRef, 0, 0, 144, 144),
                FdragOffset = lambda offset: self.move(offset)
            ),
            select = SelectLambda(self, "path node", FgetHitboxPoints = self.getHitboxPoints),
            click = ClickLambda(self, FonLeftClick = lambda : print("left click"), FonRightClick = lambda : print("right click")),
            drawOrder = DrawOrder.NODE
            )
        
        self.section = section
        
        CircleMixin.__init__(self, 10, 12)

        self.prevSegment = prevSegment
        self.nextSegment = nextSegment

        self.adapter: TurnAdapter = TurnAdapter()
        self.updateAdapter()

    def getColor(self) -> tuple:
        return self.FIRST_BLUE_COLOR if self.section.previous is None else self.BLUE_COLOR

    def getAdapter(self) -> TurnAdapter:
        return self.adapter
    
    def updateAdapter(self) -> None:
        if self.prevSegment is None and self.nextSegment is None:
            self.adapter.set(0,0)
        elif self.prevSegment is not None and self.nextSegment is None:
            angle = self.prevSegment.getEndTheta()
            self.adapter.set(angle, angle)
        elif self.nextSegment is not None and self.prevSegment is None:
            angle = self.nextSegment.getStartTheta()
            self.adapter.set(angle, angle)
        else:
            startAngle = self.prevSegment.getEndTheta()
            endAngle = self.nextSegment.getEndTheta()
            self.adapter.set(startAngle, endAngle)

    def move(self, offset: VectorRef):
        self.position += offset
        if not self.prevSegment is None:
            self.prevSegment.updateAdapter()
        if not self.nextSegment is None:
            self.nextSegment.updateAdapter()
        self.updateAdapter()