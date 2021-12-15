#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import *
from types import MethodType
from wsnSimulator.core.NodeSkeleton import *
from wsnSimulator.core.Field import *

class CollectedData(object):
   def __init__(self):
      self.data : dict[int, Any] = {}
      self.lastLastTime = None
      self.lastTime = None
   
   def addData(self, time : int, value):
      self.data[time] = value
      self.lastTime, self.lastLastTime, lllTime = time, self.lastTime, self.lastLastTime
      
      if self.lastTime == None or self.lastLastTime == None:
         return

      if self.data[time] == self.data[self.lastTime] == self.data[self.lastLastTime]:
         del self.data[self.lastTime]
         self.lastTime, self.lastLastTime = self.lastLastTime, lllTime

   def getLast(self):
      return self.data[self.lastTime]

   def getHistogram(self):
      hist = {} 
      for i in self.data.values(): 
         hist[i] = hist.get(i, 0) + 1 
      return hist

class DataCollector(object):
   def __init__(self, source : any, dataLabelsAndPaths : dict[str, str]):
      self.source = source
      self.dataLabelsAndPaths = dataLabelsAndPaths
      self.currentSession : int = 0
      self.oldSessions : list[dict[str, CollectedData]] = []
      self.sessionData : dict[str, CollectedData] = {}
      self.triggerValues : dict[str, Any] = {}

   def startNextSession(self):
      self.currentSession += 1
      self.oldSessions.append(self.sessionData)
      self.sessionData = {}

   def getSourceValue(self, path):
      return eval("self.source.{}".format(path))

   def collectData(self, time : int):
      for label, dataSource in self.dataLabelsAndPaths.items():
         try:
            logData = False
            if type(dataSource) == type(dict()):
               if dataSource['type'] == "trigger":
                  path = dataSource['path']
                  trigger = dataSource['trigger']
                  triggerValue = self.getSourceValue(trigger)
                  if path not in self.triggerValues:
                     self.triggerValues[path] = triggerValue
                  logData = self.triggerValues[path] != triggerValue
                  self.triggerValues[path] = triggerValue
            elif type(dataSource) == type(""):
               path = dataSource
               logData = True
            if logData:
               value = self.getSourceValue(path)
               if label not in self.sessionData:
                  self.sessionData[label] = CollectedData()
               self.sessionData[label].addData(time, value)
         except AttributeError:
            pass

class NodeDataCollector(DataCollector):
   def __init__(self, node : NodeSkeleton, dataLabelsAndPaths : dict[str, str]):
      super().__init__(node, dataLabelsAndPaths)
      self.node = node

class FieldDataCollector(DataCollector):
   def __init__(self, field, dataLabelsAndPathsForNodes : dict[str, str]):
      super().__init__(field, {})
      self.dataLabelsAndPathsForNodes = dataLabelsAndPathsForNodes
      self.currentSession : int = 0
      self.nodeDataCollectors : list[NodeDataCollector] = []
      self.__monitorField(field)

   def __monitorField(self, field : Field):
      self.monitoredField = field
      field.originalAddNode = field.addNode 
      field.originalTick = field.tick
      
      dataCollector = self
      def injectedAddNodeaddNode(self : Field, node : NodeSkeleton) -> None:
         nodeDataCollector = NodeDataCollector(node, dataCollector.dataLabelsAndPathsForNodes)
         dataCollector.nodeDataCollectors.append(nodeDataCollector)
         self.originalAddNode(node)
      def injectedTick(self : Field):
         self.originalTick()
         dataCollector.tick()

      field.addNode = MethodType(injectedAddNodeaddNode, field)
      field.tick = MethodType(injectedTick, field)

   def tick(self):
      time = self.monitoredField.localTime
      self.collectData(time)
      for nodeDataCollector in self.nodeDataCollectors:
         nodeDataCollector.collectData(time)

   