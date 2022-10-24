#Documentation: https://pyserial.readthedocs.io/en/latest/pyserial_api.html
#linux allow read and write on: sudo chmod a+rw /dev/ttyACM3

import time
import serial
from serial.tools import list_ports

#which port should be used, if set to None, first port available is used.
__PORT_NAME = None
__SERIAL_OBJECT = None
__ARDUINO_BOOT_TIME_SECONDS = 3

#region -> helper functions
def __get_available_serial_ports():
        #returns all avilable serial ports as string list
        port_objects = list(list_ports.comports())
        list_str = []

        for port_object in port_objects:
            list_str.append(port_object.device)

        return list_str
def __set_serial_object(port_name):
        return serial.Serial(
                port = port_name,
                baudrate =  9600, 
                bytesize = 8, 
                parity = "N", 
                stopbits = 1, 
                timeout=2
        )
def __open_port(__SERIAL_OBJECT):
        #Opens the serial port
        if(isinstance(__SERIAL_OBJECT, serial.Serial)):
                if(__SERIAL_OBJECT.is_open):
                        print("Port is already open")
                else:
                        __SERIAL_OBJECT.open()
        else:
                print("No __SERIAL_OBJECT to open")
def __write_to_port_and_get_response(str_data_to_write, wait_response_seconds):
        #clear buffer
        while __SERIAL_OBJECT.in_waiting > 0:
                __SERIAL_OBJECT.read()
        #Writes data to the serial port       
        __SERIAL_OBJECT.write(str_data_to_write.encode("utf-8"))
        time.sleep(wait_response_seconds)
        buffer_str = ""
        while __SERIAL_OBJECT.in_waiting > 0:
                buffer_str += __SERIAL_OBJECT.read().decode("utf-8")
        buffer_str = buffer_str.replace("\r", "")
        buffer_str = buffer_str.replace("\n", "")
        if(buffer_str == ""):
                buffer_str = None
        return(buffer_str)

#region -> public functions
def close_port():
        #Closes the serial port
        if(isinstance(__SERIAL_OBJECT, serial.Serial)):
                __SERIAL_OBJECT.close()
        else:
                print("No __SERIAL_OBJECT to close")
def write_to_port_and_get_response(str_data_to_write, wait_response_seconds):
        global __PORT_NAME
        global __SERIAL_OBJECT
        global __ARDUINO_BOOT_TIME_SECONDS
        try:
                if(isinstance(__SERIAL_OBJECT, serial.Serial) and __SERIAL_OBJECT.is_open):  
                        __SERIAL_OBJECT.flushInput()                      
                        return __write_to_port_and_get_response(str_data_to_write, wait_response_seconds)

                elif(isinstance(__SERIAL_OBJECT, serial.Serial) and not __SERIAL_OBJECT.is_open):
                        __open_port(__SERIAL_OBJECT)
                        time.sleep(__ARDUINO_BOOT_TIME_SECONDS)
                        return __write_to_port_and_get_response(str_data_to_write, wait_response_seconds)
                
                else:
                        port_to_use = ""
                        if(__PORT_NAME != None):
                                port_to_use = __PORT_NAME
                        else:
                                available_port = __get_available_serial_ports()
                                if(len(available_port)< 1):
                                        raise Exception("No serial port available")
                                port_to_use = available_port[0]
                        
                        __SERIAL_OBJECT = __set_serial_object(port_to_use)
                        time.sleep(__ARDUINO_BOOT_TIME_SECONDS)
                        return __write_to_port_and_get_response(str_data_to_write, wait_response_seconds)
        except Exception as e:
                __SERIAL_OBJECT = None
                print("execute_and_get_reply() -> Error occured while executing command: " + str(e))
                time.sleep(0.5)

