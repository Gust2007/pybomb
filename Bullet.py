#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
import random
import math
from bombglobals import *


class Bullet():
    def __init__(self, Surface, StartPosition, ShotAngle, Velocity):
        self.Surface = Surface
        self.StartX = StartPosition[0]
        self.StartY = StartPosition[1]
        self.XPos = StartPosition[0]
        self.YPos = StartPosition[1]
        self.ShotAngle = math.radians(ShotAngle)
        self.Time = 0
        self.Height = 0
        self.Distance = 0
        self.Collided = False
        self.Color = White
        self.Velocity = Velocity
    
        
    def draw(self):
        if (self.Collided == True):
            self.Color = Red
        pygame.draw.circle(self.Surface, self.Color, (int(self.XPos), int(self.YPos)), 2)

    
    def isCollided(self):
        return self.Collided
    
    def getPos(self):
        return (int(self.XPos), int(self.YPos))

    def advance(self, ElapsedTime):
        self.Time += ElapsedTime / 100.0

        self.Distance = self.Velocity * math.cos(self.ShotAngle) * self.Time - (BBGlobals.Wind * math.pow(self.Time, 2)) / 2.0
        self.Height = (self.Velocity * math.sin(self.ShotAngle) * self.Time) - (BBGlobals.Gravity * math.pow(self.Time, 2)) / 2.0
            
        self.XPos = int(self.StartX + self.Distance)
        self.YPos = int(self.StartY - self.Height)
        
        try:
            # test for bullet collision of surface
            if (self.XPos < self.Surface.get_width() and self.XPos > 0 and self.YPos > 0 and self.YPos < self.Surface.get_height()):
                PixelColor = self.Surface.get_at((self.XPos, self.YPos))
                if (PixelColor == DarkGreen):
                    self.Collided = True
                
            # test if bullet is below bottom surface
            if (self.YPos > self.Surface.get_height()):
                print("Bullet is lost.")
                self.Collided = True


            # and test for bullet collision with a tank (damage calculations)
            for Tank in BBGlobals.Tanks:
                if (Tank.collideBullet((self.XPos, self.YPos)) == True):
                    self.Collided = True
                    Tank.doDamage((self.XPos, self.YPos))
                
        except:
            print(("Exception: {}").format(sys.exc_info()))
            print ("Bullet collided with window boundaries")
            self.Collided = True
