#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame

class ImageLoader:
   _instance = None
   def __new__(cls, *args, **kwargs):
      if not cls._instance:
         cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
      return cls._instance

   def __init__(self):
      self.images = {}

   def getImage(self, name):
      if not self.images.has_key(name):
         self.images[name]=pygame.image.load(name)
      return self.images[name]
