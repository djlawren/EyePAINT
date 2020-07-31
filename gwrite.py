"""
G-code Transmission Test
EyePAINT

By Dean Lawrence
"""

import serial
import argparse

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--baud", type=int, default=9600, help="Baud rate for serial")
    parser.add_argument("--port", type=str, default="COM1", help="COM port for communcation")

    args = parser.parse_args()

    ser = serial.Serial(port=args.port, baudrate=args.baud)

    print("--- EyePAINT SKR Debug Shell ---\n")

    while True:
        print("Prompt>", end=" ")
        code = input()

        for byt in code:
            ser.write(byt)

        ser.write('/r')
        ser.write('/n')

if __name__ == "__main__":
    main()
    