"""
G-code Generation
EyePAINT

By Dean Lawrence
"""

import serial

class GcodeGenerator():
    def __init__(self):
        pass

    def generate(self):
        pass

class GcodeCommunicator():
    def __init__(self, port, baud):
        
        self.port = port
        self.baud = baud

        self.ser = serial.Serial(self.port, self.baud)

    def send(self, string_list):
        
        for string in string_list:
            
            for byt in string:
                self.ser.write(byt)
            
            self.ser.write('/r')
            self.ser.write('/n')
