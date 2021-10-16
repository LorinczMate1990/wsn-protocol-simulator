#!/usr/bin/env python
# -*- coding: utf-8 -*-

def add(a : list, b : list):
   ret = list(a)
   for i in range(0, len(a)):
      ret[i] += b[i]
   return ret

def mul(vec : list, num : float):
   ret = list(vec)
   for i in range(0, len(vec)):
      ret[i] *= num
   return ret
      
def coordRound(vec : list):
   ret = list(vec)
   for i in range(0, len(vec)):
      ret[i] = int(round(ret[i]))
   return ret
      
def getWeightedMidpoint(a : list, b : list, weight : float):
   b=mul(b, weight)
   a=mul(a, 1 - weight)
   return add(a, b)
