#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nodes.BasicNode import *
from wsnSimulator.core.Field import *
from wsnSimulator.core.DataCollector import FieldDataCollector

maxRange = 100

def checkBinaryConnection(a, b):
   if pow(a.x-b.x,2)+pow(a.y-b.y,2)<pow(maxRange,2):
      return 1
   else:
      return 0
      
def calculateConnectionPropability(a,b):
   if pow(a.x-b.x,2)+pow(a.y-b.y,2)<pow(maxRange,2):
      return 1.*(pow(maxRange,2)-pow(a.x-b.x,2)-pow(a.y-b.y,2)) / pow(maxRange,2)
   else:
      return 0
      
def calculateNonlinearConnectionPropability(a,b):
   if pow(a.x-b.x,2)+pow(a.y-b.y,2)<pow(62,2):
      return 1
   elif pow(a.x-b.x,2)+pow(a.y-b.y,2)<pow(100,2):
      return 1.*(pow(maxRange,2)-pow(a.x-b.x,2)-pow(a.y-b.y,2)) / pow(maxRange,2)
   else:
      return 0

if __name__ == '__main__':
   field = GraphFieldHandler(calculateNonlinearConnectionPropability, 400, 400)
   fieldDataCollector = FieldDataCollector(field,
      {
         "randomDelay": "randomDelay",
         "Received messages": "messageCounter",
         "Power level": "battery.powerLevel"
      }
   )

   for i in range(0, 60*6, 60):
      for j in range(0, 60*6, 60):
         node = BasicNode(i+60, j+60, 1)
         field.addNode(node)
   
   field.simulation(600, 30, 100)
   
   print(fieldDataCollector.nodeDataCollectors[0].sessionData['randomDelay'].data)
