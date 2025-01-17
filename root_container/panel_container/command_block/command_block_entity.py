from __future__ import annotations
from typing import TYPE_CHECKING

from root_container.panel_container.command_block.interfaces import ICommandBlock

if TYPE_CHECKING:
    from command_creation.command_definition_database import CommandDefinitionDatabase
    from root_container.panel_container.command_block.command_inserter import CommandInserter
    from models.command_models.command_model import CommandModel
    
from adapter.turn_adapter import TurnAdapter
from data_structures.linked_list import LinkedList
from entity_base.listeners.hover_listener import HoverLambda
from entity_ui.group.variable_group.variable_container import VariableContainer
from entity_ui.group.variable_group.variable_group_container import VariableGroupContainer
from models.command_models.model_based_entity import ModelBasedEntity
from root_container.panel_container.element.overall.row_elements_container import RowElementsContainer
from root_container.panel_container.element.overall.task_commands_container import TaskCommandsContainer




from entity_base.entity import Entity
from entity_base.listeners.click_listener import ClickLambda
from entity_base.listeners.tick_listener import TickLambda
from entity_base.listeners.drag_listener import DragLambda, DragListener
from entity_base.listeners.select_listener import SelectLambda, SelectorType

from adapter.path_adapter import PathAdapter

from command_creation.command_type import CommandType
from command_creation.command_definition import CommandDefinition

from root_container.panel_container.command_block.command_block_header import CommandBlockHeader
from root_container.panel_container.command_expansion.command_expansion_container import CommandExpansionContainer

from root_container.panel_container.element.overall.elements_container_factory import createElementsContainer

from root_container.panel_container.command_block.command_block_constants import CommandBlockConstants as Constants
from common.font_manager import FontID
from common.draw_order import DrawOrder
from data_structures.observer import NotifyType, Observer
from utility.pygame_functions import shade, drawText, drawTransparentRect
from utility.motion_profile import MotionProfile
import pygame, re

"""
A CommandBlockEntity object describes a single instance of a command block
displayed on the right panel.
It references some CommandDefinition at any given point, which specfies the template of the
command. Note the same CommandDefinition may be shared by multiple CommandBlockEntities
The WidgetEntities and pathAdapters hold the informatino for this specific instance.
Position calculation is offloaded to CommandBlockPosition
"""

class CommandBlockEntity(Entity, Observer, ModelBasedEntity, ICommandBlock):

    HIGHLIGHTED = None


    def __init__(self, parent: Entity, model: CommandModel):
        
        self.container = parent
        self.model = model
        self.database = model.database
        
        self.COLLAPSED_HEIGHT = 35
        self.EXPANDED_HEIGHT = 50 

        self.DRAG_OPACITY = 0.7
        self.dragOffset = 0

        # controls height animation
        endValue = 1 if self.model.uiState.expanded else 0
        self.animatedExpansion = MotionProfile(endValue, speed = 0.4)
        # whether to expand by default, ignoring global flags

        r,g,b = self.model.getDefinition().color
        self.colorR = MotionProfile(r, speed = 0.2)
        self.colorG = MotionProfile(g, speed = 0.2)
        self.colorB = MotionProfile(b, speed = 0.2)
        
        # This recomputes position at Entity constructor
        super().__init__(
            parent = parent,
            click = ClickLambda(self, FonLeftClick = self.onClick, FOnMouseDown = self.onMouseDown),
            tick = TickLambda(self, FonTickStart = self.onTick),
            drag = DragLambda(self, FonStartDrag = self.onStartDrag, FonDrag = self.onDrag, FonStopDrag = self.onStopDrag),
            hover = HoverLambda(self),
            drawOrder = DrawOrder.COMMANND_BLOCK,
            recomputeWhenInvisible = True,
            verbose = self.model.isTask(),
            thisUpdatesParent=True
        )

        ModelBasedEntity.__init__(self, self.model)

        self.elementsContainer = None
        self.mouseHoveringCommand = False

        self.elementsVisible = True

        self.headerEntity = CommandBlockHeader(self, self.model.getAdapter(), self.model.getCommandType() == CommandType.CUSTOM)

        self.elementsContainer = createElementsContainer(self, self.model.getDefinition(), self.model.getAdapter())

    def getChildVGC(self) -> VariableGroupContainer:
        if not isinstance(self.elementsContainer, TaskCommandsContainer):
            return None
        
        return self.elementsContainer.vgc
    
    # call whenever database command color changes
    def onColorChange(self):
        # switch to the new definition color (animated)
        r,g,b = self.model.getDefinition().color
        self.colorR.setEndValue(r)
        self.colorG.setEndValue(g)
        self.colorB.setEndValue(b)

    # called when a different name is selected in the dropdown
    def onFunctionChange(self):

        # First, get the definition for the new function
        functionName = self.headerEntity.functionName.getFunctionName()
        definitionID = self.database.getDefinitionIDByName(self.model.getCommandType(), functionName)
        self.model.setDefinitionID(definitionID)

        # Delete old elements container and assign new one
        self.entities.removeEntity(self.elementsContainer)
        self.elementsContainer = createElementsContainer(self, self.model.getDefinition(), self.model.getAdapter())
        self.elementsContainer.recomputeEntity()

        self.model.rebuildChildren()
        print("rebuild children model")

        self.onColorChange()

        # set initial visibility for new elements container
        if self.isFullyCollapsed():
            self.elementsContainer.setInvisible()
            self.elementsVisible = False
        else:
            self.elementsContainer.setVisible()
            self.elementsVisible = True

        # update header entity. Need to show/hide wait entity
        self.headerEntity.onFunctionChange()

        self.recomputeEntity()
        print("recompute tasks")

    # Update animation every tick
    def onTick(self):
        # handle elements visibility
        if self.elementsVisible and self.isFullyCollapsed():
            self.elementsContainer.setInvisible()
            self.elementsVisible = False
        elif not self.elementsVisible and not self.isFullyCollapsed():
            self.elementsContainer.setVisible()
            self.elementsVisible = True

        self.mouseHoveringCommand = self.isSelfOrChildrenHovering()

        self.colorR.tick()
        self.colorG.tick()
        self.colorB.tick()
        # handle color animation
        if self.colorR.wasChange() or self.colorG.wasChange() or self.colorB.wasChange():
            self.headerEntity.functionName.updateColor()

        # handle expansion animation
        if not self.animatedExpansion.isDone():
            #self.animatedPosition.tick()
            self.animatedExpansion.tick()

            self.recomputeEntity()

    # how much the widgets stretch the command by. return the largest one
    def getElementStretch(self) -> int:
        if self.elementsContainer is None:
            return 0
        return self.elementsContainer.defineHeight()

    
    # call only if this is a task command. Get the list of commands inside task
    def getTaskList(self) -> LinkedList[VariableContainer]:

        if not self.model.isTask():
            return None

        taskContainer: TaskCommandsContainer = self.elementsContainer
        return taskContainer.vgc.containers

    
    # Return the list of possible function names for this block
    # If inside a task and is a custom block, cannot contain task
    def getFunctionNames(self) -> list[str]:
        return self.database.getDefinitionNames(self.model.getCommandType(), self.model.parent.isTask())

    def defineWidth(self) -> float:
        return self._pwidth(1)
    
    def defineHeight(self) -> float:

        if not self.isVisible():
            return 0
        
        # calculate target height
        expanded = self.model.uiState.expanded
        
        self.ACTUAL_COLLAPSED_HEIGHT = self._aheight(self.COLLAPSED_HEIGHT)
        self.ACTUAL_EXPANDED_HEIGHT = self._aheight(self.EXPANDED_HEIGHT) + self.getElementStretch()
        self.ACTUAL_HEIGHT = self.ACTUAL_EXPANDED_HEIGHT if expanded else self.ACTUAL_COLLAPSED_HEIGHT

        self.animatedExpansion.setEndValue(1 if expanded else 0)
        
        # current animated height
        ratio = self.animatedExpansion.get()
        height = self.ACTUAL_COLLAPSED_HEIGHT + (self.ACTUAL_EXPANDED_HEIGHT - self.ACTUAL_COLLAPSED_HEIGHT) * ratio
        return height
    
    def defineCenterY(self):
        return self._py(0.5) + self.dragOffset
    
    def getPercentExpanded(self) -> float:
        return self.animatedExpansion.get()
        
    def isFullyCollapsed(self) -> bool:
        return self.animatedExpansion.get() == 0
    
    def isFullyExpanded(self) -> bool:
        return self.animatedExpansion.get() == 1
    
    def getCommandType(self) -> CommandType:
        return self.model.getCommandType()


    # Toggle command expansion. Modify global expansion flags if needed
    def onClick(self, mouse: tuple):
        if self.model.uiState.expanded:
            self.model.collapseUI()
        else:
            self.model.expandUI()

    def onTurnEnableToggled(self):
        if self.model.getCommandType() == CommandType.TURN:
            turnAdapter: TurnAdapter = self.model.getAdapter()
            if turnAdapter.isTurnEnabled():
                self.setVisible(recompute = False)
            else:
                self.setInvisible()

            self.recomputeEntity()

    def getOpacity(self) -> float:
        if self.isDragging():
            return 0.7 # drag opacity
        else:
            return self._parent.getOpacity()
    
    # return 0 if minimized, 1 if maximized, and in between
    def getAddonsOpacity(self) -> float:
        if self.isDragging():
            return self.getOpacity()
        else:
            ratio = self.getPercentExpanded()
            return ratio * self.getOpacity() # square for steeper opacity animation
    
    # return 1 if not dragging, and dragged opacity if dragging
    # not applicable for regular command blocks
    def isDragging(self):
        return self.drag.isDragging

    # Called when the highlight button in the command block is clicked.
    # Should highlight the corresponding node or segment in the path
    def onHighlightPath(self, mouse: tuple):
        pass
        #self.handler.highlightPathFromCommand(self)

    # if mouse down on different command, clear highlight
    def onMouseDown(self, mouse: tuple):
        if CommandBlockEntity.HIGHLIGHTED is not None and CommandBlockEntity.HIGHLIGHTED is not self:
            CommandBlockEntity.HIGHLIGHTED = None

    def onStartDrag(self, mouse: tuple):
        self.startMouseY = mouse[1]
        self.dragOffset = 0

        # cache flattened inserters
        self.getRootEntity().ip.process()

    def onDrag(self, mouse: tuple):
        my = mouse[1]
        self.dragOffset = my - self.startMouseY
        self.recomputeEntity()

        self.getRootEntity().ip.computeClosestInserter(self)

    def onStopDrag(self):
        self.dragOffset = 0

        draggedToInserter = self.getRootEntity().ip.getClosestInserterData()
        if draggedToInserter is not None:
            if draggedToInserter.after is not None:
                self.model.moveThisBefore(draggedToInserter.after.model)
            elif draggedToInserter.before is not None:
                self.model.moveThisAfter(draggedToInserter.before.model)
            else:
                # Replace inserter with command
                self.model.moveThisInsideParent(draggedToInserter.parentModel)

        self.getRootEntity().ip.reset()
        self.recomputeEntity()

    # If dragging, put dragged command on top
    def drawOrderTiebreaker(self) -> float:
        if self.drag.isDragging:
            return 0
        else:
            return None

    def getColor(self) -> tuple:
        r = self.colorR.get()
        g = self.colorG.get()
        b = self.colorB.get()
        return (r, g, b)

    def draw(self, screen: pygame.Surface, isActive: bool, isHovered: bool) -> bool:
        
        isHighlighted = self.model.isHighlighted()

        # draw rounded rect
        color = self.getColor()
        if isHighlighted:
            color = shade(color, 1.4)
        elif isActive and isHovered and self.interactor.leftDragging:
            color = shade(color, 1.3)
        elif self.mouseHoveringCommand and not self.interactor.disableUntilMouseUp:
            color = shade(color, 1.2)
        else:
            color = shade(color, 1.1)

        drawTransparentRect(screen, *self.RECT, color, alpha = self.getOpacity()*255, radius = Constants.CORNER_RADIUS)

        if isHighlighted:
            pygame.draw.rect(screen, (0,0,0), self.RECT, border_radius = Constants.CORNER_RADIUS, width = 2)


    def toString(self) -> str:
        return "Command Block Entity"
        
    def logMoreInfo(self):
        return self.model.getFunctionName()