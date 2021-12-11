#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
   from wsnSimulator.core.NodeSkeleton import NodeSkeleton

import sys

import bisect
import pygame
from wsnSimulator.core.Message import *
from wsnSimulator.core.NodeHelpers import *
from wsnSimulator.core.Reporting import *
import wsnSimulator.utility.vector as vector

class MessageEvent:
   def __init__(self, fireTime : int, message : Message, channel : int, recipients : list[ReachableDescriptor], source : NodeSkeleton):
      self.source = source     # the source of the message 
      self.fireTime = fireTime # The round's number when this object will be destroyed
      self.message = message   # the sended message object
      self.recipients = recipients
      self.channel = channel   # The used channel
      self.success : set[int, bool] ={}
      for descriptor in recipients:
         descriptor.to._beginChannelUse(channel)
         self.success[descriptor.to.ID] = descriptor.success()
      source._RXMode=True

   def fire(self) -> None:
      for reachableDesc in self.recipients:
         reachableNode = reachableDesc.to
         if reachableNode._endChannelUse(self.channel) and self.success[reachableNode.ID]:
            reachableDesc.to.messageEvent(self.message.getData())
      self.source._RXMode=False
      self.source._endChannelUse(self.channel)
   
   # I have to sort them reverse
   def __lt__(self, o : MessageEvent) -> bool: return self.fireTime > o.fireTime 
   def __le__(self, o : MessageEvent) -> bool: return self.fireTime >= o.fireTime
   def __eq__(self, o : MessageEvent) -> bool: return self.fireTime == o.fireTime
   def __ne__(self, o : MessageEvent) -> bool: return self.fireTime != o.fireTime
   def __gt__(self, o : MessageEvent) -> bool: return self.fireTime < o.fireTime
   def __ge__(self, o : MessageEvent) -> bool: return self.fireTime <= o.fireTime

class GraphMessageEvent(MessageEvent):
   def __init__(self, fireTime : int, message, channel : int, recipients : list[ReachableDescriptor], source : NodeSkeleton, ttl : float):
      MessageEvent.__init__(self,fireTime, message, channel, recipients, source)
      self.originalTtl = ttl
      self.ttl = ttl

   def decraseTtl(self, by : float) -> None:
      self.ttl-=by
   
   def _draw(self, screen : pygame.Surface) -> None:
      ratio = 1.0*self.ttl/self.originalTtl
      for recDesc in self.recipients:
         rec = recDesc.to
         progressVector = vector.getWeightedMidpoint((rec.x, rec.y), (self.source.x,self.source.y), ratio)
         progressVector = vector.coordRound(progressVector)
         pygame.draw.line(screen, (255,255,255), (self.source.x,self.source.y), (rec.x, rec.y), 2)
         if self.success[rec.ID]:
            pygame.draw.circle(screen, (255,255,0), progressVector, 4)

class Field:
   def __init__(self, connectionCheckFunction : Callable[[NodeSkeleton, NodeSkeleton], float]):
      self.connectionCheckFunction = connectionCheckFunction 
      self.nodeList : list[NodeSkeleton] = []
      self.eventList : list[MessageEvent] = []
      self.localTime : int = 0
      self.firstTick = True

   def reset(self) -> None:
      self.eventList : list[MessageEvent] = []
      self.localTime : int = 0
      self.firstTick = True
   
   def __addNewNodeToConnectionList(self, node : NodeSkeleton) -> None:
      for oldNode in self.nodeList:
         if node == oldNode: continue
         propabilityTo = self.connectionCheckFunction(oldNode, node)
         propabilityFrom = self.connectionCheckFunction(node, oldNode)
         if propabilityTo > 0:
            oldNode.reachables.append(ReachableDescriptor(node, propabilityTo))
         if propabilityFrom > 0:
            node.reachables.append(ReachableDescriptor(oldNode, propabilityFrom))

   def __validateConnectionLists(self) -> None:
      for node in self.nodeList:
         node.reachables = []
         
      for nodeA in self.nodeList:
         for nodeB in self.nodeList:
            if nodeA == nodeB: continue
            if self.connectionCheckFunction(nodeA, nodeB):
               nodeA.reachables.push_back(nodeB)
   
   def addNode(self, node : NodeSkeleton) -> None:
      self.__addNewNodeToConnectionList(node)
      node._setFieldReference(self)
      self.nodeList.append(node)
   
   def periodicEvent(self) -> None:
      for node in self.nodeList:
         node._periodicEvent()

   def deliverMessages(self) -> None:
      while len(self.eventList)>0 and self.eventList[-1].fireTime <= self.localTime:
         msgEvent = self.eventList.pop()
         msgEvent.fire()
   
   def sendMessage(self, reachables : list[ReachableDescriptor], messageData, duration : int, channel : int, source : NodeSkeleton):
      event = MessageEvent(self.localTime+duration, Message(messageData), channel, reachables, source)
      bisect.insort(self.eventList, event)
   
   def tick(self):
      if self.firstTick:
         self.firstTick = False
         for node in self.nodeList:
            node.init()
      self.__laterTicks()
   
   def __laterTicks(self):
      # If you use non-graphic simulation, you only have to call this function from your main script
      # In every discrete time unit, I have to...
      # ...deliver the messages
      print("self.localTime: ", self.localTime)
      self.deliverMessages()
      
      # ...call the nodes' periodic event
      self.periodicEvent() 
      
      self.localTime += 1
         
class GraphFieldHandler(Field):
   def __init__(self, connectionCheckFunction : Callable[[NodeSkeleton, NodeSkeleton]], width : int, height : int):
      Field.__init__(self, connectionCheckFunction)
      pygame.init()
      self.done = False
      self.paused = False
      self.screen : pygame.Surface = pygame.display.set_mode((width, height))
   
   def __eventHandler(self, events):
      for event in events:
         if event.type == pygame.QUIT:
            self.done = True
         elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.paused = not self.paused
            
   def __displayNodes(self):
      for node in self.nodeList:
         node._draw(self.screen)
         
   def __displayEvents(self):
      for event in self.eventList:
         event._draw(self.screen)
         
   def __decraseMessageEventTtlBy(self, by : float):
      # ...decrease the message event's TTL
      for msgEvent in self.eventList:
         assert issubclass(type(msgEvent), GraphMessageEvent)
         msgEvent : GraphMessageEvent = msgEvent
         msgEvent.decraseTtl(by)

   def sendMessage(self, reachables : list[ReachableDescriptor], msgData, duration : int, channel : int, source : NodeSkeleton):
      event = GraphMessageEvent(self.localTime+duration, Message(msgData), channel, reachables, source, duration)
      bisect.insort(self.eventList, event)
         
   def simulation(self, iterationNumber : int, frameRate : int, iterationRate : int):
      clock = pygame.time.Clock()
      tickCounter=0
      frameIterationRatio = 1.0*frameRate/iterationRate
      # This cycle will run frameRate times in every sec (because clock.tick(frameRate)),
      #   but I only want to run the tick() iterationRate times in every sec 
      # I have to run the cycle iterationNumber/iterationRate*frameRate
      #   because the cycle run frameRate times in every secound and the 
      #   simulation must run during iterationNumber/iterationRate secounds
      # The tick must be called in every frameRate/iterationRate-th cycle
      #   this can be a fraction, that's why I need the tickCounter variable
      #   tickCounter increases by frameRate/iterationRate if tick() performs.
      #   tick() performs only if i >= tickCounter
      # If frameRate/iterationRate < 1, then tick() must be performed more than once
      #   in each cycle.
      upperBound = iterationNumber*frameIterationRatio
      cycleCounter = 0
      while cycleCounter<upperBound and not self.done:
         if not self.paused:
            cycleCounter+=1
            while cycleCounter>=tickCounter:
               tickCounter+=frameIterationRatio
               self.tick()
            self.__decraseMessageEventTtlBy(1./frameIterationRatio)
            
         self.screen.fill((0, 0, 0))
         self.__eventHandler(pygame.event.get())
         self.__displayEvents()
         self.__displayNodes()
         pygame.display.flip()
         clock.tick(frameRate)