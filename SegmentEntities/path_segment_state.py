from abc import ABC, abstractmethod
from enum import Enum
from reference_frame import PointRef
from BaseEntity.entity import Entity
from linked_list import LinkedListNode
from Adapters.path_adapter import PathAdapter
import pygame

"""
Following the State design pattern, an interface for segment shapes (straight, arc, etc.)
Also provides an interface for getting thetas at both sides, and holding references to nodes
"""

class PathSegmentState(ABC):
    def __init__(self, segment: Entity | LinkedListNode) -> None:
        self.segment = segment # type PathSegmentEntity (the parent)

    @abstractmethod
    def getAdapter(self) -> PathAdapter:
        pass

    @abstractmethod
    def updateAdapter(self) -> None:
        pass

    @abstractmethod
    def getStartTheta(self) -> float:
        pass

    @abstractmethod
    def getEndTheta(self) -> float:
        pass

    @abstractmethod
    def isTouching(self, position: PointRef) -> bool:
        pass

    @abstractmethod
    def distanceTo(self, position: PointRef) -> float:
        pass

    @abstractmethod
    def getPosition(self) -> PointRef:
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface, isActive: bool, isHovered: bool) -> bool:
        pass

    @abstractmethod
    def toString(self) -> str:
        pass