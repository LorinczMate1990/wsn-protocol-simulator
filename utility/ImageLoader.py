#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame

class ImageLoader(object):
   _instance = None
   def __new__(class_, *args, **kwargs):
      if not isinstance(class_._instance, class_):
         class_._instance = object.__new__(class_, *args, **kwargs)
      return class_._instance

   def __init__(self):
      self.images = {}

   def getImage(self, name):
      if name not in self.images:
         self.images[name]=pygame.image.load(name)
      return self.images[name]
