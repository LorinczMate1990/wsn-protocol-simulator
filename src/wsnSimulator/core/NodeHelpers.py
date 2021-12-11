#!/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
   from wsnSimulator.core.NodeSkeleton import NodeSkeleton

from random import random  

class ChannelStateDescriptor(object):
   def __init__(self):
      self.counter = 1
      self.__jammed = False
      
   def newMessage(self):
      self.counter +=1
      self.__jammed = True
      
   def endMessage(self):
      self.counter -= 1
      
   def destroyable(self):
      return self.counter == 0
   
   def jammed(self):
      return self.__jammed

class ReachableDescriptor(object):
   def __init__(self, to : NodeSkeleton, propability : float):
      self.to = to
      self.propability = propability
      
   def success(self) -> bool:
      return random()<self.propability

class Battery(object):
   def __init__(self):
      self.powerLevel : float = float('inf')
   
   def drain(self, energy : float):
      self.powerLevel -= energy
   
   def hasPower(self):
      return self.powerLevel > 0

class NodeIconDescriptor(object):
   def __init__(self, width : int, icon : str):
      self.width=width
      self.icon=icon