from pymodbus.client import ModbusSerialClient
from typing import Optional, Tuple

from error import Error

def parse_signed_32bit(registers: list[int]) -> Tuple[Optional[int], Optional[Error]]:
    if len(registers) != 2:
        return None, Error(f'Expected two registers, received {len(registers)}')
    
    raw = (registers[0] << 16) | registers[1]
    if raw & (1 << 31):
        raw -= (1 << 32)
    
    return raw, None

# returns a list of values which can be used as the data argument for the move_to_point command
def new_point(position: float, velocity: float, acceleration: float, position_tolerance: float) -> list[int]:
    return [0x0000, int(position * 100), 0x0000, int(position_tolerance * 100), 0x0000, int(velocity*100), int(acceleration*100)]
        
class Controller:
    def __init__(self, port="COM4", ):
        self.client = ModbusSerialClient("COM4", baudrate=9600)
    
    def connect(self) -> Optional[Error]:
        err = None
        try:
            self.client.connect()
            if not self.client.connected:
                err = Error('Failed to connect to controller')
        
        except Exception as e:
            err = Error(str(e)).wrap('caught an exception while connecting to controller')
        
        return err
    
    def disconnect(self) -> Optional[Error]:
        err = None
        try:
            self.client.close()
            if self.client.connected:
                err = Error('Failed to connect to controller')
        
        except Exception as e:
            err = Error(str(e)).wrap('caught an exception while disconnecting from controller')
        
        return err            
    
    def get_current_position(self) -> Tuple[Optional[float], Optional[Error]]:
        try:
            response = self.client.read_holding_registers(address=0x9000, count=0x02, slave=0x01)
            position, err = parse_signed_32bit(response.registers)
            if err is not None:
                return None, err.Wrap("failed to parse position from response")
            
            return position * 0.01, None
        except Exception as e:
            return None, Error(str(e))
        
    def servo_on(self):
        try:
            response = self.client.write_coil(0x0403, slave=0x01, value=True)
            print(response)
        except Exception as e:
            return Error(str(e))

    def home(self) -> Optional[Error]:
        try:
            self.client.write_coil(address=0x040B, slave=0x01, value=True)
            self.client.write_coil(address=0x040B, slave=0x01, value=False)
            # TODO: Should probably wait for homing to be complete by checking for HEND bit to go high
        except Exception as e:
            return Error(e).wrap("caught an exception during home command")
    
    def jog_positive(self) -> Optional[Error]:
        try:
            self.client.write_coil(address=0x0416, slave=0x01, value=True)
        except Exception as e:
            return Error(e).wrap("caught an exception during jog_positive command")

    def jog_negative(self) -> Optional[Error]:
        try:
            self.client.write_coil(address=0x0417, slave=0x01, value=True)
        except Exception as e:
            return Error(e).wrap("caught an exception during jog_negative command")
        
    def move_to_point(self, position: float, velocity: float, acceleration: float, position_tolerance = 0.1) -> Optional[Error]:
        try:
            point = new_point(position, velocity, acceleration, position_tolerance)
            self.client.write_registers(address=0x9900, slave=0x01, values=point)
        except Exception as e:
            return Error(e).wrap("caught an exception during move_to_point command")
    
    def change_velocity(self, velocity: float) -> Optional[Error]:
        try:
            self.client.write_registers(address=0x9904, slave=0x01, values=[0x0000, int(velocity*100)])
        except Exception as e:
            return Error(e).wrap("caught an exception during change_velocity command")

if __name__ == "__main__":
    RCP5 = Controller()
    RCP5.connect()
    RCP5.get_current_position()
    RCP5.servo_on()
    RCP5.home()
    RCP5.move_to_point(120, 10, 1)
    RCP5.move_to_point(10, 20, 1)
    