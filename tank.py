#!/usr/bin/env python
# -*- coding: utf-8 -*-


# tank.py
# holds a class representing a single tank in the game

import sys, pygame
import random, math
from bombglobals import *




#--------------------------------------------------------------------------------------------------------------------
class Tank():
    def __init__(self, color, Surface, Left, Top, PlayerName):
        self.__Color = color
        self.RectSize = 35
        self.Surface = Surface
        self.PosRect = pygame.Rect(Left, Top, self.RectSize, self.RectSize)
        self.CannonAngle = 90   # Range: 0 = straight left, 90 = straight up, 180 = straight right
        self.__Hitpoints = 100
        self.__ShotVelocity = 50
        self.CollideRect = self.PosRect.inflate(-10, -10)
        self.__PlayerName = PlayerName


    def getPlayerName(self):
        return self.__PlayerName

    def getColor(self):
        return self.__Color
    
    def getHitpoints(self):
        return self.__Hitpoints
    
    def modifyHitpoints(self, Amount):
        self.__Hitpoints += Amount
    
    def getShotVelocity(self):
        return self.__ShotVelocity
    
    def modifyShotVelocity(self, Amount):
        self.__ShotVelocity += Amount

    def doDamage(self, HitPosition):
        pass



    def aimLeft(self, AngleIncrement = 1):
        self.CannonAngle -= AngleIncrement
        if (self.CannonAngle < 0):
            self.CannonAngle = 180



    def aimRight(self, AngleIncrement = 1):
        self.CannonAngle += AngleIncrement
        if (self.CannonAngle > 180):
            self.CannonAngle = 0



    def getCannonAngle(self):
        return 180 - self.CannonAngle



    def draw(self):
        # these are just 2 rectangles which make up the body of the tank
        pygame.draw.rect(self.Surface, self.__Color, pygame.Rect(self.PosRect.left, self.PosRect.centery, self.PosRect.w, self.PosRect.h / 2))
        pygame.draw.rect(self.Surface, self.__Color, pygame.Rect(self.PosRect.left + 5, self.PosRect.centery - 5, self.PosRect.w - 10, 10))
        
        
        # draw cannon: startpoint = center of PosRect, endPoint = Radius * angle of cannon
        CannonLength = self.PosRect.w / 2 + 5
        self.CannonEndPoint = (self.PosRect.centerx - math.cos(math.radians(self.CannonAngle)) * CannonLength,
                            self.PosRect.centery - math.sin(math.radians(self.CannonAngle)) * CannonLength)
                            
        pygame.draw.line(self.Surface, Yellow, self.PosRect.center, self.CannonEndPoint, 2)
        
        # draw debug rectangle
        pygame.draw.rect(self.Surface, Red, self.PosRect, 1)
        pygame.draw.rect(self.Surface, Yellow, self.CollideRect, 1)


    def getBulletStartPosition(self):
        return self.CannonEndPoint
        
        
    def moveDown(self, Amount):
        try:
            if (self.PosRect.bottom >= BBGlobals.WindowHeight):
                return
                
            PixelColor = self.Surface.get_at(self.PosRect.midbottom)
            if (PixelColor.g < 128):
                self.PosRect.move_ip(0, Amount)
                self.CollideRect.center = self.PosRect.center
        except IndexError as Msg:
            print("IndexError in Tank::moveDown - self.PosRect.midbottom: {}").format(self.PosRect.midbottom)



    def getCenter(self):
        return self.PosRect.center



    def collideBullet(self, BulletPos):
        return self.PosRect.collidepoint(BulletPos)
