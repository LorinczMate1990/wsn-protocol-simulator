#!/bin/env python

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
   def __init__(self, to, propability):
      self.to = to
      self.propability = propability
      
   def success(self):
      return random()<self.propability

class Battery(object):
   def __init__(self):
      self.powerLevel = float('inf')
   
   def drain(self, energy):
      self.powerLevel -= energy
   
   def hasPower(self):
      return self.powerLevel > 0

class NodeIconDescriptor(object):
   def __init__(self, width, icon):
      self.width=width
      self.icon=icon