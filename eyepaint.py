"""
EyePAINT

By Hannah Imboden and Dean Lawrence
"""

import pygame
import enum
import math
import argparse
from sklearn import linear_model

from eyelib import GazeEstimationThread, GazeState
from eyelib import GcodeGeneration
from eyelib import ProgramState, Color, Tool, Control, Text, ColorButton, Canvas, CanvasButton, BrushStroke, CalibrationDot


class MockGazeEstimationThread():
    def get(self):
        pos = pygame.mouse.get_pos()

        return GazeState(pos[0], pos[1])
    
    def add_sample(self, pos):
        pass

    def train(self):
        pass

class MockGcodeGeneration():
    def initialize(self):
        pass

    def generate(self, point1, point2, color, tool):
        pygame.time.delay(4000)

class App():
    def __init__(self, width, height, canvas_divisions=10, calibration_dots=4, port="COM3"):
        self._running = True
        self._screen = None
        self.size = self.width, self.height = width, height     # Hardcoded dimensions for the window
        
        #self.mouseXY
        
        self.canvas_divisions = canvas_divisions

        #self.state = ProgramState.Calibration       # Program begins in the calibrated state
        #self.state = ProgramState.ControlSelect
        self.state = ProgramState.Calibration
        self.gaze_state = None

        self.active_color = Color.Blue  # Store an active color
        self.active_tool = Tool.Line    # Store an active tool
        self.active_control = Control.Mouse
        
        self.gridSize = canvas_divisions
        self.radius = int((self.height/self.gridSize)/2)
        tempHeight = int(self.height)
        tempWidth = int(self.width)
        self.canvasButtons = [CanvasButton(((tempWidth-tempHeight)/2) + self.radius + ((i//self.gridSize)*self.radius*2), self.radius + ((i%self.gridSize)*self.radius*2), self.radius) for i in range(0,self.gridSize*self.gridSize)]

        self.pointOne = (0, 0)
        self.pointTwo = (0, 0)
        self.distance = 0
        self.commitStroke = 0
        self.brushStrokeTemp = [0]
        self.brushStroke_dict = []
        self.count = 0


        # Dictionary to store color tuples for consistency between things later
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

        self.calibration_dots = calibration_dots
        calibration_width = self.width * (1 / self.calibration_dots)
        calibration_height = self.height * (1 / self.calibration_dots)

        # Lists of buttons that are separated by program state
        self.button_dict = {
            ProgramState.Calibration:   [CalibrationDot((calibration_width / 2) + calibration_width * (i % self.calibration_dots),
                                                        (calibration_height / 2) + calibration_height * (i // self.calibration_dots),
                                                        65) for i in range(calibration_dots * calibration_dots)],
            ProgramState.Primary:       [ColorButton(self.width * (1/8)-50, self.height * (1/2), self.width * (2/8)-100, self.height, self.color_dict[Color.ColorSelect], self.width * (2/8)-100, self.height, ProgramState.ColorSelect, 20),
                                         ColorButton(self.width * (7/8)+50, self.height * (1/2), self.width * (2/8)-100, self.height, self.color_dict[Color.ToolSelect], self.width * (2/8)-100, self.height, ProgramState.ToolSelect, 20),],
            
            ProgramState.ColorSelect:   [ColorButton(self.width * (1/4), self.height * (1/4), 100, 100, self.color_dict[Color.Blue], self.width / 2, self.height / 2, Color.Blue, 50),     # Upper left color select button
                                         ColorButton(self.width * (3/4), self.height * (1/4), 100, 100, self.color_dict[Color.Green], self.width / 2, self.height / 2, Color.Green, 50),   # Upper right color select button
                                         ColorButton(self.width * (1/4), self.height * (3/4), 100, 100, self.color_dict[Color.Red], self.width / 2, self.height / 2, Color.Red, 50),      # Lower left color select button
                                         ColorButton(self.width * (3/4), self.height * (3/4), 100, 100, self.color_dict[Color.Yellow], self.width / 2, self.height / 2, Color.Yellow, 50)], # Lower right color select button

            ProgramState.ToolSelect:    [ColorButton(self.width * (1/4), self.height * (1/2), 200, 200, self.color_dict[Color.Control], self.width / 2, self.height, Tool.Line, 20),
                                         ColorButton(self.width * (3/4), self.height * (1/2), 200, 200, self.color_dict[Color.Control], self.width / 2, self.height, Tool.Circle, 20)],

            ProgramState.Confirmation:  [ColorButton(self.width * (1/8), self.height * (1/2), 200, 200, self.color_dict[Color.Trim], self.width / 2, self.height, 0, 10),
                                         ColorButton(self.width * (7/8), self.height * (1/2), 200, 200, self.color_dict[Color.Trim], self.width / 2, self.height, 1, 10)]

        }

        self.active_calibration_dot = -1
    
        # Object that runs the gaze estimation in a separate thread
        # Deposits predictions into a queue that can be accessed through get()
        
        self.gaze_estimation = GazeEstimationThread(x_estimator=linear_model.Ridge(alpha=0.9),
                                                    y_estimator=linear_model.Ridge(alpha=0.9),
                                                    face_cascade_path="./classifiers/haarcascade_frontalface_default.xml",
                                                    eye_cascade_path="./classifiers/haarcascade_eye.xml",
                                                    shape_predictor_path="./classifiers/shape_predictor_68_face_landmarks.dat",
                                                    width=self.width,
                                                    height=self.height)
        

        #self.gcode_generation = GcodeGeneration("COM3", 250000)
        self.gcode_generation = MockGcodeGeneration()
        #self.gaze_estimation = MockGazeEstimationThread()
    
    def init(self):
        pygame.init()   # Init pygame stuff
        self._screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)  # Create the screen for drawing
        self._running = True    # Set running to true
        pygame.display.set_caption("EyePAINT")  # Set the title of the program to EyePAINT
    
    def on_event(self, event):
        if event.type == pygame.QUIT:   # Kill app in case of a quit
            self._running = False
            
        # C A L I B R A T I O N   E V E N T
        if self.state == ProgramState.Calibration:
            pass
                
        # P R I M A R Y   E V E N T        
        elif self.state == ProgramState.Primary:
            pass    # Do event handling for the primary canvas screen
        
        # C O L O R   S E L E C T   E V E N T 
        elif self.state == ProgramState.ColorSelect:
            pass    # Do event handling for the color select screen
        
        # T O O L   S E L E C T   E V E N T
        elif self.state == ProgramState.ToolSelect:
            pass    # Do event handling for the tool select screen

        # C O M F I R M A T I O N   E V E N T
        elif self.state == ProgramState.Confirmation:
            pass    # Do event handling for the confirmation screen
    
    def loop(self):
        gaze_location = self.gaze_estimation.get()  # Get the current gaze estimation position from the queue

        if gaze_location != None:   # If there was a location, update the classes known location
            self.gaze_state = gaze_location
        
        if self.gaze_state == None and self.state != ProgramState.Calibration:
            return
        
        # C A L I B R A T I O N   L O O P
        if self.state == ProgramState.Calibration:
            
            if self.active_calibration_dot == -1:
                pygame.time.delay(4000)
                self.active_calibration_dot += 1
            
            dot = self.button_dict[self.state][self.active_calibration_dot]

            if dot.get_step() == dot.set_steps:
                dot.reset()
            
            dot.decrement()

            if dot.get_step() == 0:
                dot.crad = 0
                self.gaze_estimation.add_sample((dot.get_x(), dot.get_y()))
                self.active_calibration_dot += 1

            if self.active_calibration_dot == self.calibration_dots * self.calibration_dots:
                self.gaze_estimation.train()        # Train the regressors that perform gaze estimation
                self.gcode_generation.initialize()  # Send the initialization string for the CNC
                self.state = ProgramState.Primary   # Switch to the primary screen

            """
            # If 10 samples of data are added, train the regressors and move onto next state
            if self.gaze_estimation.get_sample_count() > 10:
                self.gaze_estimation.train()
                self.state = ProgramState.Primary
            """

        # P R I M A R Y   L O O P
        elif self.state == ProgramState.Primary:
            for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                if button.get_step() == 0:
                    self.state = button.get_buttonType()
                    button.reset()

            for i in range (0, self.gridSize*self.gridSize):
                self.canvasButtons[i].contains(self.gaze_state.getX(), self.gaze_state.getY())
                if self.canvasButtons[i].get_step() <= 5:
                    if self.pointOne == (0,0):
                        self.pointOne = self.canvasButtons[i].get_xy()
                    else:
                        self.pointTwo = self.canvasButtons[i].get_xy()
                if self.pointOne != self.pointTwo != (0,0):
                    self.state = ProgramState.Confirmation
                    self.brushStrokeTemp = BrushStroke(self.active_tool, self.active_color, self.pointOne[0], self.pointOne[1], self.pointTwo[0], self.pointTwo[1])
                
        # C O L O R   S E L E C T   L O O P 
        elif self.state == ProgramState.ColorSelect:
            for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                if button.get_step() == 0:
                    self.active_color = button.get_buttonType()
                    self.state = ProgramState.Primary
                    button.reset()


        # T O O L   S E L E C T   L O O P
        elif self.state == ProgramState.ToolSelect:
            for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                if button.get_step() == 0:
                    self.active_tool = button.get_buttonType()
                    self.state = ProgramState.Primary
                    button.reset()
                            
        # C O N F I R M A T I O N   L O O P
        elif self.state == ProgramState.Confirmation:
            for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                if button.get_step() == 0:
                    self.CommitStroke = button.get_buttonType()
                    if self.CommitStroke == 1:
                        #Add current brush stroke to commited brush stroke list
                        self.brushStroke_dict.append(self.brushStrokeTemp)
                        self.count = self.count + 1

                        x1, y1 = self.brushStrokeTemp.getPointOne()
                        x2, y2 = self.brushStrokeTemp.getPointTwo()

                        x1 /= self.height
                        y1 /= self.height
                        x2 /= self.height
                        y2 /= self.height

                        self.gcode_generation.generate((x1, y1), (x2, y2), self.active_tool, self.active_color)     # Generate and send g-code string to CNC
                        
                    #Reset the canvas for next brush stroke and move back to primary
                    self.pointOne = (0, 0)
                    self.pointTwo = (0, 0)
                    self.CommitStroke = 0
                    self.state = ProgramState.Primary

                    button.reset()
    
    def render(self):
        self._screen.fill((255,255,255))  # Clear screen

        # C A L I B R A T I O N   R E N D E R
        if self.state == ProgramState.Calibration:
            
            for button in self.button_dict[self.state]:
                button.draw(self._screen)

        # P R I M A R Y   R E N D E R
        elif self.state == ProgramState.Primary:
            self._screen.fill(self.color_dict[Color.Trim])
            pygame.draw.rect(self._screen, (255,255,255), pygame.Rect((self.width-self.height)/2, 0, self.height, self.height))
            for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
                button.draw(self._screen)
            
            Text(self.width * (1/8)-50, (self.height * (1/2))-16, self.color_dict[Color.Text], 32, 'Color', self._screen)
            Text(self.width * (1/8)-50, (self.height * (1/2))+16, self.color_dict[Color.Text], 32, 'Select', self._screen)
            Text(self.width * (7/8)+50, (self.height * (1/2))-16, self.color_dict[Color.Text], 32, 'Tool', self._screen)
            Text(self.width * (7/8)+50, (self.height * (1/2))+16, self.color_dict[Color.Text], 32, 'Select', self._screen)
            #Canvas stuff
            for i in range (0, self.gridSize*self.gridSize):
                self.canvasButtons[i].draw(self._screen)
                
            if self.pointOne != self.pointTwo != (0,0):
                self.brushStrokeTemp.draw(self._screen)
            
            for i in range (0, self.count):
                self.brushStroke_dict[i].draw(self._screen)

        # C O L O R   S E L E C T   R E N D E R
        elif self.state == ProgramState.ColorSelect:
            for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
                button.draw(self._screen)

        # T O O L   S E L E C T   R E N D E R
        elif self.state == ProgramState.ToolSelect:
            for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
                button.draw(self._screen)
            Text(self.width * (1/4), (self.height * (1/2))+225, self.color_dict[Color.Text], 32, 'Line', self._screen)
            Text(self.width * (3/4), (self.height * (1/2))+225, self.color_dict[Color.Text], 32, 'Circle', self._screen)


        # C O N F I R M A T I O N   R E N D E R
        elif self.state == ProgramState.Confirmation:
            #COPY OF PRIMARY RENDER ---------------------------------------------------------
            self._screen.fill(self.color_dict[Color.Trim])
            pygame.draw.rect(self._screen, (255,255,255), pygame.Rect((self.width-self.height)/2, 0, self.height, self.height))
            for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
                button.draw(self._screen)
            
            Text(self.width * (1/8)-50, (self.height * (1/2))-16, self.color_dict[Color.Text], 32, 'Color', self._screen)
            Text(self.width * (1/8)-50, (self.height * (1/2))+16, self.color_dict[Color.Text], 32, 'Select', self._screen)
            Text(self.width * (7/8)+50, (self.height * (1/2))-16, self.color_dict[Color.Text], 32, 'Tool', self._screen)
            Text(self.width * (7/8)+50, (self.height * (1/2))+16, self.color_dict[Color.Text], 32, 'Select', self._screen)
            #Canvas stuff
            for i in range (0, self.gridSize*self.gridSize):
                self.canvasButtons[i].draw(self._screen)
                
            if self.pointOne != self.pointTwo != (0,0):
                self.brushStrokeTemp.draw(self._screen)
            
            for i in range (0, self.count):
                self.brushStroke_dict[i].draw(self._screen)    
                
            #if self.pointOne != self.pointTwo and self.pointOne != (0,0) and self.pointTwo != (0,0):
             #   self.distance = math.sqrt(abs(self.pointTwo[1]-self.pointOne[1])**2 + abs(self.pointTwo[0]-self.pointOne[0])**2)
              #  if self.active_tool == Tool.Line:
               #     pygame.draw.line(self._screen, self.color_dict[self.active_color], self.pointOne, self.pointTwo, 5)
                #else:
                 #   pygame.draw.circle(self._screen, self.color_dict[self.active_color],self.pointOne, int(self.distance), 5)
            #-----------------------------------------------------------------------------
            pygame.draw.rect(self._screen, self.color_dict[Color.ColorSelect], pygame.Rect(0, 0, self.width * (2/8)-100, self.height))
            pygame.draw.rect(self._screen, self.color_dict[Color.ToolSelect], pygame.Rect((self.width * (2/8))+self.height, 0, self.width * (2/8)-100, self.height))
            
            pygame.draw.rect(self._screen, self.color_dict[Color.Confirmation], pygame.Rect(20, (self.height/2)-200, self.width-40, 400))
            pygame.draw.rect(self._screen, self.color_dict[Color.Text], pygame.Rect(20, (self.height/2)-200, self.width-40, 400),8)
            
            for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
                button.draw(self._screen)
            
            Text(200, (self.height * (1/2))-30, self.color_dict[Color.Text], 42, 'Cancel', self._screen)
            Text(200, (self.height * (1/2))+30, self.color_dict[Color.Text], 42, 'Stroke', self._screen)
            Text(self.width -200, (self.height * (1/2))-30, self.color_dict[Color.Text], 42, 'Commit', self._screen)
            Text(self.width -200, (self.height * (1/2))+30, self.color_dict[Color.Text], 42, 'Stroke', self._screen)
                                   
            
        pygame.display.update()     # Redraw the display

    def cleanup(self):
        pygame.quit()   # Quit pygame stuff

    def execute(self):
        """
        Main loop method of the program
        """

        if self.init() == False:
            self._running = False   # If failed to init, never enter the loop and exit the program
        
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            
            self.loop()
            self.render()

            pygame.time.delay(30)   # Delay to run at about 60 updates per second
        
        self.cleanup()  # Cleanup and exit pygame

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--width", type=int, default=1600, help="Width for window to be")
    parser.add_argument("--height", type=int, default=900, help="Height for window to be")
    parser.add_argument("--canvas_divisions", type=int, default=8, help="Number divisions for the canvas")
    parser.add_argument("--calibration_dots", type=int, default=4, help="Width and height of calibration dot matrix")
    parser.add_argument("--port", type=str, default="COM3", help="Serial port to open connection to CNC with")

    args = parser.parse_args()

    app = App(args.width, args.height, canvas_divisions=args.canvas_divisions, calibration_dots=args.calibration_dots, port=args.port)    # Initialize the app at a size of 1600 pixels wide and 900 pixels high
    app.execute()   # Start the program
