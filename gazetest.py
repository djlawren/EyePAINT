"""
Gaze Estimation Testing Software

By Dean Lawrence
"""

import pygame
import enum
import math
import argparse
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import random
from sklearn import linear_model

from eyelib import GazeEstimationThread, GazeState
from eyelib import CalibrationDot, ProgramState

class MockGazeEstimationThread():
    def get(self):
        pos = pygame.mouse.get_pos()

        return GazeState(pos[0], pos[1])
    
    def add_sample(self, pos):
        pass

    def train(self):
        pass
    
    def test_data(self):
        pass

def create_stats_report(mean, min_val, first, median, third, max_val):

    report_text = ""

    report_text += "Mean: " + mean + "\n"
    report_text += "Five number summary:\n"
    report_text += "Min: " + min_val + "\n"
    report_text += "1st: " + first + "\n"
    report_text += "Med: " + median + "\n"
    report_text += "3rd: " + third + "\n"
    report_text += "Max: " + max_val + "\n\n"

    return report_text

def generate_report(experiment_name, time_data, accuracy_data, calibration_x_data, calibration_y_data):
    
    report_text = ""

    # Time data processing
    report_text += "--- Time Data ---\n"
    time_first_quartile, time_median, time_third_quartile = np.percentile(time_data, [25, 50, 75])
    time_min, time_max = min(time_data), max(time_data)
    time_avg = sum(time_data) / len(time_data)

    report_text += "Samples: " + len(time_data) + "\n"
    report_text += create_stats_report(time_avg, time_min, time_first_quartile, time_median, time_third_quartile, time_max)

    # Accuracy data processing
    report_text += "--- Accuracy Data ---\n"
    accuracy_first_quartile, accuracy_median, accuracy_third_quartile = np.percentile(accuracy_data, [25, 50, 75])
    accuracy_min, accuracy_max = min(accuracy_data), max(accuracy_data)
    accuracy_avg = sum(accuracy_data) / len(accuracy_data)

    report_text += "Samples: " + len(accuracy_data) + "\n"
    report_text += create_stats_report(accuracy_avg, accuracy_min, accuracy_first_quartile, accuracy_median, accuracy_third_quartile, accuracy_max)

    # Calibration X data processing
    report_text += "--- Calibration X Data ---\n"
    calibration_x_first_quartile, calibration_x_median, calibration_x_third_quartile = np.percentile(calibration_x_data, [25, 50, 75])
    calibration_x_min, calibration_x_max = min(calibration_x_data), max(calibration_x_data)
    calibration_x_avg = sum(calibration_x_data) / len(calibration_x_data)

    report_text += "Samples: " + len(calibration_x_data) + "\n"
    report_text += create_stats_report(calibration_x_avg, calibration_x_min, calibration_x_first_quartile, calibration_x_median, calibration_x_third_quartile, calibration_x_max)

    # Calibration Y data processing
    report_text += "--- Calibration Y Data ---\n"
    calibration_y_first_quartile, calibration_y_median, calibration_y_third_quartile = np.percentile(calibration_y_data, [25, 50, 75])
    calibration_y_min, calibration_y_max = min(calibration_y_data), max(calibration_y_data)
    calibration_y_avg = sum(calibration_y_data) / len(calibration_y_data)

    report_text += "Samples: " + len(calibration_y_data) + "\n"
    report_text += create_stats_report(calibration_y_avg, calibration_y_min, calibration_y_first_quartile, calibration_y_median, calibration_y_third_quartile, calibration_y_max)

    with open(experiment_name + "_report.txt", "w") as fp:
        fp.write(report_text)


class App():
    def __init__(self, width, height, canvas_divisions=7, calibration_dots=4, trial_name="test", trial_runs=50):
        self._running = True
        self._screen = None
        self.size = self.width, self.height = width, height     # Hardcoded dimensions for the window
        
        self.state = ProgramState.Calibration   # Variable to store which screen the program is currently on
        self.gaze_state = None                  # Variable to store latest location where the user is looking

        self.calibration_dots = calibration_dots
        calibration_width = self.width * (1 / self.calibration_dots)
        calibration_height = self.height * (1 / self.calibration_dots)

        self.canvas_divisions = canvas_divisions
        self.canvas_width = self.width * (1 / self.canvas_divisions)
        self.canvas_height = self.height * (1 / self.canvas_divisions)

        # Lists of buttons that are separated by program state
        self.button_dict = {
            ProgramState.Calibration:   [CalibrationDot((calibration_width / 2) + calibration_width * (i % self.calibration_dots),
                                                        (calibration_height / 2) + calibration_height * (i // self.calibration_dots),
                                                        65) for i in range(calibration_dots * calibration_dots)],
            ProgramState.Primary:       [CalibrationDot((self.canvas_width / 2) + self.canvas_width * (i % self.canvas_divisions),
                                                        (self.canvas_height / 2) + self.canvas_height * (i // self.canvas_divisions),
                                                        65, testing=True) for i in range(canvas_divisions * canvas_divisions)]
        }

        self.trial_name = trial_name
        self.trial_runs = trial_runs

        self.active_calibration_dot = -1
        self.active_testing_dot = -1
        self.current_trial = 0
        self.accuracy_data = []
    
        # Object that runs the gaze estimation in a separate thread
        # Deposits predictions into a queue that can be accessed through get()
        
        """
        self.gaze_estimation = GazeEstimationThread(x_estimator=linear_model.Ridge(alpha=0.9),
                                                    y_estimator=linear_model.Ridge(alpha=0.9),
                                                    face_cascade_path="./classifiers/haarcascade_frontalface_default.xml",
                                                    eye_cascade_path="./classifiers/haarcascade_eye.xml",
                                                    shape_predictor_path="./classifiers/shape_predictor_68_face_landmarks.dat",
                                                    width=self.width,
                                                    height=self.height)
        """

        #self.gcode_generation = GcodeGeneration("COM3", 250000)
        self.gaze_estimation = MockGazeEstimationThread()
    
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
                self.gaze_estimation.test_data()
                self.active_calibration_dot += 1

            if self.active_calibration_dot == self.calibration_dots * self.calibration_dots:
                self.gaze_estimation.train()        # Train the regressors that perform gaze estimation
                
                self.state = ProgramState.Primary   # Switch to the primary screen

        # P R I M A R Y   L O O P
        elif self.state == ProgramState.Primary:
            
            if self.active_testing_dot == -1:
                pygame.time.delay(4000)
                self.active_testing_dot = random.randrange(self.canvas_divisions * self.canvas_divisions)
            
            dot = self.button_dict[self.state][self.active_testing_dot]

            if dot.get_step() == dot.set_steps:
                dot.reset()
            
            dot.decrement()

            if dot.get_step() == 0:
                dot.crad = 0
                
                self.current_trial += 1

                x_diff = abs(dot.get_x() - self.gaze_state.getX() + self.canvas_width / 2) // self.canvas_width
                y_diff = abs(dot.get_y() - self.gaze_state.getY() + self.canvas_height / 2) // self.canvas_height

                self.accuracy_data.append(x_diff + y_diff)

                self.active_calibration_dot = random.randrange(self.canvas_divisions * self.canvas_divisions)
            
            if self.current_trial >= self.trial_runs:
                self._running = False
    
    def render(self):
        self._screen.fill((255,255,255))  # Clear screen

        for button in self.button_dict[self.state]:
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
            
            self.loop()         # Call loop method that updates the logic of the program
            self.render()       # Render method that clears screen and redraws buttons

            pygame.time.delay(30)   # Delay to run at about 60 updates per second
        
        calibration_x_data, calibration_y_data = self.gaze_estimation.get_calibration_samples()
        generate_report(self.experiment_name, self.gaze_estimation.get_time_samples(), self.accuracy_data, calibration_x_data, calibration_y_data)

        self.cleanup()  # Cleanup and exit pygame

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("trial_name", type=str, help="Name to attribute to this trial in the report")
    parser.add_argument("--width", type=int, default=1600, help="Width for window to be")
    parser.add_argument("--height", type=int, default=900, help="Height for window to be")
    parser.add_argument("--test_divisions", type=int, default=8, help="Number divisions for the testing grid")
    parser.add_argument("--trial_runs", type=int, default=50, help="Number of samples to take during trial")
    parser.add_argument("--calibration_dots", type=int, default=4, help="Width and height of calibration dot matrix")

    args = parser.parse_args()

    app = App(args.width, args.height, canvas_divisions=args.test_divisions, calibration_dots=args.calibration_dots, trial_name=args.trial_name, trial_runs=args.trial_runs)    # Initialize the app at a size of 1600 pixels wide and 900 pixels high
    app.execute()   # Start the program
