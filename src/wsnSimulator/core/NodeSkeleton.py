#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import *

from random import random  
from wsnSimulator.core.Field import *
from wsnSimulator.core.NodeHelpers import *
from pygame import *
from wsnSimulator.utility.ImageLoader import *

class NodeSkeleton(object):
   nodeCounter = 0
   def __init__(self, x : int, y : int, *args, **kwargs):
      global nodeCounter
      self.x = x # Position on the world. The painting, visualisation and the default connection tester are based on x and y
      self.y = y
      self.ID = NodeSkeleton.nodeCounter # The node's unique name. It's uniquness is vital for the simulation, that's why it's generated automaticly.
      NodeSkeleton.nodeCounter += 1
      self.__needRecheckConnections = True
      self.reachables : list[ReachableDescriptor] = [] # The neighbours. Sometimes, it's practical during the simulation to know the neighbours, that's why it's not marked with _ or __
      self.asyncPropability = 1 # If this is 1, than this node's periodicEvent will call in every periodic event cycle. If this is 0, then never
      self.__channelUsage : dict[int, ChannelStateDescriptor] = {}
      self._RXMode = False
      self.periodicSpeedScale = 1 # Only in every periodicSpeedScale-th period will the periodicEvent run. This must be a positive integer number.
      self.periodicEventCounter = 0
      self.battery = Battery()
      self.periodicEventEnergyConsumption = 0 # Every periodicEvent will drain the battery with periodicEventEnergyConsumption
      self.initObject(x, y, *args, *kwargs)
            
   def move(self, x : int, y : int) -> None:
      self.x=x
      self.y=y
      self.__needRecheckConnections = True
      
   def isRXMode(self) -> bool:
      return self._RXMode

   def _setFieldReference(self, field : Field) -> None:
      self.field = field

   def getConnectionState(self) -> bool:
      return self.__needRecheckConnections

   def _connectionsRechecked(self) -> None:
      self.__needRecheckConnections = False # This should only call by the core/Field after the connections are rechecked
   
   def connectionsInvalidated(self) -> None:
      self.__needRecheckConnections = True # For example if the node's moved or changed its transmit power
   
   def initObject(self, x, y, *args, **kwargs) -> None: pass # This function is called by the constructor, it gets every arguments from it
   def firstTick(self) -> None: pass # This is the first function called by the environment in the first tick. 
   
   def sensorEvent(self, value) -> None: pass # Sensor-like events. Can be periodic or event-driven dependent on the config
   
   def _periodicEvent(self) -> None:
      if random()<=self.asyncPropability:
         self.periodicEventCounter +=1
         if self.periodicEventCounter % self.periodicSpeedScale == 0:
            self.periodicEvent()
            self.battery.drain(self.periodicEventEnergyConsumption)
         return True
      return False

   def periodicEvent(self) -> None: pass # Runs periodicly. (Can be set assincronity by setting the self.asyncPropability)
   
   def messageEvent(self, data) -> None: pass # Runs if the node receives a message
   
   # TODO : Why there is no newMessage call in the else line?
   def _beginChannelUse(self, channel : int): # If a message begins to use a channel, it will call this function
      if channel in self.__channelUsage:
         self.__channelUsage[channel].newMessage()
      else:
         self.__channelUsage[channel] = self.field.getChannelStateDescriptor(channel)
      
   def _endChannelUse(self, channel : int) -> None: # If the sending of a message is finished, it will call this function
      descriptor=self.__channelUsage[channel]
      descriptor.endMessage()
      if descriptor.destroyable():
         del self.__channelUsage[channel]
      return not descriptor.jammed()

   def sendMessage(self, data, duration, channel=1):
      if self._RXMode: return False
      self.field.sendMessage(self.reachables, data, duration, channel, self)
      self._beginChannelUse(channel)
     
class GraphNodeSkeleton(NodeSkeleton):
   def __init__(self, x : int, y : int, asyncPropability : float):
      NodeSkeleton.__init__(self, x, y, asyncPropability)
      self.image = NodeIconDescriptor(30, (255,0,0))
      
   def setImage(self, image : tuple | str):
      self.image = image

   def _draw(self, screen):
      width = self.image.width
      icon = self.image.icon
      if type(icon) == type(()):
         pygame.draw.rect(screen, icon, pygame.Rect(self.x-width/2, self.y-width/2, width, width))
      elif type(icon)==type(""):
         loader = ImageLoader()
         image = loader.getImage(icon)
         image = transform.scale(image, (width, width))
         screen.blit(image, (self.x-width/2, self.y-width/2))
      else:
         pass # TODO: Error
