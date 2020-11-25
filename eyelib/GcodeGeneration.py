"""
G-code Generation
EyePAINT

By Dean Lawrence
"""

import serial
import enum
import time
import math
import pygame

from . import Color, Tool

class GcodeGeneration():
    def __init__(self, port, baud):
        
        self.port = port
        self.baud = baud

        self.ser = serial.Serial(self.port, self.baud)

        self.bias_x = 10        # Start of x-axis of canvas in millimeters from zero position
        self.bias_y = 10        # Start of y-axis of canvas in millimeters from zero position
        self.scale_x = 260      # Scale of canvas from a float between 0-1
        self.scale_y = 260      # Scale of canvas from a float between 0-1

        self.clean_x = 340      # Position on x-axis of cleaning mechanism from zero position
        self.clean_y = 22       # Position on y-axis of cleaning mechanism from zero position

        self.canvas_height = 10 # Height of canvas on z-axis
        self.normal_height = 30 # Height of floating on z-axis
        self.paint_height = 0   # Height of paint pot on z-axis

    def initialize(self):
        """
        Initializes the board parameters with a default string and sends it to the board
        """

        # Measure in mm, Set steps per unit of measurement, absolute positioning, home X and Y axes, home Z axis, move back up to normal height
        init_string = "G21\r\n" + \
                      "M92 X80.00 Y80.00 Z400.00\r\n" + \
                      "G90\r\n" + \
                      "G28 X Y\r\n" + \
                      "G28 Z\r\n" + \
                      "G01 Z{}\r\n".format(self.normal_height)

        self._send(init_string)

    def generate(self, point1, point2, color, tool):
        """
        Given two points, a color and a tool, the method generates the g-code string and sends it to the board
        """

        complete_string = self._set(color)  # Add the color set routine to the current string

        if tool == Tool.Line:   # If the line tool is selected, add the line to current string
            complete_string += self._line(point1, point2)
        elif tool == Tool.Circle:   # If the circle tool is selected, add the circle to current string
            complete_string += self._circle(point1, point2)

        complete_string += self._clean()    # Add the clean routine to current string

        self._send(complete_string)     # Send complete string to the SKR Pro
    
    def _line(self, point1, point2):
        """
        Creates and returns the line drawing g-code given two point tuples
        """
        
        # Calculate true position of given points
        start_true_x = int(point1[0] * self.scale_x + self.bias_x)
        start_true_y = int(point1[1] * self.scale_y + self.bias_y)
        end_true_x = int(point2[0] * self.scale_x + self.bias_x)
        end_true_y = int(point2[1] * self.scale_y + self.bias_y)

        # Move over starting point, move down to starting point, move to end point, pick up from end point
        return "G01 X{} Y{} Z{}\r\n".format(start_true_x, start_true_y, self.normal_height) + \
               "G01 X{} Y{} Z{}\r\n".format(start_true_x, start_true_y, self.canvas_height) + \
               "G01 X{} Y{} Z{}\r\n".format(end_true_x, end_true_y, self.canvas_height) + \
               "G01 X{} Y{} Z{}\r\n".format(end_true_x, end_true_y, self.normal_height)

    def _circle(self, point1, point2):
        
        # Calculate radius
        radius = int(math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) * self.scale_x)        

        center_x        = int(point1[0] * self.scale_x + self.bias_x)
        center_y        = int(point1[1] * self.scale_y + self.bias_y)
        top_point_y     = center_y - radius
        bottom_point_y  = center_y + radius

        # Move over starting point, move down to starting point, draw first half of circle, draw second half of circle, pick up from canvas
        return "G01 X{} Y{} Z{}\r\n".format(center_x, top_point_y, self.normal_height) + \
               "G01 X{} Y{} Z{}\r\n".format(center_x, top_point_y, self.canvas_height) + \
               "G02 X{} Y{} R{}\r\n".format(center_x, bottom_point_y, radius) + \
               "G02 X{} Y{} R{}\r\n".format(center_x, top_point_y, radius) + \
               "G01 X{} Y{} Z{}\r\n".format(center_x, top_point_y, self.normal_height)

    def _clean(self):
        """
        Creates and returns the cleaning g-code
        """
        
        # Move to position over cleaning rag, move down to rag, move right on rag, move left on rag, lift up on rag
        return "G01 X{} Y{} Z{}\r\n".format(self.clean_x - 10, self.clean_y, self.normal_height) + \
               "G01 X{} Y{} Z{}\r\n".format(self.clean_x - 10, self.clean_y, self.canvas_height) + \
               "G01 X{} Y{} Z{}\r\n".format(self.clean_x + 10, self.clean_y, self.canvas_height) + \
               "G01 X{} Y{} Z{}\r\n".format(self.clean_x - 10, self.clean_y, self.canvas_height) + \
               "G01 X{} Y{} Z{}\r\n".format(self.clean_x, self.clean_y, self.normal_height)

    def _set(self, color):
        """
        Creates and returns the paint set g-code
        """

        pot_x = 340     # All of the pots are in line on the x-axis

        if color == Color.Blue:
            pot_y = 198
        elif color == Color.Green:
            pot_y = 154
        elif color == Color.Red:
            pot_y = 110
        elif color == Color.Yellow:
            pot_y = 66

        # Move over paint pot, move down to paint, move up from pot
        return "G01 X{} Y{} Z{}\r\n".format(pot_x, pot_y, self.normal_height) + \
               "G01 X{} Y{} Z{}\r\n".format(pot_x, pot_y, self.paint_height) + \
               "G01 X{} Y{} Z{}\r\n".format(pot_x, pot_y, self.normal_height)

    def _send(self, final_string):
        """
        Communicates a g-code string to the board using pyserial
        """
        print(final_string)
        self.ser.write(final_string.encode())    # Write complete string over serial to board
        #time.sleep(1)
        pygame.time.delay(4000)
