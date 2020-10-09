"""
EyePAINT

By Hannah Imboden and Dean Lawrence
"""

import pygame
import enum
from sklearn import linear_model

from eyelib import GazeEstimationThread


class ProgramState(enum.Enum):
    Calibration = 1
    Primary = 2
    ColorSelect = 3
    ToolSelect = 4
    Confirmation = 5

class Color(enum.Enum):
    Blue = 1
    Green = 2
    Red = 3
    Yellow = 4

class Tool():
    Line = 1
    Circle = 2

class Button():
    def __init__(self, cx, cy, width, height, color, active_width, active_height, steps=90):
        
        self.cx = cx
        self.cy = cy
        self.width = self.set_width = width
        self.height = self.set_height = height
        self.color = color

        self.active_width = active_width
        self.active_height = active_height
        
        self.step = self.set_steps = steps
    
    def reset(self):
        self.step = self.set_steps
        self.width = self.set_width
        self.height = self.set_height

    def decrement(self, ticks=1):
        self.step = max(0, self.step - ticks)

        self.width = int((self.step / self.set_steps) * self.set_width)
        self.height = int((self.step / self.set_steps) * self.set_height)

    def get_step(self):
        return self.step

    def contains(self, x, y):
        if x >= self.cx - self.active_width / 2 and  \
           x <= self.cx + self.active_width / 2 and  \
           y >= self.cy - self.active_height / 2 and \
           y <= self.cy + self.active_height / 2:
           
           self.decrement()     # If the cursor is within the active area, decrement

           if self.get_step() == 0:
               pass

        else:
            self.reset()        # If the cursor is not within the active area, reset the size of the button

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.cx - self.width / 2, self.cy - self.height / 2, self.width, self.height))

class App():
    def __init__(self, width, height):
        self._running = True
        self._screen = None
        self.size = self.width, self.height = width, height     # Hardcoded dimensions for the window

        self.state = ProgramState.Calibration       # Program begins in the calibrated state
        self.gaze_state = None

        self.active_color = Color.Blue
        self.active_tool = Tool.Line

        self.button_dict = {
            ProgramState.Calibration:   [],
            ProgramState.Primary:       [Button(400, 225, 50, 50, (248, 202, 157), 800, 450),   # Upper left color select button
                                         Button(1200, 225, 50, 50, (197, 215, 192), 800, 450),  # Upper right color select button
                                         Button(400, 675, 50, 50, (142, 201, 187), 800, 450),   # Lower left color select button
                                         Button(1200, 675, 50, 50, (251, 142, 126), 800, 450)], # Lower right color select button
            ProgramState.ColorSelect:   [Button(400, 225, 50, 50, (0, 0, 0), 800, 450),   # 
                                         Button(1200, 225, 50, 50, (0, 0, 0), 800, 450),  # 
                                         Button(400, 675, 50, 50, (0, 0, 0), 800, 450),   # 
                                         Button(1200, 675, 50, 50, (0, 0, 0), 800, 450)], # 
            ProgramState.ToolSelect:    [],
            ProgramState.Confirmation:  []
        }

        # Object that runs the gaze estimation in a separate thread
        # Deposits predictions into a queue that can be accessed through get()
        self.gaze_estimation = GazeEstimationThread(x_estimator=linear_model.Ridge(alpha=0.9),
                                                    y_estimator=linear_model.Ridge(alpha=0.9),
                                                    face_cascade_path="./classifiers/haarcascade_frontalface_default.xml",
                                                    eye_cascade_path="./classifiers/haarcascade_eye.xml",
                                                    shape_predictor_path="./classifiers/shape_predictor_68_face_landmarks.dat",
                                                    width=self.width,
                                                    height=self.height)
    
    def init(self):
        pygame.init()
        self._screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        # Hannah's Stuff
        #colorButtonsScale()
        #toolButtonsScale()
    
    def on_event(self, event):
        if event.type == pygame.QUIT:   # Kill app in case of a quit
            self._running = False
        
        if self.state == ProgramState.Calibration:
            
            # Temporary calibration routine where clicks add samples
            if event.type == pygame.MOUSEBUTTONUP:
                self.gaze_estimation.add_sample(pygame.mouse.get_pos()) 
                print("New sample added")
                
        elif self.state == ProgramState.Primary:
            pass

        elif self.state == ProgramState.ColorSelect:
            pass

        elif self.state == ProgramState.ToolSelect:
            pass

        elif self.state == ProgramState.Confirmation:
            pass
    
    def loop(self):
        if self.state == ProgramState.Calibration:
            
            # If 10 samples of data are added, train the regressors and move onto next state
            if self.gaze_estimation.get_sample_count() > 10:
                self.gaze_estimation.train()
                self.state = ProgramState.Primary

        elif self.state == ProgramState.Primary:
            
            gaze_location = self.gaze_estimation.get()
            
            if gaze_location != None:
                self.gaze_state = gaze_location

                for button in self.button_dict[self.state]:
                    button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                
        elif self.state == ProgramState.ColorSelect:
            pass

        elif self.state == ProgramState.ToolSelect:
            pass

        elif self.state == ProgramState.Confirmation:
            pass
    
    def render(self):
        self._screen.fill((255,255,255))  # Clear screen

        for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
            button.draw(self._screen)

        if self.state == ProgramState.Calibration:
            pass

        elif self.state == ProgramState.Primary:
            pass

            #if self.gaze_state != None:
            #    pygame.draw.circle(self._screen, (0,0,0), (self.gaze_state.getX(),self.gaze_state.getY()), 10)

        elif self.state == ProgramState.ColorSelect:
            pass

        elif self.state == ProgramState.ToolSelect:
            pass

        elif self.state == ProgramState.Confirmation:
            pass

        pygame.display.update()

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

            pygame.time.delay(33)
        
        self.cleanup()

if __name__ == "__main__":
    app = App(1600, 900)
    app.execute()
