import time
import serial
from serial.tools import list_ports

SERIAL_OBJECT = None
ARDUINO_BOOT_TIME_SECONDS = 5


def __keep_port_alive():
    global SERIAL_OBJECT
    global ARDUINO_BOOT_TIME_SECONDS
    #May throw serial.serialutil.SerialException
    #Exceptions are not handled here
    
    #Available serial ports as string list
    ports_str_list = []
    for port_object in list(list_ports.comports()):
        ports_str_list.append(port_object.device)

    #Check if are there any available ports
    if(len(ports_str_list) == 0):
        raise Exception("No serial port available")

    #Check if current port is in the list of available ports
    if(SERIAL_OBJECT != None):
        if SERIAL_OBJECT.port not in ports_str_list:
             SERIAL_OBJECT = None

    #if serial object is set, be sure it is open
    if(SERIAL_OBJECT != None and not SERIAL_OBJECT.is_open):
        SERIAL_OBJECT.open()    
        time.sleep(ARDUINO_BOOT_TIME_SECONDS)
    
    #Set serial object if not already set, when set, it is automatically opened
    if(SERIAL_OBJECT == None):
                SERIAL_OBJECT = serial.Serial(
                    port = ports_str_list[0],
                    baudrate =  9600, 
                    bytesize = 8, 
                    parity = "N", 
                    stopbits = 1, 
                    timeout=3
                )
                time.sleep(ARDUINO_BOOT_TIME_SECONDS)

    
def __kill_port():
    global SERIAL_OBJECT
    global ARDUINO_BOOT_TIME_SECONDS
    if(SERIAL_OBJECT != None):
        if(SERIAL_OBJECT.is_open):
            SERIAL_OBJECT.close()
        SERIAL_OBJECT = None
        time.sleep(ARDUINO_BOOT_TIME_SECONDS)


def write_to_port_and_get_response(str_data_to_write = "", wait_response_seconds=1, is_empty_response_accepted = False, timeout_seconds = 10):
    global SERIAL_OBJECT
    time_start = time.time()
    while time.time()<time_start+timeout_seconds:
        try:
            #ensure port is alive, otherwise thrown an error
            __keep_port_alive()

            #clear buffer
            while SERIAL_OBJECT.in_waiting > 0:
                    SERIAL_OBJECT.read()

            #Writes data to the serial port       
            SERIAL_OBJECT.write(str_data_to_write.encode("utf-8"))        
            time.sleep(wait_response_seconds)

            #read buffer
            buffer_str = ""
            while SERIAL_OBJECT.in_waiting > 0:
                    buffer_str += SERIAL_OBJECT.read().decode("utf-8")
            buffer_str = buffer_str.replace("\r", "")
            buffer_str = buffer_str.replace("\n", "")

            #check if response is empty, if empty response is not accepted, go back to the beginning of the loop and retry
            if(buffer_str == ""):
                    buffer_str = None
                    if( not is_empty_response_accepted):
                        continue

            #success
            return(buffer_str)
        except Exception as e:
            #if an error occurs, kill port and try again
            #TODO: keep log of errors
            print(f"{time.time()} write_to_port_and_get_response:" + str(e)) 
            __kill_port()
    
    __kill_port()
    raise Exception("Serial connection timeout")


while True:
    print("loop start")
    

    rslt = write_to_port_and_get_response(str_data_to_write = "a", wait_response_seconds=0.2, is_empty_response_accepted = False, timeout_seconds = 30)
    print(rslt)
 
   





