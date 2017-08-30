#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pygame

# bombglobals.py
# holds a 'singleton' class storing global game info
# makes the class accessible for all other modules importing this module



# standard colors
White = (255, 255, 255, 255)
Black = (0, 0, 0, 255)
BlackAsInt = 0

Red   = (255, 0, 0, 255)
Green = (0, 255, 0, 255)
Blue  = (0, 0, 255, 255)

Yellow = (255, 255, 0, 255)
Cyan   = (0, 255, 255, 255)
DarkGreen = (0, 128, 0, 255)
DarkGreenAsInt = 32768

# mousebutton defs for pygame
LEFTBUTTON      = 1
MIDDLEBUTTON    = 2
RIGHTBUTTON     = 3



PLAYERSTURN = 0
SHOTINPROGRESS = 1



#--------------------------------------------------------------------------------------------------------------------
class GameGlobals():
    def __init__(self):
        self.WindowWidth = 1024
        self.WindowHeight = 768
        self.Screen = None
        self.Tanks = []
        self.Gravity = 9.8
        self.Wind = 0
        self.Tanks = []
        self.CurrentTank = 0
        self.GameState = PLAYERSTURN


    def addTank(self, NewTank):
        self.Tanks.append(NewTank)



    def nextTankActive(self):
        self.CurrentTank += 1
        if (self.CurrentTank >= len(self.Tanks)):
            self.CurrentTank = 0






#--------------------------------------------------------------------------------------------------------------------
class Point():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def toTuple(self):
        return (self.x, self.y)





#--------------------------------------------------------------------------------------------------------------------
class Line():
    def __init__(self, StartPoint = Point(), EndPoint = Point()):
        self.StartPoint = StartPoint
        self.EndPoint = EndPoint

    def __str__(self):
        return 'Line from (%d, %d) to (%d, %d)' % (self.StartPoint.x, self.StartPoint.y, self.EndPoint.x, self.EndPoint.y)

    def getMidPoint(self):
        return Point((self.StartPoint.x + self.EndPoint.x) / 2.0, (self.StartPoint.y + self.EndPoint.y) / 2.0)









def loadSound(Name):
    class NoneSound:
        def play(self): pass
        
    if not pygame.mixer:
        return NoneSound()
        
    try:
        Sound = pygame.mixer.Sound(Name)
    except pygame.error, message:
        print ('Cannot load sound:', wav)
        raise SystemExit, message
        
    return Sound







# this is the main global 'singleton' class/game object !!
BBGlobals = GameGlobals()    
