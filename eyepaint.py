"""
EyePAINT
By Hannah Imboden and Dean Lawrence
"""

import pygame
import enum

from eyelib import GazeEstimationThread

class ProgramState(enum.Enum):
    Calibration = 1
    Primary = 2
    ColorSelect = 3
    ToolSelect = 4
    Confirmation = 5

pygame.init()

x = 50
y = 50
r = 15
width = 3
vel = 5
screenX = 1500
screenY = 900

# Color Buttons (Top Down) 0Red, 1Purple, 2Blue, 3Green, 4Yellow, 5White
butPressed = [0,0,0,0,0,0]
butUnpressOG = [pygame.image.load('images/RedButUnpress.png'), pygame.image.load('images/PurButUnpress.png'), pygame.image.load('images/BluButUnpress.png'), pygame.image.load('images/GreButUnpress.png'), pygame.image.load('images/YelButUnpress.png'), pygame.image.load('images/WhiButUnpress.png'),]
butPressOG = [pygame.image.load('images/RedButPress.png'), pygame.image.load('images/PurButPress.png'), pygame.image.load('images/BluButPress.png'), pygame.image.load('images/GreButPress.png'), pygame.image.load('images/YelButPress.png'), pygame.image.load('images/WhiButPress.png'),]
butUnpress = []
butPress = []

# Tool Buttons (Top Down) 0fill, 1line, 2circle
toolPressed = [0,0,0]
toolUnpressOG = [pygame.image.load('images/filButUnpress.png'), pygame.image.load('images/linButUnpress.png'), pygame.image.load('images/cirButUnpress.png')]
toolPressOG = [pygame.image.load('images/filButPress.png'), pygame.image.load('images/linButPress.png'), pygame.image.load('images/cirButPress.png')]
toolSelectOG = [pygame.image.load('images/filButSelect.png'), pygame.image.load('images/linButSelect.png'), pygame.image.load('images/cirButSelect.png')]
toolUnpress = []
toolPress = []
toolSelect = []
toolCurrent = 100

# Selected Color
currentColor = [100,100,100]
color = [[204,58,0],[80,51,153],[121,208,242],[73,102,0],[242,216,121],[255,255,255]]


butWidth = 150
butHeight = 100
toolWidth = 80
toolHeight = 50


#Create the screen
screen = pygame.display.set_mode((screenX,screenY))

#Title and Icon
pygame.display.set_caption("EyePAINT")
icon = pygame.image.load('images/london-eye.png')
pygame.display.set_icon(icon)


def colorButtonsScale():
    for b in butUnpressOG:
        image = pygame.transform.scale(b, (butWidth, butHeight))
        butUnpress.append(image)
    for b in butPressOG:
        image = pygame.transform.scale(b, (butWidth, butHeight))
        butPress.append(image)      
    return

def toolButtonsScale():
    for b in toolUnpressOG:
        image = pygame.transform.scale(b, (toolWidth, toolHeight))
        toolUnpress.append(image)
    for b in toolPressOG:
        image = pygame.transform.scale(b, (toolWidth, toolHeight))
        toolPress.append(image)
    for b in toolSelectOG:
        image = pygame.transform.scale(b, (toolWidth, toolHeight))
        toolSelect.append(image)
    return

def colorButtons():
    butX = 75
    butY0 = 25
    yRate = 50
    cnt = 0
    key = pygame.key.get_pressed()
    
    #draw all 6 buttons
    for b in butUnpress:
        screen.blit(b,(butX,(butY0 + cnt*(butHeight + yRate))))
        butPressed[cnt] = 0
        if (x-r)>butX and (x+r)<=(butX+butWidth) and (y-r)>(butY0+(cnt*(yRate+butHeight))) and (y+r)<=(butY0+butHeight+(cnt*(yRate+butHeight))):
            butPressed[cnt] = 1
            screen.blit(butPress[cnt],(butX,(butY0 + cnt*(butHeight + yRate))))
            if keys [pygame.K_SPACE]:
                currentColor[0] = color[cnt][0]
                currentColor[1] = color[cnt][1]
                currentColor[2] = color[cnt][2]  
        cnt = cnt + 1     
            
    return

def toolButtons():
    global toolCurrent
    
    butX = 275
    butY0 = 25
    yRate = 25
    cnt = 0
    key = pygame.key.get_pressed()
    
    #draw all 6 buttons
    for b in toolUnpress:
        toolPressed[cnt] = 0
        if toolCurrent != cnt:
            screen.blit(b,(butX,(butY0 + cnt*(butHeight + yRate))))
            
        if (x-r)>butX and (x+r)<=(butX+butWidth) and (y-r)>(butY0+(cnt*(yRate+butHeight))) and (y+r)<=(butY0+butHeight+(cnt*(yRate+butHeight))):
            toolPressed[cnt] = 1
            screen.blit(toolPress[cnt],(butX,(butY0 + cnt*(butHeight + yRate))))
            if keys [pygame.K_SPACE]:
                 toolCurrent = cnt
                 
        cnt = cnt + 1     
            
    return

def redrawScreen():
    #screen.fill((214, 237, 154))
    screen.fill((255,255,255))
    colorButtons()
    toolButtons()
    pygame.draw.rect(screen,(214,237,154), (400,30,(screenX-500),(screenY-60)))
    pygame.draw.circle(screen,(currentColor[0],currentColor[1],currentColor[2]), (x, y), r, width )
    pygame.draw.circle(screen,(100,100,100), (x,y), 2)
    pygame.display.update()
    return

#initialize
colorButtonsScale()
toolButtonsScale()
#Game Loop
run = True

#gaze_estimation = GazeEstimationThread()

# Initial state stuff
state = ProgramState.Calibration


while run == True:
    pygame.time.delay(20) #pass time
    
    """
    #check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    #move Point with arrow keys
    keys = pygame.key.get_pressed()
    if keys [pygame.K_LEFT] and x > vel + r:
        x -= vel
    if keys[pygame.K_RIGHT] and x < screenX - r - vel:
        x += vel
    if keys[pygame.K_UP] and y > vel + r:
        y -= vel
    if keys[pygame.K_DOWN] and y < screenY - r - vel:
        y += vel
    """

    if state == ProgramState.Calibration:
        pass
    elif state == ProgramState.Primary:
        redrawScreen()
    elif state == ProgramState.ColorSelect:
        pass
    elif state == ProgramState.ToolSelect:
        pass
    elif state == ProgramState.Confirmation:
        pass

class Calibration():
    def __init__(self):
        pass

    def update(self):
        pass

    def render(self):
        pass

class App():
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1500, 900

        self.state = ProgramState.Calibration
        self.gaze_estimation = GazeEstimationThread()
    
    def init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        # Hannah's Stuff
        colorButtonsScale()
        toolButtonsScale()
    
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    
    def loop(self):
        if self.state == ProgramState.Calibration:
            pass
        elif self.state == ProgramState.Primary:
            pass
        elif self.state == ProgramState.ColorSelect:
            pass
        elif self.state == ProgramState.ToolSelect:
            pass
        elif self.state == ProgramState.Confirmation:
            pass
    
    def render(self):
        if self.state == ProgramState.Calibration:
            pass
        elif self.state == ProgramState.Primary:
            redrawScreen()
        elif self.state == ProgramState.ColorSelect:
            pass
        elif self.state == ProgramState.ToolSelect:
            pass
        elif self.state == ProgramState.Confirmation:
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
        
        self.cleanup()

if __name__ == "__main__":
    app = App()
    app.execute()

#pygame.quit()
