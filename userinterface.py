#!/usr/bin/env python
# -*- coding: utf-8 -*-


# userinterface.py
# holds a class responsible for drawing the user interface of pybomb

import sys, pygame
import random, math
from bombglobals import *




#--------------------------------------------------------------------------------------------------------------------
class GameUI():
    def __init__(self, Surface, Width, Height):
        self.Surface = Surface
        self.Width = Width
        self.Height = Height
        self.MainFont = pygame.font.Font(None, 30)
        

    def drawUI(self):
        CurrentTank = BBGlobals.Tanks[BBGlobals.CurrentTank]
        
        # Angle of Cannon
        self.Surface.blit(self.MainFont.render("Angle: " + str(CurrentTank.getCannonAngle()), 0, CurrentTank.getColor()), (10, 10))
        
        # Power of Tank (Shot Velocity)
        self.Surface.blit(self.MainFont.render("Power: " + str(CurrentTank.getShotVelocity()), 0, CurrentTank.getColor()), (10, 40))
        
        # PlayerName
        self.Surface.blit(self.MainFont.render(str(CurrentTank.getPlayerName()), 0, CurrentTank.getColor()), (self.Width / 2, 10))

        # Wind
        self.Surface.blit(self.MainFont.render("Wind: " + str(BBGlobals.Wind), 0, CurrentTank.getColor()), (self.Width / 2, 40))

        # Hitpoints of Player
        self.Surface.blit(self.MainFont.render("Men: " + str(CurrentTank.getHitpoints()), 0, CurrentTank.getColor()), (self.Width - 150, 10))
