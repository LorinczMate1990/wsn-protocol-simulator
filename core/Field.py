#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, 'utility')
import bisect
import pygame
from Message import *
from NodeSkeleton import *
from Reporting import *
import utility.vector as vector

class MessageEvent:
   def __init__(self, fireTime, message, channel, recipients, source):
      self.source = source     # the source of the message 
      self.fireTime = fireTime # The round's number when this object will be destroyed
      self.message = message   # the sended message object
      self.recipients = recipients
      self.channel = channel   # The used channel
      self.success={}
      for descriptor in recipients:
         descriptor.to._beginChannelUse(channel)
         self.success[descriptor.to.ID] = descriptor.success()
      source._RXMode=True
      
   def fire(self):
      for reachableDesc in self.recipients:
         reachableNode = reachableDesc.to
         if reachableNode._endChannelUse(self.channel) and self.success[reachableNode.ID]:
            reachableDesc.to.messageEvent(self.message.getData())
      self.source._RXMode=False
      self.source._endChannelUse(self.channel)
   
   # I have to sort them reverse
   def __lt__(self,o): return self.fireTime > o.fireTime 
   def __le__(self,o): return self.fireTime >= o.fireTime
   def __eq__(self,o): return self.fireTime == o.fireTime
   def __ne__(self,o): return self.fireTime != o.fireTime
   def __gt__(self,o): return self.fireTime < o.fireTime
   def __ge__(self,o): return self.fireTime <= o.fireTime

class GraphMessageEvent(MessageEvent):
   def __init__(self, fireTime, message, channel, recipients, source, ttl):
      MessageEvent.__init__(self,fireTime, message, channel, recipients, source)
      self.originalTtl = ttl
      self.ttl = ttl

   def decraseTtl(self, by):
      self.ttl-=by
   
   def _draw(self, screen):
      ratio = 1.0*self.ttl/self.originalTtl
      for recDesc in self.recipients:
         rec = recDesc.to
         progressVector = vector.getWeightedMidpoint((rec.x, rec.y), (self.source.x,self.source.y), ratio)
         progressVector = vector.coordRound(progressVector)
         pygame.draw.line(screen, (255,255,255), (self.source.x,self.source.y), (rec.x, rec.y), 2)
         if self.success[rec.ID]:
            pygame.draw.circle(screen, (255,255,0), progressVector, 4)   
   

class Field:
   def __init__(self, connectionCheckFunction):
      self.connectionCheckFunction = connectionCheckFunction 
      self.nodeList=[]
      self.eventList=[]
      self.localTime=0
   
   def __addNewNodeToConnectionList(self, node):
      for oldNode in self.nodeList:
         if node == oldNode: continue
         propabilityTo = self.connectionCheckFunction(oldNode, node)
         propabilityFrom = self.connectionCheckFunction(node, oldNode)
         if propabilityTo > 0:
            oldNode.reachables.append(ReachableDescriptor(node, propabilityTo))
         if propabilityFrom > 0:
            node.reachables.append(ReachableDescriptor(oldNode, propabilityFrom))

   def __validateConnectionLists(self):
      for node in self.nodeList:
         node.reachables = []
         
      for nodeA in self.nodeList:
         for nodeB in self.nodeList:
            if nodeA == nodeB: continue
            if self.connectionCheckFunction(nodeA, nodeB):
               nodeA.reachables.push_back(nodeB)
   
   def addNode(self, node):
      self.__addNewNodeToConnectionList(node)
      node._setFieldReference(self)
      self.nodeList.append(node)
   
   def periodicEvent(self):
      for node in self.nodeList:
         node._periodicEvent()

   def deliverMessages(self):
      while len(self.eventList)>0 and self.eventList[-1].fireTime <= self.localTime:
         msgEvent = self.eventList.pop()
         msgEvent.fire()
   
   def sendMessage(self, reachable, msgData, duration, channel, source):
      event = MessageEvent(self.localTime+duration, Message(msgData), channel, reachable, source)
      bisect.insort(self.eventList, event)
   
   def tick(self):
      for node in self.nodeList:
         node.init()
      self.__laterTicks()
      self.tick = self.__laterTicks # I have to call the init only on first tick, but later,
                                    # I have to call only __laterTicks.
   
   def __laterTicks(self):
      # If you use non-graphic simulation, you only have to call this function from your main script
      # In every discrete time unit, I have to...
      # ...deliver the messages
      print "self.localTime: ", self.localTime
      self.deliverMessages()
      
      # ...call the nodes' periodic event
      self.periodicEvent() 
      
      self.localTime += 1
         
class GraphFieldHandler(Field):
   def __init__(self, connectionCheckFunction, width, height):
      Field.__init__(self, connectionCheckFunction)
      pygame.init()
      self.done = False
      self.paused = False
      self.screen=screen = pygame.display.set_mode((width, height))
   
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
         
   def __decraseMessageEventTtlBy(self, by):
      # ...decrease the message event's TTL
      for msgEvent in self.eventList:
         msgEvent.decraseTtl(by)

   def sendMessage(self, reachable, msgData, duration, channel, source):
      event = GraphMessageEvent(self.localTime+duration, Message(msgData), channel, reachable, source, duration)
      bisect.insort(self.eventList, event)
         
   def simulation(self, iterationNumber, frameRate, iterationRate):
      clock = pygame.time.Clock()
      tickCounter=0
      frameIterationRatio = 1.0*frameRate/iterationRate;
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
