"""
EyePAINT GUI

By Dean Lawrence
"""

import sys
import random
import pygame
from rx.subjects import Subject
from rx import Observer, Observable

from eyelib import FeatureExtraction, GazeEsimation

class CalibrationDot():
    def __init__(self):
        pass

    def render(self, surface):
        pass

class Canvas():
    def __init__(self):
        pass

    def render(self, surface):
        pass

class Button():
    def __init__(self, x, y, width, height, color):
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def render(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

class Cursor():
    def __init__(self):
        pass

    def render(self, surface):
        pass

class App():
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 400
    
    def init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
    
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    
    def loop(self):
        pass
    
    def render(self):
        pass

    def cleanup(self):
        pygame.quit()

    def execute(self):
        if self.init() == False:
            self._running = False
        
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            
            self.loop()
            self.render()
        
        self.on_cleanup()

if __name__ == "__main__":
    app = App()
    app.execute()
    