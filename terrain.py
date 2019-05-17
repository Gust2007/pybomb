#!/usr/bin/env python
# -*- coding: utf-8 -*-


# terrain.py
# holds a class responsible for generating and maintaining the terrain

import sys, pygame
import random, math
from bombglobals import *




# terrain generation algorithm: http://www.gameprogrammer.com/fractal.html#midpoint
# (Midpoint Displacement algorithm)
MIDPOINT_DAMPING = 1.0

#--------------------------------------------------------------------------------------------------------------------
class CrumbleLineSection():
    def __init__(self, Color = Black):
        self.LowerY = 0
        self.UpperY = 0
        self.Color = Color
#        if (self.Color == Black):
#            self.Color = Blue
#        if (self.Color == DarkGreen):
#            self.Color = White





#--------------------------------------------------------------------------------------------------------------------
class CrumbleLine():
    def __init__(self, XCoord, YCoord, Surface):
        self.XCoord = XCoord
        self.YCoord = YCoord
        self.Surface = Surface
        
        self.NumGreenSections = 0
        self.NumBlackSections = 0
        self.Sections = [] # this is a list of CrumbleLineSections
        
        
        
    def generateSections(self):
        OldPixelColor = None
        NewLineSection = None
        
        for y in range(self.YCoord, 0, -1):
            try:
                PixelColor = self.Surface.get_at((self.XCoord, y))
                
                if (PixelColor != OldPixelColor):
                    #check if we have to finish an existing section
                    if (NewLineSection is not None):
                        NewLineSection.UpperY = y + 1
                        self.Sections.append(NewLineSection)
                    
                    # and start a new line section
                    NewLineSection = CrumbleLineSection(PixelColor)
                    NewLineSection.LowerY = y
                    
                    OldPixelColor = PixelColor
            except IndexError as Msg:
                pass
                # print("IndexError in Terrain::generateSections - self.XCoord: {}, y: {}").format(self.XCoord, y)

        # this is the last section going to the top of the window
        if (NewLineSection is not None):
            self.Sections.append(NewLineSection)



    def advance(self):
        # just remove green sections at the beginning of the crumbleline
        if (self.Sections and self.Sections[0].Color == DarkGreen):
            self.Sections.pop(0)

        # if we still have more than 2 sections, this must be a black one
        if (self.getNumSections() > 1):
            # reduce height of black sections by 1 px
            self.Sections[0].UpperY += 1
            
            # all other sections have to move 1 px down
            for i in range(1, len(self.Sections)):
                self.Sections[i].LowerY += 1
                self.Sections[i].UpperY += 1

        # after eventually reducing the size of a (possibly 1px sized) black section,
        # we have to check if we can also remove it
        if (self.Sections and self.Sections[0].Color == Black):
            if (self.Sections[0].LowerY < self.Sections[0].UpperY):
                self.Sections.pop(0)



    def draw(self):
        for Section in self.Sections:
            pygame.draw.line(self.Surface, Section.Color, (self.XCoord, Section.LowerY), (self.XCoord, Section.UpperY), 1)



    def getNumSections(self):
        return len(self.Sections)





#--------------------------------------------------------------------------------------------------------------------
class Terrain():
    def __init__(self, Surface, Width, Height):
        self.TerrainLines = []
        self.Surface = Surface.copy()   # this is a copy of the main screen surface
        self.Damping = MIDPOINT_DAMPING
        self.NumSplits = 8   # corresponds to 256 lines 2^8
        self.Width = Width
        self.Height = Height
        self.TopMargin = 100
        self.CrumbleRectangles = []
        self.CrumbleLines = []
        self.isCrumblingInProgress = False



    def generateCrumbleLineList(self):
        # this block is for generating crumble lines from the dirty rect(s)
  
        for DirtyRect in self.CrumbleRectangles:
            # generate crumblelines for every xcoord in a dirtyrect
            for x in range(DirtyRect.left, DirtyRect.right):
                NewCrumbleLine = CrumbleLine(x, DirtyRect.bottom, self.Surface)
                NewCrumbleLine.generateSections()
                if (NewCrumbleLine.getNumSections() >= 2):
                    self.CrumbleLines.append(NewCrumbleLine)
                    
#            pygame.draw.rect(self.Surface, Red, DirtyRect, 1)
                
                
        # empty the list of dirty rectangles
        del self.CrumbleRectangles[:]
                
        

    def drawCrumbleLines(self):
        NewCrumbleLines = []
        for CrumbleLine in self.CrumbleLines:
            CrumbleLine.advance()
            CrumbleLine.draw()
            if (CrumbleLine.getNumSections() >= 2):
                NewCrumbleLines.append(CrumbleLine)

        self.CrumbleLines = NewCrumbleLines
        if (self.CrumbleLines):
            self.isCrumblingInProgress = True
        else:
            self.isCrumblingInProgress = False


    def doCrumble(self):
        self.generateCrumbleLineList()
        self.drawCrumbleLines()




    def reset(self):
        pass



    def addCrumbleRect(self, CrumbleRect):
        self.CrumbleRectangles.append(CrumbleRect)


    def generateTerrain(self):
        self.Damping = MIDPOINT_DAMPING
        del self.TerrainLines[:]
        self.TerrainLines = [(Line(Point(0, random.randint(self.TopMargin, self.Height)), 
            Point(self.Width, random.randint(self.TopMargin, self.Height))))]
        for x in range(0, self.NumSplits):
            self.TerrainLines = self.splitLines()
        self.Surface.fill(Black)
        self.drawLines()
    


    def dumpLines(self):
        for CurrentLine in self.TerrainLines:
            print("Line: %s" % (CurrentLine))



    def splitLines(self):
        NewLines = []
        
        # splice one line after the other in 2 new lines
        for CurrentLine in self.TerrainLines:
            MidPoint = CurrentLine.getMidPoint()
            MidPoint.y += random.uniform(-1, 1) * self.Height / 2.0 * self.Damping
            
            #confine the MidPoint to minimum and maximum screen size
            MidPoint.y = max(MidPoint.y, self.TopMargin)
            MidPoint.y = min(MidPoint.y, self.Height)

            LeftLine  = Line(CurrentLine.StartPoint, Point(MidPoint.x, MidPoint.y))
            RightLine = Line(Point(MidPoint.x, MidPoint.y), CurrentLine.EndPoint)
            NewLines.append(LeftLine)
            NewLines.append(RightLine)
                
        self.Damping /= 2.0
        return NewLines



    def drawLines(self):
        for CurrentLine in self.TerrainLines:
            NewLine = Line(Point(CurrentLine.StartPoint.x, CurrentLine.StartPoint.y), 
                            Point(CurrentLine.EndPoint.x, CurrentLine.EndPoint.y))
            
            pygame.draw.line(self.Surface, DarkGreen, NewLine.StartPoint.toTuple(), NewLine.EndPoint.toTuple(), 1)
            
            # fill line from bottom to top, using the 2 point form of a line
            m = (CurrentLine.EndPoint.y - CurrentLine.StartPoint.y) / (CurrentLine.EndPoint.x - CurrentLine.StartPoint.x)
            n = CurrentLine.StartPoint.y - m * CurrentLine.StartPoint.x
            
            for x in range(int(CurrentLine.StartPoint.x), int(CurrentLine.EndPoint.x)):
                y = m * x + n
                pygame.draw.line(self.Surface, DarkGreen, (x, y), (x, self.Height), 1)



















