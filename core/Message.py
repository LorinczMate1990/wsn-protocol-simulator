#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

class Message:
   def __init__(self, data):
      self.__data = copy.deepcopy(data)  # The user data. Can be any type of object
      
   def getData(self):
      return copy.deepcopy(self.__data)
