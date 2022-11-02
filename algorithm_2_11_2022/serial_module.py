import time
import serial
from serial.tools import list_ports

SERIAL_OBJECT = None
ARDUINO_BOOT_TIME_SECONDS = 5


def __keep_port_alive():
    global SERIAL_OBJECT
    global ARDUINO_BOOT_TIME_SECONDS
    # May throw serial.serialutil.SerialException
    # Exceptions are not handled here

    # Available serial ports as string list
    ports_str_list = []
    for port_object in list(list_ports.comports()):
        ports_str_list.append(port_object.device)

    # Check if are there any available ports
    if (len(ports_str_list) == 0):
        raise Exception("No serial port available")

    # Check if current port is in the list of available ports
    if (SERIAL_OBJECT != None):
        if SERIAL_OBJECT.port not in ports_str_list:
            SERIAL_OBJECT = None

    # if serial object is set, be sure it is open
    if (SERIAL_OBJECT != None and not SERIAL_OBJECT.is_open):
        SERIAL_OBJECT.open()
        time.sleep(ARDUINO_BOOT_TIME_SECONDS)

    # Set serial object if not already set. Note that, when set, it is automatically opened
    if (SERIAL_OBJECT == None):
        SERIAL_OBJECT = serial.Serial(
            port=ports_str_list[0],
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=3
        )
        time.sleep(ARDUINO_BOOT_TIME_SECONDS)


def __kill_port():
    global SERIAL_OBJECT
    global ARDUINO_BOOT_TIME_SECONDS

    if (SERIAL_OBJECT != None):
        if (SERIAL_OBJECT.is_open):
            SERIAL_OBJECT.close()
        SERIAL_OBJECT = None
        time.sleep(ARDUINO_BOOT_TIME_SECONDS)


def write_to_port_and_get_response(str_data_to_write="", wait_response_seconds=1, is_empty_response_accepted=False, number_of_retries_on_empty_response = 3, timeout_seconds=30):
    #================================================================================================
    # str_data_to_write:                   Data to write to the serial port as utf-8 decoded string
    # wait_response_time:                  When data is written to the serial port, the function sleeps for the response for this amount of seconds. If the response is not received in this time, the function assumes no response is returned
    # is_empty_response_accepted:          If the response is empty, the function returns None, if this is set to True, the function returns an empty string
    # number_of_retries_on_empty_response: If the response is empty, the function retries to read the response for this amount of times vefore killing and reopening the port
    # timeout_seconds:                     If is_empty_response_accepted is set to False, when an empty response is received, the function will reopen the serial port and try again. This is repeated until the timeout is reached. If the timeout is reached, the function raises an exception. 
    #                                      In addition to this, if there is an exception is raised, the function will reopen the serial port and try again. This is also repeated until the timeout is reached.
    #================================================================================================

    global SERIAL_OBJECT

    retry_counter = 0
    time_start = time.time()
    while time.time() < time_start+timeout_seconds:
        try:
            # ensure port is alive, otherwise thrown an error
            __keep_port_alive()

            # clear buffer
            while SERIAL_OBJECT.in_waiting > 0:
                SERIAL_OBJECT.read()

            # Writes data to the serial port
            SERIAL_OBJECT.write(str_data_to_write.encode("utf-8"))
            time.sleep(wait_response_seconds)

            # read buffer and parse the response
            buffer_str = ""
            while SERIAL_OBJECT.in_waiting > 0:
                buffer_str += SERIAL_OBJECT.read().decode("utf-8")
            buffer_str = buffer_str.replace("\r", "")
            buffer_str = buffer_str.replace("\n", "")

            # check if response is empty, if empty response is not accepted, go back to the beginning of the loop and retry
            if (buffer_str == ""):
                buffer_str = None
                if (not is_empty_response_accepted):
                    retry_counter+= 1
                    if(retry_counter > number_of_retries_on_empty_response):
                        print(f"{time.time()} write_to_port_and_get_response:" + f"Empty response received for the {retry_counter} time, killing the port")
                        __kill_port()
                    print(f"{time.time()} write_to_port_and_get_response:" + "Empty response received, retrying")

                    continue

            # success
            return (buffer_str)
        except Exception as e:
            # if an error occurs, kill port and try again
            # TODO: keep log of errors
            print(f"{time.time()} write_to_port_and_get_response:" + str(e))
            __kill_port()

    __kill_port()
    raise Exception(f"{time.time()} write_to_port_and_get_response:" + "Serial connection timeout")

