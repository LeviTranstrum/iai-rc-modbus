import serial

ser = serial.Serial("COM5", baudrate=115200, timeout=0.1)
need_newline = False
print("I'm listening:")

while True:
    data = ser.read()
    if data:
        need_newline = True
        print(" ".join(f"{b:02X}" for b in data), end=" ")

        
    if not data:
        if need_newline:
            print()
            need_newline = False
