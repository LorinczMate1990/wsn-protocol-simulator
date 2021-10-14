#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import random  
from Field import *
from pygame import *
from ImageLoader import *

nodeCounter = 0

class ChannelStateDescriptor:
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

class ReachableDescriptor:
   def __init__(self, to, propability):
      self.to = to
      self.propability = propability
      
   def success(self):
      return random()<self.propability

class Battery:
   def __init__(self):
      self.powerLevel = float('inf')
   
   def drain(self, energy):
      self.powerLevel -= energy
   
   def hasPower(self):
      return self.powerLevel > 0

class NodeSkeleton:
   def __init__(self, x, y, asyncPropability):
      global nodeCounter
      self.x=x # Position on the world. The painting, visualisation and the default connection tester are based on x and y
      self.y=y
      self.ID=nodeCounter # The node's unique name. It's uniquness is vital for the simulation, that's why it's generated automaticly.
      nodeCounter+=1
      self.__needRecheckConnections = True
      self.reachables = [] # The neighbours. Sometimes, it's practical during the simulation to know the neighbours, that's why it's not marked with _ or __
      self.asyncPropability = asyncPropability # If this is 1, than this node's periodicEvent will call in every periodic event cycle. If this is 0, then never
      self.__channelUsage={}
      self._RXMode = False
      self.periodicSpeedScale = 1 # Only in every periodicSpeedScale-th period will the periodicEvent run. This must be a positive integer number.
      self.periodicEventCounter = 0
      self.battery = Battery()
      self.periodicEventEnergyConsumption = 0 # Every periodicEvent will drain the battery with periodicEventEnergyConsumption
            
   def move(self, x, y):
      self.x=x
      self.y=y
      self.__needRecheckConnections = True
      
   def isRXMode(self):
      return self._RXMode
   def _setFieldReference(self, field):
      self.field = field
   def getConnectionState(self):
      return self.__needRecheckConnections
   def _connectionsRechecked(self):
      self.__needRecheckConnections = False # This should only call by the core/Field after the connections are rechecked
   def connectionsInvalidated(self):
      self.__needRecheckConnections = True # For example if the node's moved or changed its transmit power
   def init(self): pass # This is the first function called by the environment. It's called only once
   def sensorEvent(self, value): pass # Sensor-like events. Can be periodic or event-driven dependent on the config
   def _periodicEvent(self):
      if random()<=self.asyncPropability:
         self.periodicEventCounter +=1
         if self.periodicEventCounter % self.periodicSpeedScale == 0:
            self.periodicEvent()
            self.battery.drain(self.periodicEventEnergyConsumption)
         return True
      return False
   def periodicEvent(self): pass # Runs periodicly. (Can be set assincronity by setting the self.asyncPropability)
   def messageEvent(self, data): pass # Runs if the node receives a message
   def _beginChannelUse(self, channel): # If a message begins to use a channel, it will call this function
      if self.__channelUsage.has_key(channel):
         self.__channelUsage[channel].newMessage()
      else:
         self.__channelUsage[channel] = ChannelStateDescriptor()
      
   def _endChannelUse(self, channel): # If the sending of a message is finished, it will call this function
      descriptor=self.__channelUsage[channel]
      descriptor.endMessage()
      if descriptor.destroyable():
         del self.__channelUsage[channel]
      return not descriptor.jammed()
   def sendMessage(self, data, duration, channel=1):
      if self._RXMode: return False
      self.field.sendMessage(self.reachables, data, duration, channel, self)
      self._beginChannelUse(channel)

class NodeIconDescriptor:
   def __init__(self, width, icon):
      self.width=width
      self.icon=icon
     
class GraphNodeSkeleton(NodeSkeleton):
   def __init__(self, x, y, asyncPropability):
      NodeSkeleton.__init__(self, x, y, asyncPropability)
      self.image = NodeIconDescriptor(30, (255,0,0))
      
   def setImage(self,image):
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
