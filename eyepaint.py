"""
EyePAINT

By Hannah Imboden and Dean Lawrence
"""
# Initialize the app at a size of 1600 pixels wide and 900 pixels high
appX = 1600
appY = 900

import pygame
import enum
from sklearn import linear_model

from eyelib import GazeEstimationThread
from eyelib import GcodeGeneration

# Enum for different screens that exist in the program
class ProgramState(enum.Enum):
    Calibration = 1
    Primary = 2
    ColorSelect = 3
    ToolSelect = 4
    Confirmation = 5
    ControlSelect = 6

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

# Enum for the types of tools
class Tool(enum.Enum):
    Line = 1
    Circle = 2

class Control(enum.Enum):
    Mouse = 1
    Eye = 2
    
    
def Text(cx, cy, color, fontSize, textStr, _screen):
    font = pygame.font.Font('SWSimp.ttf', fontSize)
    text = font.render(textStr, True, color)
    textRect = text.get_rect()
    textRect.center = (cx,cy)
    _screen.blit(text, textRect)    

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



class ToolButton():
    def __init__(self, image_path, steps=90):
        pass

    def contains(self, x, y):
        pass

    def draw(self, screen):
        pass

class CanvasButton():
    def __init__(self, appWidth, appHeight, gridSize, steps=90):
        self.cx = appWidth * (1/2)
        self.cy = appHeight * (1/2)
        #pygame.draw.rect(_screen, (255,255,255), (appWidth-(appHeight * (1/2)), 0, appHeight, appHeight))
        
        #self.active_width = active_width
        #self.active_height = active_height

        #self.increment = increment
        self.crad = 0

        self.step = self.set_steps = steps
    
    def reset(self):
        self.step = self.set_steps
        self.crad = 0

    def decrement(self, ticks=1):
        self.step = max(0, self.step - ticks)

        self.crad += self.increment

    def get_step(self):
        return self.step

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
        Draw the active circle on the pygame canvas
        """
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(appWidth-(appHeight * (1/2)), 0, appHeight, appHeight))
        #pygame.draw.circle(_screen, (255, 0, 0), (self.cx, self.cy), int(self.crad))

class App():
    def __init__(self, width, height, canvas_divisions=4):
        self._running = True
        self._screen = None
        self.size = self.width, self.height = width, height     # Hardcoded dimensions for the window
        
        #self.mouseXY
        
        self.canvas_divisions = canvas_divisions

        #self.state = ProgramState.Calibration       # Program begins in the calibrated state
        self.state = ProgramState.ControlSelect
        #self.state = ProgramState.Primary
        self.gaze_state = None

        self.active_color = Color.Blue  # Store an active color
        self.active_tool = Tool.Line    # Store an active tool
        self.active_control = Control.Mouse

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
            Color.Trim:         (229, 229, 229)
        }

        # Lists of buttons that are separated by program state
        self.button_dict = {
            ProgramState.ControlSelect: [ColorButton(self.width * (1/4), self.height * (1/2), 200, 200, self.color_dict[Color.Control], 200, 200, Control.Mouse, 30),
                                         ColorButton(self.width * (3/4), self.height * (1/2), 200, 200, self.color_dict[Color.Control], 200, 200, Control.Eye, 30)],
            ProgramState.Calibration:   [],
            ProgramState.Primary:       [ColorButton(self.width * (1/8)-5, self.height * (1/2), self.width * (2/8)-10, self.height, self.color_dict[Color.ColorSelect], 200, 200, ProgramState.ColorSelect, 30),
                                         ColorButton(self.width * (7/8)+5, self.height * (1/2), self.width * (2/8)-10, self.height, self.color_dict[Color.ToolSelect], 200, 200, ProgramState.ToolSelect, 30),
                                         CanvasButton(self.width, self.height, 5)],
            
            ProgramState.ColorSelect:   [ColorButton(self.width * (1/4), self.height * (1/4), 100, 100, self.color_dict[Color.Blue], self.width / 2, self.height / 2, Color.Blue, 90),     # Upper left color select button
                                         ColorButton(self.width * (3/4), self.height * (1/4), 100, 100, self.color_dict[Color.Green], self.width / 2, self.height / 2, Color.Green, 90),   # Upper right color select button
                                         ColorButton(self.width * (1/4), self.height * (3/4), 100, 100, self.color_dict[Color.Red], self.width / 2, self.height / 2, Color.Red, 90),      # Lower left color select button
                                         ColorButton(self.width * (3/4), self.height * (3/4), 100, 100, self.color_dict[Color.Yellow], self.width / 2, self.height / 2, Color.Yellow, 90),90], # Lower right color select button
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
        pygame.init()   # Init pygame stuff
        self._screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)  # Create the screen for drawing
        self._running = True    # Set running to true
        pygame.display.set_caption("EyePAINT")  # Set the title of the program to EyePAINT
    
    def on_event(self, event):
        if event.type == pygame.QUIT:   # Kill app in case of a quit
            self._running = False
        
        if self.state == ProgramState.ControlSelect:
            pass
        elif self.state == ProgramState.Calibration:
            
            # Temporary calibration routine where clicks add samples
            if event.type == pygame.MOUSEBUTTONUP:
                self.gaze_estimation.add_sample(pygame.mouse.get_pos()) 
                print("New sample added")
                
        elif self.state == ProgramState.Primary:
            pass    # Do event handling for the primary canvas screen

        elif self.state == ProgramState.ColorSelect:
            pass    # Do event handling for the color select screen

        elif self.state == ProgramState.ToolSelect:
            pass    # Do event handling for the tool select screen

        elif self.state == ProgramState.Confirmation:
            pass    # Do event handling for the confirmation screen
    
    def loop(self):
        gaze_location = self.gaze_estimation.get()  # Get the current gaze estimation position from the queue
        mouseXY = pygame.mouse.get_pos()
        
        if gaze_location != None:   # If there was a location, update the classes known location
            self.gaze_state = gaze_location
        
        # C O N T R O L   S E L E C T   L O O P
        if self.state == ProgramState.ControlSelect:
            for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                button.contains(mouseXY[0], mouseXY[1])
                if button.get_step() == 0:
                    self.active_control = button.get_buttonType()
                    if self.active_control == Control.Mouse:
                        self.state = ProgramState.Primary
                    else:
                        self.state = ProgramState.Calibration
        
        # C A L I B R A T I O N   L O O P
        elif self.state == ProgramState.Calibration:
            
            # If 10 samples of data are added, train the regressors and move onto next state
            if self.gaze_estimation.get_sample_count() > 10:
                self.gaze_estimation.train()
                self.state = ProgramState.Primary

        # P R I M A R Y   L O O P
        elif self.state == ProgramState.Primary:
            #Mouse Control
            if self.active_control == Control.Mouse:
                for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                    button.contains(mouseXY[0], mouseXY[1])
                    if button.get_step() == 0:
                        self.state = button.get_buttonType()
            #Eye Control
            else:
                if self.gaze_state != None: # If there is a gaze state, update the buttons
                    for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                        button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                        if button.get_step() == 0:
                            self.state = button.get_buttonType()
                
        # C O L O R   S E L E C T   L O O P 
        elif self.state == ProgramState.ColorSelect:
            #Mouse Control
            if self.active_control == Control.Mouse:
                for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                    button.contains(mouseXY[0], mouseXY[1])
                    if button.get_step() == 0:
                        self.active_color = button.get_buttonType()
                        self.state == ProgramState.Primary
            #Eye Control
            else:    
                if self.gaze_state != None: # If there is a gaze state, update the buttons
                    for button in self.button_dict[self.state]: # Update all the buttons in the button dictionary
                        button.contains(self.gaze_state.getX(), self.gaze_state.getY())
                        if button.get_step() == 0:
                            self.active_color = button.get_buttonType()
                            self.state == ProgramState.Primary

        # T O O L   S E L E C T   L O O P
        elif self.state == ProgramState.ToolSelect:
            pass    # Do update program stuff for the tool select screen

        elif self.state == ProgramState.Confirmation:
            pass    # Do update program stuff for the confirmation screen
    
    def render(self):
        self._screen.fill((255,255,255))  # Clear screen
        
        # C ON T R O L   S E L E C T   R E N D E R
        if self.state == ProgramState.ControlSelect:
            Text(self.width * (1/4), (self.height * (1/2))+225, self.color_dict[Color.Text], 32, 'Mouse', self._screen)
            Text(self.width * (3/4), (self.height * (1/2))+225, self.color_dict[Color.Text], 32, 'Eye Tracking', self._screen)

        # C A L I B R A T I O N   R E N D E R
        elif self.state == ProgramState.Calibration:
            pass    # Render code for while on the calibration screen

        # P R I M A R Y   R E N D E R
        elif self.state == ProgramState.Primary:
            self._screen.fill(self.color_dict[Color.Trim])
            #if self.gaze_state != None:
            #    pygame.draw.circle(self._screen, (0,0,0), (self.gaze_state.getX(),self.gaze_state.getY()), 10)

        # C O L O R   S E L E C T   R E N D E R
        elif self.state == ProgramState.ColorSelect:
            pass    # Render code for while in the color select screen

        # T O O L   S E L E C T   R E N D E R
        elif self.state == ProgramState.ToolSelect:
            pass    # Render code for while in the tool select screen

        # C O N F I R M A T I O N   R E N D E R
        elif self.state == ProgramState.Confirmation:
            pass    # Render code for while on the line confirmation screen
        
        for button in self.button_dict[self.state]:     # Draw all buttons for a given screen
            button.draw(self._screen)

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

            pygame.time.delay(15)   # Delay to run at about 60 updates per second
        
        self.cleanup()  # Cleanup and exit pygame

if __name__ == "__main__":
    app = App(appX, appY)    # Initialize the app at a size of 1600 pixels wide and 900 pixels high
    app.execute()   # Start the program
