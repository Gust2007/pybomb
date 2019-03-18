#!/usr/bin/env python
# -*- coding: utf-8 -*-


# bomb clone, to remember the good old time and to really learn python
# bomb.py
import sys
import pygame
import random
import math
from bombglobals import *
from terrain import *
from tank import *
from userinterface import *


# GameTodos
# add a UI for Playernames, selecting weapons and hitpoint/Power gauge
# implement damage model and end game condition
# add automatism for having an arbitrary number of tanks (not only 2)
# add network multiplayer capability


# Known Bugs:
# crumble algorithm: whenever the terrain reaches to the top of the window,
# terrain is not crumbling correctly


# Todo: rename global variables to g_BlaBla
# Todo: each class should get its own file/module
# Todo: Line 307: very important, otherwise a user can shoot twice or more #
# and not crumbleinprogress !!
# Todo: Refactoring of advanceGame and drawGame:
#       currently mixed calls for advancing and drawing stuff (we want real MVC
#       architecture)
# Todo: use the euclid.py module in this directory
# Todo: make it run on every OS Pygame supports


# Todo: decide on Python 2 or Python 3


ANIM_INPROGRESS = 1
ANIM_FINISHED = 2


#--------------------------------------------------------------------------------------------------------------------
class Animation():

    def __init__(self, Type, Surface):
        self.Type = Type
        self.Surface = Surface
        self.Status = ANIM_INPROGRESS
        self.DirtyRect = pygame.Rect(0, 0, 0, 0)
    
    def getDirtyRect(self):
        pass




#--------------------------------------------------------------------------------------------------------------------
class ImpactExplosion(Animation):
    def __init__(self, Type, Surface, Position):
        Animation.__init__(self, Type, Surface)
        self.Position = Position
        self.AnimStep = 0
        self.AnimPhase = 0
        self.Radius = 50
        self.DirtyRect = pygame.Rect(Position[0] - self.Radius, 0, 2 * self.Radius, Position[1] + self.Radius)    # Rect height always til top of window (0)



    def draw(self):
        if (self.Status == ANIM_INPROGRESS):
            if (self.AnimPhase == 0):
                pygame.draw.circle(self.Surface, Red, self.Position, self.AnimStep)
                self.AnimStep += 1
                if (self.AnimStep == self.Radius):
                    self.AnimPhase = 1
                    self.AnimStep = 0

            if (self.AnimPhase == 1):
                pygame.draw.circle(self.Surface, Black, self.Position, self.AnimStep)
                self.AnimStep += 1
                if (self.AnimStep == self.Radius):
                    self.Status = ANIM_FINISHED



    def getDirtyRect(self):
        return self.DirtyRect





#--------------------------------------------------------------------------------------------------------------------
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
            PixelColor = self.Surface.get_at((self.XPos, self.YPos))
            if (PixelColor == DarkGreen):
                self.Collided = True
                
            # and test for bullet collision with a tank
            for Tank in BBGlobals.Tanks:
                if (Tank.collideBullet((self.XPos, self.YPos)) == True):
                    self.Collided = True
                    Tank.doDamage((self.XPos, self.YPos))
                
        except:
            print("Exception {} : {}").format(sys.exc_type, sys.exc_value)
#            print "Bullet collided with window boundaries"
            self.Collided = True













#--------------------------------------------------------------------------------------------------------------------
class PyBomb():
    def __init__(self):
        self.Bullets = []
        self.Animations = []
        self.TimeUntilNextAimOp = 0
        self.Terrain = None

        pygame.init()
        BBGlobals.Screen = pygame.display.set_mode((BBGlobals.WindowWidth, BBGlobals.WindowHeight))


        pygame.display.set_caption("PyBomb - Fun the old way !")

        self.Terrain = Terrain(BBGlobals.Screen, BBGlobals.WindowWidth, BBGlobals.WindowHeight)
        self.Terrain.generateTerrain()
        
        # create the tanks
        NewTank = Tank(Blue, BBGlobals.Screen, BBGlobals.WindowWidth / 2.0 - 200, 0, "Player1")
        BBGlobals.addTank(NewTank)
        NewTank = Tank(Cyan, BBGlobals.Screen, BBGlobals.WindowWidth / 2.0 + 200, 0, "Player2")
        BBGlobals.addTank(NewTank)
        
        BBGlobals.Screen.fill(Black)
        self.Terrain.drawLines()
        
        # init UI class
        self.UI = GameUI(BBGlobals.Screen, BBGlobals.WindowWidth, BBGlobals.WindowHeight)
        
        # init sound
        pygame.mixer.init() 
        self.ExplosionSound = loadSound("small_explosion.wav")
        self.ExplosionSound.set_volume(1.0)
        self.AimSound = loadSound("newaim.wav")
        self.AimSound.set_volume(1.0)
        
        # init fonts
        self.FPSFont = pygame.font.Font(None, 20)
        self.DebugFont = pygame.font.Font(None, 17)
        
        # init game initial values
        BBGlobals.Wind = random.uniform(-1, 1) * 10



    def blitTerrain(self):
        if (self.Terrain.SurfaceArray is not None):
            pygame.surfarray.blit_array(BBGlobals.Screen, self.Terrain.SurfaceArray)
        else:
            BBGlobals.Screen.blit(self.Terrain.Surface, (0,0))
        


    def crumbleTerrain(self):
        self.Terrain.doCrumble()



    def __drawFPS(self, CurrentFPS):
        BBGlobals.Screen.blit(self.FPSFont.render("FPS: " + str(CurrentFPS), 0, Red), (0, 0))



    def __drawDebugInfo(self):
#        BBGlobals.Screen.blit(self.DebugFont.render("#Bullets: " +
#        str(len(self.Bullets)), 0, White), (0, 20))
        BBGlobals.Screen.blit(self.DebugFont.render("Gravity: " + str(BBGlobals.Gravity), 0, White), (0, 80))
#        BBGlobals.Screen.blit(self.DebugFont.render("Velocity: " +
#        str(BBGlobals.Velocity), 0, White), (0, 40))
#        BBGlobals.Screen.blit(self.DebugFont.render("Wind: " +
#        str(BBGlobals.Wind), 0, White), (0, 90))
#        BBGlobals.Screen.blit(self.DebugFont.render("CurrentTank: " +
#        str(BBGlobals.CurrentTank), 0, White), (0, 60))
#        BBGlobals.Screen.blit(self.DebugFont.render("CurrentAngle: " +
#        str(BBGlobals.Tanks[BBGlobals.CurrentTank].getCannonAngle()), 0,
#        White), (0, 70))
#        BBGlobals.Screen.blit(self.DebugFont.render("#CrumbleLines: " +
#        str(len(self.Terrain.CrumbleLines)), 0, White), (0, 100))



    def __advanceGame(self, ElapsedTime):
        for Tank in BBGlobals.Tanks:
            Tank.moveDown(2)

        if (BBGlobals.GameState == SHOTINPROGRESS):
            if (not self.Animations and not self.Bullets and not self.Terrain.isCrumblingInProgress):
                BBGlobals.GameState = PLAYERSTURN
                BBGlobals.nextTankActive()



    def __drawGame(self, ElapsedTime):
        BBGlobals.Screen.fill(Black)
        self.crumbleTerrain()
        self.blitTerrain()
        
        # iterate over tanks to let them draw themselves
        for Tank in BBGlobals.Tanks:
            Tank.draw()

        # handle bullets
        NewBullets = []
        for Bullet in self.Bullets:
            Bullet.advance(ElapsedTime)
            if (Bullet.isCollided()):
                ImpactPos = Bullet.getPos()
                ImpactExp = ImpactExplosion(0, self.Terrain.Surface, ImpactPos)
                self.Animations.append(ImpactExp)
                self.ExplosionSound.play()
            else:
                NewBullets.append(Bullet)
                Bullet.draw()
                
        self.Bullets = NewBullets


        # handle animations
        NewAnims = []
        for Anim in self.Animations:
            Anim.draw()
            if (Anim.Status != ANIM_FINISHED):
                NewAnims.append(Anim)
            else:
                NewCrumbleRect = Anim.getDirtyRect()
                self.Terrain.addCrumbleRect(NewCrumbleRect)

        self.Animations = NewAnims
        
        # and also update the UI
        self.UI.drawUI()




    def __eventTick(self, ElapsedTime):     # ElapsedTime is in milliseconds
        keystate = pygame.key.get_pressed()
        if (self.TimeUntilNextAimOp > 0):
           self.TimeUntilNextAimOp -= ElapsedTime

        # control angle of cannon
        if (keystate[pygame.K_LEFT] and self.TimeUntilNextAimOp <= 0):
            BBGlobals.Tanks[BBGlobals.CurrentTank].aimLeft()
            self.AimSound.play()
            self.TimeUntilNextAimOp += 30   # ms
            
            
        if (keystate[pygame.K_RIGHT] and self.TimeUntilNextAimOp <= 0):
            BBGlobals.Tanks[BBGlobals.CurrentTank].aimRight()
            self.AimSound.play()
            self.TimeUntilNextAimOp += 30   # ms
            


        # control gravity setting
        if (keystate[pygame.K_g]):
            if (keystate[pygame.K_LSHIFT]):
                BBGlobals.Gravity -= 0.1
            else:
                BBGlobals.Gravity += 0.1
                
                
        # control power of bullet
        if (keystate[pygame.K_UP]):
            CurTank = BBGlobals.Tanks[BBGlobals.CurrentTank]
            CurTank.modifyShotVelocity(0.1)
                
        if (keystate[pygame.K_DOWN]):
            CurTank = BBGlobals.Tanks[BBGlobals.CurrentTank]
            CurTank.modifyShotVelocity(-0.1)
                
                
        # control wind speed
        if (keystate[pygame.K_w]):
            if (keystate[pygame.K_LSHIFT]):
                BBGlobals.Wind -= 0.1
            else:
                BBGlobals.Wind += 0.1



        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                print("pygame.QUIT event")
                sys.exit()
                
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    return False
                    
                if (event.key == pygame.K_TAB):
                    BBGlobals.nextTankActive()
              
                if (event.key == pygame.K_RETURN):
                    if (BBGlobals.GameState == PLAYERSTURN):
                        CurTank = BBGlobals.Tanks[BBGlobals.CurrentTank]
                        TankPosition = CurTank.getCenter()
                        BulletStartPosition = CurTank.getBulletStartPosition()
                        NewBullet = Bullet(BBGlobals.Screen, BulletStartPosition, CurTank.getCannonAngle(), CurTank.getShotVelocity())
                        self.Bullets.append(NewBullet)
                        BBGlobals.GameState = SHOTINPROGRESS

                    
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == LEFTBUTTON):
                    PixelColor = BBGlobals.Screen.get_at(event.pos)
                    print("Pixel: Pos: {}, Color: {}").format(event.pos, PixelColor)
                    
                if (event.button == RIGHTBUTTON):
                    self.Terrain.generateTerrain()
        
        return True



    def GameLoop(self):
        TimerClock = pygame.time.Clock()
        TimerClock.tick()
        Running = True
        
        while Running:
            Running = self.__eventTick(TimerClock.get_time())

            self.__drawGame(TimerClock.get_time())
            self.__advanceGame(TimerClock.get_time())
            
            TimerClock.tick()
            self.__drawFPS(TimerClock.get_fps())
            
            self.__drawDebugInfo()
            pygame.display.flip()






def main():
    print("This is a rewrite of bomb(Tank wars 3.0) in python and pygame.")
    PyBombGame = PyBomb()
    PyBombGame.GameLoop()
    pygame.quit()


if (__name__ == "__main__"):
    main()
