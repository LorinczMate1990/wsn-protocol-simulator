#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'core')
from core.NodeSkeleton import *
from core.NodeHelpers import *
from random import *

class BasicNode(GraphNodeSkeleton):
   def init(self):
      self.counter = 0
      self.randomDelay = 0
      if (self.ID==3):
         self.randomDelay=1
      else:
         self.randomDelay=0
         
   def sensorEvent(self,value): pass # Sensor-like events. Can be periodic or event-driven dependent on the config
  
   def periodicEvent(self): # Runs periodicly. (Can be set asyncronity in the config-file)
      if self.randomDelay>=0: self.randomDelay-=1
      self.image = NodeIconDescriptor(20, "media/1.jpg")
      if self.randomDelay == 0: 
         self.sendMessage((3,2,1), 10)
         self.image = NodeIconDescriptor(20,(255,0,0))
   
   def messageEvent(self, data): # Runs if the node receives a valid message
      self.randomDelay=randint(1, 20)
