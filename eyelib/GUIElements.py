"""
GUI Components
EyePAINT

By Hannah Imboden and Dean Lawrence
"""

import pygame
import enum
import math

# Enum for different screens that exist in the program
class ProgramState(enum.Enum):
    Calibration = 1
    Primary = 2
    ColorSelect = 3
    ToolSelect = 4
    Confirmation = 5

# Enums for types of colors
class Color(enum.Enum):
    #Color states
    Blue = 1
    Green = 2
    Red = 3
    Yellow = 4
    #GUI colors used
    Control = 5
    Text = 6
    ColorSelect = 7
    ToolSelect = 8
    Trim = 9
    Confirmation = 10

# Enum for the types of tools
class Tool(enum.Enum):
    Line = 1
    Circle = 2
    
    
def Text(cx, cy, color, fontSize, textStr, _screen):
    font = pygame.font.Font('SWSimp.ttf', fontSize)
    text = font.render(textStr, True, color)
    textRect = text.get_rect()
    textRect.center = (cx,cy)
    _screen.blit(text, textRect)    

class CalibrationDot():
    def __init__(self, cx, cy, radius, steps=55):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.step = self.set_steps = steps

        self.crad = 0

    def reset(self):
        self.step = self.set_steps
        self.crad = self.radius

    def decrement(self, ticks=1):
        self.step = max(0, self.step - ticks)
        self.crad = max(0, self.crad - ticks)

    def get_step(self):
        return self.step

    def get_x(self):
        return self.cx
    
    def get_y(self):
        return self.cy
    
    def draw(self, screen):
        pygame.draw.circle(screen, (229, 229, 229), (int(self.cx), int(self.cy)), self.crad)

        if self.crad > 5:
            pygame.draw.circle(screen, (150, 150, 150), (int(self.cx), int(self.cy)), 5)
            pygame.draw.circle(screen, (125, 125, 125), (int(self.cx), int(self.cy)), self.crad, 5)
        

# If it has an interface of contains and draw, it can probably be a button
class ColorButton():
    def __init__(self, cx, cy, width, height, color, active_width, active_height, buttonType, steps):
        
        self.cx = cx    # Center x position
        self.cy = cy    # Center y position
        self.width = self.set_width = width     # Width of drawn button
        self.height = self.set_height = height  # Height of drawn button
        self.color = color  # Color tuple

        self.active_width = active_width    # Width of active area
        self.active_height = active_height  # Height of active area
        
        self.step = self.set_steps = steps  # Total number of steps in the update

        self.buttonType = buttonType    # Tool enum thing for returning when clicked
    
    def reset(self):
        """
        Resets the steps and width and height of the button to default
        """

        self.step = self.set_steps
        self.width = self.set_width
        self.height = self.set_height

    def decrement(self, ticks=1):
        """
        Decrements the steps and width and height
        """

        self.step = max(0, self.step - ticks)

        self.width = int((self.step / self.set_steps) * self.set_width)
        self.height = int((self.step / self.set_steps) * self.set_height)

    def get_step(self):
        return self.step
    
    def get_buttonType(self):
        return self.buttonType

    def contains(self, x, y):
        """
        Handles all of the containing code. If cursor is within active area, decrement, otherwise reset
        """

        if x >= self.cx - self.active_width / 2 and  \
           x <= self.cx + self.active_width / 2 and  \
           y >= self.cy - self.active_height / 2 and \
           y <= self.cy + self.active_height / 2:
           
           self.decrement()     # If the cursor is within the active area, decrement

        else:
            self.reset()        # If the cursor is not within the active area, reset the size of the button

    def draw(self, screen):
        """
        Draw the button on the pygame canvas
        """

        pygame.draw.rect(screen, self.color, pygame.Rect(self.cx - self.width / 2, self.cy - self.height / 2, self.width, self.height))

class Canvas():
    def __init__(self, appWidth, appHeight, gridSize):
        self.cx = appWidth * (1/2)
        self.cy = appHeight * (1/2)
        
        self.appWidth = appWidth
        self.appHeight = appHeight
        
        self.gridSize = gridSize

        self.point = []
        self.buttons = []
    
    def contains(self, x, y):
        pass
    
    def reset(self):
        pass

    def get_step (self):
        pass

    def buttonGridSetup(self):
        i = 0
        while i <= (self.gridSize*self.gridSize):
            i = i + 1
            self.point.append(0)
        
    def draw(self, screen):

        pygame.draw.rect(screen, (255,255,255), pygame.Rect((self.appWidth-self.appHeight)/2, 0, self.appHeight, self.appHeight))
        
        

class CanvasButton():
    def __init__(self, cx, cy, radius, steps=20):
        
        self.cx = int(cx)    # Center x position
        self.cy = int(cy)    # Center y position
        self.set_radius = self.radius = radius
        
        self.step = self.set_steps = steps  # Total number of steps in the update

        self.color = (255, 255, 255)
    
    def reset(self):
        """
        Resets the steps and width and height of the button to default
        """
        self.step = self.set_steps
        self.radius = self.set_radius
        self.color = (255, 255, 255)

    def decrement(self, ticks=1):
        """
        Decrements the steps and width and height
        """
        self.step = max(0, self.step - ticks)
        self.radius = int((self.step / self.set_steps) * self.set_radius)
        if self.radius <= 4:
            self.radius = 4

    def get_step(self):
        return int(self.step)
    
    def get_xy(self):
        xy =[self.cx,self.cy]
        return xy

    def contains(self, x, y):
        """
        Handles all of the containing code. If cursor is within active area, decrement, otherwise reset
        """
        if x >= self.cx - self.set_radius and  \
           x <= self.cx + self.set_radius and  \
           y >= self.cy - self.set_radius and \
           y <= self.cy + self.set_radius :
           
           self.decrement()     # If the cursor is within the active area, decrement
           self.color = (229, 229, 229)

        else:
            self.reset()        # If the cursor is not within the active area, reset the size of the button

    def draw(self, screen):
        """
        Draw the button on the pygame canvas
        """

        pygame.draw.circle(screen, self.color, (self.cx, self.cy), self.radius, 2)
        pygame.draw.circle(screen, (229,229,229), (self.cx, self.cy), 4)

class BrushStroke ():
    def __init__(self, tool, color, x1, y1, x2, y2, width = 5):
        
        self.tool = tool
        self.color = color
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.width = width
        self.distance = math.sqrt(abs(self.y2-self.y1)**2 + abs(self.x2-self.x1)**2)
        
        #copy from App
        self.color_dict = {
            Color.Blue:         (248, 202, 157),
            Color.Green:        (197, 215, 192),
            Color.Red:          (142, 201, 187),
            Color.Yellow:       (251, 142, 126),
            Color.Control:      (229, 229, 229),
            Color.Text:         (125, 125, 125),
            Color.ColorSelect:  (235, 189, 191),
            Color.ToolSelect:   (143, 188, 145),
            Color.Trim:         (229, 229, 229),
            Color.Confirmation: (247, 249, 249)
        }
    
    def getPointOne(self):
        return (self.x1, self.y1)

    def getPointTwo(self):
        return (self.x2, self.y2)
            
    def draw(self, screen):
        if self.tool == Tool.Line:
            pygame.draw.line(screen, self.color_dict[self.color], (self.x1, self.y1), (self.x2, self.y2), self.width)
        else:
            pygame.draw.circle(screen, self.color_dict[self.color], (self.x1, self.y1), int(self.distance), self.width)
