#!/usr/bin/env python
# -*- coding: utf-8 -*-

def add(a,b):
   ret = list(a)
   for i in range(0,len(a)):
      ret[i]+=b[i]
   return ret

def mul(vec, num):
   ret = list(vec)
   for i in range(0,len(vec)):
      ret[i]*=num
   return ret
      
def coordRound(vec):
   ret = list(vec)
   for i in range(0,len(vec)):
      ret[i]=int(round(ret[i]))
   return ret
      
def getWeightedMidpoint(a, b, weight):
   b=mul(b,weight)
   a=mul(a,1-weight)
   return add(a,b)
