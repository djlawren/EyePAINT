"""
G-code Generation
EyePAINT

By Dean Lawrence
"""

import serial
import enum
import time

class Color(enum.Enum):
    Blue = 1
    Green = 2
    Red = 3
    Yellow = 4

class Tool(enum.Enum):
    Line = 1
    Circle = 2

class GcodeGeneration():
    def __init__(self, port, baud):
        
        self.port = port
        self.baud = baud

        self.ser = serial.Serial(self.port, self.baud)

        self.bias_x = 0
        self.bias_y = 0
        self.scale_x = 0
        self.scale_y = 0

        self.clean_x = 0
        self.clean_y = 0

    def initialize(self):
        """
        Initializes the board parameters with a default string and sends it to the board
        """

        init_string = "G90\r\n" + \
                      "G28\r\n"

        self._send(init_string)

    def generate(self, point1, point2, color, tool):
        """
        Given two points, a color and a tool, the method generates the g-code string and sends it to the board
        """

        complete_string = self._set(color)

        if tool == Tool.Line:
            complete_string += self._line(point1, point2)
        elif tool == Tool.Circle:
            complete_string += self._circle(point1, point2)

        complete_string += self._clean()

        self._send(complete_string)
    
    def _line(self, point1, point2):
        """
        Creates and returns the line drawing g-code given two point tuples
        """
        
        start_true_x = point1[0] * self.scale_x + self.bias_x
        start_true_y = point1[1] * self.scale_y + self.bias_y
        end_true_x = point2[0] * self.scale_x + self.bias_x
        end_true_y = point2[1] * self.scale_y + self.bias_y

        return "G01 X{} Y{} Z10\r\n".format(start_true_x, start_true_y) + \
               "G01 X{} Y{} Z0\r\n".format(start_true_x, start_true_y) + \
               "G01 X{} Y{} Z0\r\n".format(end_true_x, end_true_y) + \
               "G01 X{} Y{} Z10\r\n".format(end_true_x, end_true_y)

    def _circle(self, point1, point2):
        return ""

    def _clean(self):
        """
        Creates and returns the cleaning g-code
        """

        return "G01 X{} Y{} Z10\r\n".format(self.clean_x, self.clean_y) + \
               "G01 X{} Y{} Z0\r\n".format(self.clean_x, self.clean_y) + \
               "G01 X{} Y{} Z10\r\n".format(self.clean_x, self.clean_y)

    def _set(self, color):
        """
        Creates and returns the paint set g-code
        """

        if color == Color.Blue:
            pot_x = 0
            pot_y = 0
        elif color == Color.Green:
            pot_x = 0
            pot_y = 0
        elif color == Color.Red:
            pot_x = 0
            pot_y = 0
        elif color == Color.Yellow:
            pot_x = 0
            pot_y = 0

        return "G01 X{} Y{} Z10\r\n".format(pot_x, pot_y) + \
               "G01 X{} Y{} Z0\r\n".format(pot_x, pot_y) + \
               "G01 X{} Y{} Z10\r\n".format(pot_x, pot_y)

    def _send(self, final_string):
        """
        Communicates a g-code string to the board using pyserial
        """

        self.ser.write(final_string)
        time.sleep(1)
