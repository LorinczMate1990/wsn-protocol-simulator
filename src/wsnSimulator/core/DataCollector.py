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
    
    def addData(self, time : int, value):
        self.data[time] = value

class DataCollector(object):
    def __init__(self, source : any, dataLabelsAndPaths : dict[str, str]):
        self.source = source
        self.dataLabelsAndPaths = dataLabelsAndPaths
        self.currentSession : int = 0
        self.oldSessions : list[dict[str, CollectedData]] = []
        self.sessionData : dict[str, CollectedData] = {}

    def startNextSession(self):
        self.currentSession += 1
        self.oldSessions.append(self.sessionData)
        self.sessionData = {}

    def collectData(self, time : int):
        for label, path in self.dataLabelsAndPaths.items():
            try:
                value = eval("self.source.{}".format(path))
            except AttributeError:
                pass
            else:
                if label not in self.sessionData:
                    self.sessionData[label] = CollectedData()
                self.sessionData[label].addData(time, value)

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

    